class ExpandContractParameters: public SwitchParameters
{
public:
	ExpandContractParameters();
	~ExpandContractParameters() {};
	
	// expansion/contraction rate
	double rate;
	int num_expansion;
	int num_contraction;
	
	virtual bool set(string &, string &);
	virtual bool arrange();
	virtual void usage();
};

ExpandContractParameters::ExpandContractParameters() : SwitchParameters() 
{
	num_expansion = 1;
	num_contraction = 1;
	rate = 0.1;
	command_flags.push_back("-expand");		//15	
	command_flags.push_back("-contract");	//16	
	command_flags.push_back("-r");			//17
}

bool ExpandContractParameters::arrange() 
{
	if (num_expansion<0) 
	{
		cerr<<"\n***********************\nERROR:\t invalid number of expansion events"<<endl;
		return false;
	}
	if (num_contraction<0) 
	{
		cerr<<"\n***********************\nERROR:\t invalid number of contraction events"<<endl;
		return false;
	}	
	if( rate < 0 ) 
	{
		cerr<<"\n***********************\nERROR:\t invalid expansion/contraction rate"<<endl;
		return false;
	}
	
	if( !SwitchParameters::arrange() )
	{
		return false;
	}
	cout<<"expansion events per step:\t"<< num_expansion <<endl;
	cout<<"contraction events per step:\t"<< num_contraction <<endl;	
	cout << "expansion/contraction rate:\t"<< rate <<endl;
	return true;
}

bool ExpandContractParameters::set(string & flag, string & num) 
{
	// false is something goes wrong
	double err;
	if (!cast_string_to_double(num, err)) 
	{
		cerr<<"\n***********************\nERROR while reading parameters"<<endl;
		return false;
	}
	if (flag==command_flags[15]) 
	{
		if (fabs(err-int (err))>1e-8) 
		{
			cerr<<"\n***********************\nERROR: the number of expansion events must be an integer"<<endl;
			return false;
		}
		num_expansion = cast_int(err);
		return true;
	}
	else if (flag==command_flags[16]) 
	{
		if (fabs(err-int (err))>1e-8) 
		{
			cerr<<"\n***********************\nERROR: the number of contraction events must be an integer"<<endl;
			return false;
		}
		num_contraction = cast_int(err);
		return true;
	}
	else if (flag==command_flags[17]) 
	{
		rate = err;
		return true;
	}
	return SwitchParameters::set(flag,num);
}

void ExpandContractParameters::usage()
{
	SwitchParameters::usage();
	cout<<"-expand\t\t[number of expansion events per time step]"<<endl;
	cout<<"-contract\t\t[number of contraction events per time step]"<<endl;	
	cout<<"-r\t\t[rate of expansion/contraction rate]"<<endl;
}

// ------------------------------------------------------------------------------------------------------------

class ExpandContractGenerator: public SwitchGenerator
{
public:
	ExpandContractGenerator( ExpandContractParameters* param );
	~ExpandContractGenerator() {};
	virtual int mutate( int step, int num_nodes, deque<deque<int> > &member_matrix, multimap<int,int> &last_step_dynamic_map, multimap<int,int> &step_dynamic_map );
	
	int num_expansion, num_contraction;
	double rate;
};

ExpandContractGenerator::ExpandContractGenerator(ExpandContractParameters* param) : SwitchGenerator(param) 
{
	num_expansion = param->num_expansion;
	num_contraction = param->num_contraction;	
	rate = param->rate;
}

/**
 * NB: this implementation assumes that all in the previous step there was a 1-1 mapping between step and dynamic clusters (i.e. no duplicate keys in last_step_dynamic_map).
 */
