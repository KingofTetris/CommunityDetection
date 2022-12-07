class BirthDeathParameters: public SwitchParameters
{
public:
	BirthDeathParameters();
	~BirthDeathParameters() {};
	
	int num_birth;
	int num_death;
	virtual bool set(string &, string &);
	virtual bool arrange();
	virtual void usage();
};

BirthDeathParameters::BirthDeathParameters() : SwitchParameters() 
{
	num_birth = 1;
	num_death = 1;
	command_flags.push_back("-birth");		//15	
	command_flags.push_back("-death");		//16	
}

bool BirthDeathParameters::arrange() 
{
	if (num_birth<0) 
	{
		cerr<<"\n***********************\nERROR:\t invalid number of birth events"<<endl;
		return false;
	}
	if (num_death<0) 
	{
		cerr<<"\n***********************\nERROR:\t invalid number of death events"<<endl;
		return false;
	}
	
	if( !SwitchParameters::arrange() )
	{
		return false;
	}
	cout<<"birth events per step:\t"<< num_birth <<endl;
	cout<<"death events per step:\t"<< num_death <<endl;
	return true;
}

bool BirthDeathParameters::set(string & flag, string & num) 
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
			cerr<<"\n***********************\nERROR: the number of birth events must be an integer"<<endl;
			return false;
		}
		num_birth = cast_int(err);
		return true;
	}
	else if (flag==command_flags[16]) 
	{
		if (fabs(err-int (err))>1e-8) 
		{
			cerr<<"\n***********************\nERROR: the number of death events must be an integer"<<endl;
			return false;
		}
		num_death = cast_int(err);
		return true;
	}	
	return SwitchParameters::set(flag,num);
}

void BirthDeathParameters::usage()
{
	SwitchParameters::usage();
	cout<<"-birth\t\t[number of birth events per time step]"<<endl;
	cout<<"-death\t\t[number of death events per time step]"<<endl;
}

// ------------------------------------------------------------------------------------------------------------

class BirthDeathGenerator: public SwitchGenerator
{
public:
	BirthDeathGenerator( BirthDeathParameters* param );
	~BirthDeathGenerator() {};
	virtual int mutate( int step, int num_nodes, deque<deque<int> > &member_matrix, multimap<int,int> &last_step_dynamic_map, multimap<int,int> &step_dynamic_map );
	
	int num_birth, num_death;
};

BirthDeathGenerator::BirthDeathGenerator(BirthDeathParameters* param) : SwitchGenerator(param) 
{
	num_birth = param->num_birth;
	num_death = param->num_death;
}

/**
 * NB: this implementation assumes that all in the previous step there was a 1-1 mapping between step and dynamic clusters (i.e. no duplicate keys in last_step_dynamic_map).
 */
int BirthDeathGenerator::mutate( int step, int num_nodes, deque<deque<int> > &member_matrix, multimap<int,int> &last_step_dynamic_map, multimap<int,int> &step_dynamic_map )
{
#ifdef ALWAYS_SWITCH
	apply_switch( num_nodes, member_matrix );
#endif
	printf("Mutating communities (num_birth=%d,num_death=%d)...\n", num_birth, num_death );

	// create list of dynamic identifiers
	vector<int> dynamic_indices;
	multimap<int, int>::iterator it = last_step_dynamic_map.begin(); 
	for (; it != last_step_dynamic_map.end(); ++it)
	{
		int dynamic_index = it->second;
		dynamic_indices.push_back( dynamic_index );
	}
	
	// Death events
	int actual_death = 0;
	for( int event_index = 0; event_index < num_death; event_index++)
	{
		// choose the cluster
		if( member_matrix.empty() )
		{
			break;
		}
		int death_cluster_index = irand(member_matrix.size()-1);
		int dynamic_index = dynamic_indices[death_cluster_index];
		// add to unassigned
		deque<int>::const_iterator cit;
		for( cit = member_matrix[death_cluster_index].begin() ; cit != member_matrix[death_cluster_index].end(); cit++ )
		{
			unassigned.push_back(*cit);
		}
		// remove from membership matrix
		member_matrix.erase( member_matrix.begin() + death_cluster_index );
#ifdef DEBUG_MUTATION
		printf("Death: removed cluster C%d (M%d). %d clusters remaining.\n", death_cluster_index+1, dynamic_index + 1, (int)member_matrix.size() );
#endif	
		// remove corresponding dynamic index
		dynamic_indices.erase( dynamic_indices.begin() + death_cluster_index );	
		Event event( step, "death" );
		event.add( dynamic_index+1 );
		events.push_back( event );
		actual_death++;
	}
	
	// Add surviving to mapping
	for(int step_cluster_index = 0; step_cluster_index < member_matrix.size(); step_cluster_index++)
	{
		step_dynamic_map.insert( make_pair(step_cluster_index, dynamic_indices[step_cluster_index]) );
	}
	
	// Birth events
	int median_size = median_cluster_size(member_matrix);
	printf("Median community size is %d\n", median_size);
	for( int event_index = 0; event_index < num_birth; event_index++)
	{
		deque <int> first;
		int target_size = max(median_size,MIN_CLUSTER_SIZE);
		int k = (int)member_matrix.size();
		while( first.size() < target_size )
		{
			int node_index;
			// should we take an unassigned?
			if( first.size() %2 == 0 && unassigned.size() > 0 )
			{
				int pos = irand(unassigned.size()-1);
				node_index = unassigned[pos];
				unassigned.erase( unassigned.begin() + pos );
			}
			else
			{
				// find somewhere to remove it from...
				int other_cluster_index = irand(k-1);
				if( member_matrix[other_cluster_index].size() <= MIN_CLUSTER_SIZE )
				{
					continue;
				}
				int pos = irand(member_matrix[other_cluster_index].size()-1);
				node_index = member_matrix[other_cluster_index][pos];
				member_matrix[other_cluster_index].erase( member_matrix[other_cluster_index].begin() + pos );
			}
			// add it to the new cluster
			first.push_back( node_index );
		}
		// add to membership matrix
		int step_cluster_index = k;
		member_matrix.push_back(first);
		// add new dynamic cluster and make mapping, but don't add here
		int dynamic_index = timeline.create_record();
		timeline.add( step, dynamic_index, step_cluster_index );		
		step_dynamic_map.insert( make_pair(step_cluster_index, dynamic_index) );
#ifdef DEBUG_MUTATION
		printf("Birth: added cluster of size %d (M%d). %d clusters now present.\n", (int)first.size(), dynamic_index + 1, (int)member_matrix.size() );
#endif
		Event event( step, "birth" );
		event.add( dynamic_index + 1 );
		events.push_back( event );
	}
	printf("%d birth event(s), %d death event(s), %d node(s) left unassigned\n", num_birth, actual_death, (int)unassigned.size() );

	// reorder again, now that we've changed
	for (int i=0; i<member_matrix.size(); i++)
	{
		sort(member_matrix[i].begin(), member_matrix[i].end());
	}
	return num_birth + actual_death;
}