int ExpandContractGenerator::mutate( int step, int num_nodes, deque<deque<int> > &member_matrix, multimap<int,int> &last_step_dynamic_map, multimap<int,int> &step_dynamic_map )
{
#ifdef ALWAYS_SWITCH
	apply_switch( num_nodes, member_matrix );
#endif	
	printf("Mutating communities (num_expansion=%d,num_contraction=%d,rate=%.2f)...\n", num_expansion, num_contraction, rate );
	
	// create list of dynamic identifiers
	vector<int> dynamic_indices;
	multimap<int, int>::iterator it = last_step_dynamic_map.begin(); 
	for (; it != last_step_dynamic_map.end(); ++it)
	{
		int dynamic_index = it->second;
		dynamic_indices.push_back( dynamic_index );
	}
	
	vector<int> available;
	for (int i = 0; i < member_matrix.size(); i++)
	{
		available.push_back( i );
	}
	
	// Expansion events
	int actual_expand = 0;
	int k = (int)member_matrix.size();
	for( int event_index = 0; event_index < num_expansion; event_index++)
	{
		if( available.empty() )
		{
			printf("Warning: no clusters available for an expansion event\n");
			break;
		}
		// select next
		int available_pos = irand(available.size()-1);
		int expand_cluster_index = available[available_pos];
		int dynamic_index = dynamic_indices[expand_cluster_index];
		// no longer available
		available.erase( available.begin() + available_pos );
		// expand
		int prev_size = (int)member_matrix[expand_cluster_index].size();
		int expand_count = max(1,(int)(prev_size*rate));
		int target_size = min( num_nodes, prev_size + expand_count );
		if( target_size == 0 )
		{
			printf("Warning: cannot expand cluster C%d\n", (expand_cluster_index+1) );
			continue;
		}
		int node_index;
		while( (int)member_matrix[expand_cluster_index].size() < target_size )		
		{
			// any unassigned? use them
			if( !unassigned.empty() )
			{
				node_index = unassigned.front();
				unassigned.pop_front();
			}
			else
			{
				// find somewhere to remove it from...
				int other_cluster_index = irand(k-1);
				if( other_cluster_index == expand_cluster_index || member_matrix[other_cluster_index].size() <= MIN_CLUSTER_SIZE )
				{
					continue;
				}
				int pos = irand(member_matrix[other_cluster_index].size()-1);
				node_index = member_matrix[other_cluster_index][pos];
				member_matrix[other_cluster_index].erase( member_matrix[other_cluster_index].begin() + pos );
			}
			// add it to the expanding cluster
			member_matrix[expand_cluster_index].push_back( node_index );
		}
#ifdef DEBUG_MUTATION
		printf("Expand: cluster C%d expanded from %d to %d\n", expand_cluster_index+1, prev_size, target_size );
#endif		
		Event event( step, "expand" );
		event.add( dynamic_index + 1 );
		events.push_back( event );
		actual_expand++;
	}
	
	// Contraction events
	int actual_contract = 0;
	for( int event_index = 0; event_index < num_contraction; event_index++)
	{
		if( available.empty() )
		{
			printf("Warning: no clusters available for a contraction event\n");
			break;
		}
		// select next
		int available_pos = irand(available.size()-1);
		int contract_cluster_index = available[available_pos];
		int dynamic_index = dynamic_indices[contract_cluster_index];
		// no longer available
		available.erase( available.begin() + available_pos );
		// expand
		int prev_size = (int)member_matrix[contract_cluster_index].size();
		if( prev_size ==  MIN_CLUSTER_SIZE)
		{
			printf("Warning: cannot reduced size of clusters C%d below %d\n", contract_cluster_index+1,MIN_CLUSTER_SIZE);
			break;
		}
		int contract_count = max(1,(int)(prev_size*rate));
		int target_size = max( MIN_CLUSTER_SIZE, prev_size - contract_count );
		while( (int)member_matrix[contract_cluster_index].size() > target_size )		
		{		
			int node_pos = irand((int)member_matrix[contract_cluster_index].size()-1);
			int nodex_index = member_matrix[contract_cluster_index][node_pos];
			unassigned.push_back(nodex_index);
			member_matrix[contract_cluster_index].erase( member_matrix[contract_cluster_index].begin() + node_pos );
		}		
		Event event( step, "contract" );
		event.add( dynamic_index + 1 );
		events.push_back( event );		
#ifdef DEBUG_MUTATION		
		printf("Contract: cluster C%d contracted from %d to %d\n", contract_cluster_index+1, prev_size, target_size );
#endif		
		actual_contract++;
	}
	printf("%d expansion event(s), %d contraction event(s), %d node(s) left unassigned\n", actual_expand, actual_contract, (int)unassigned.size() );

	// simple step->dynamic mapping (i.e. just copy last)
	step_dynamic_map.clear();
	step_dynamic_map.insert(last_step_dynamic_map.begin(), last_step_dynamic_map.end());
	
	// reorder again, now that we've changed
	for (int i=0; i<member_matrix.size(); i++)
	{
		sort(member_matrix[i].begin(), member_matrix[i].end());
	}
	return actual_expand + actual_contract;
}

