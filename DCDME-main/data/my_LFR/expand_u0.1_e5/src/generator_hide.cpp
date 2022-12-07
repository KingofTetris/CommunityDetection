class HiddenParameters: public SwitchParameters
{
public:
	HiddenParameters();
	~HiddenParameters() {};
	
	double frac_hide;
	virtual bool set(string &, string &);
	virtual bool arrange();
	virtual void usage();
};

HiddenParameters::HiddenParameters() : SwitchParameters() 
{
	frac_hide = 0.1;
	command_flags.push_back("-hide");		//15	
}

bool HiddenParameters::arrange() 
{
	if (frac_hide<0) 
	{
		cerr<<"\n***********************\nERROR:\t invalid number of hide events"<<endl;
		return false;
	}
	
	if( !SwitchParameters::arrange() )
	{
		return false;
	}
	cout<<"fraction of communities to hide per step:\t"<< frac_hide <<endl;
	return true;
}

bool HiddenParameters::set(string & flag, string & num) 
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
		frac_hide = err;
		return true;
	}	
	return SwitchParameters::set(flag,num);
}

void HiddenParameters::usage()
{
	SwitchParameters::usage();
	cout<<"-hide\t\t[fraction of communities to hide per time step]"<<endl;
}

// ------------------------------------------------------------------------------------------------------------

class HiddenGenerator: public SwitchGenerator
{
public:
	HiddenGenerator( HiddenParameters* param );
	~HiddenGenerator() {};
	virtual int mutate( int step, int num_nodes, deque<deque<int> > &member_matrix, multimap<int,int> &last_step_dynamic_map, multimap<int,int> &step_dynamic_map );
	
protected:
	deque<deque<int> > sub_member_matrix;
	vector<int> sub_dynamic_indices;
	double frac_hide;
};

HiddenGenerator::HiddenGenerator(HiddenParameters* param) : SwitchGenerator(param), frac_hide(param->frac_hide) {}

/**
 * NB: this implementation assumes that all in the previous step there was a 1-1 mapping between step and dynamic clusters (i.e. no duplicate keys in last_step_dynamic_map).
 */
int HiddenGenerator::mutate( int step, int num_nodes, deque<deque<int> > &member_matrix, multimap<int,int> &last_step_dynamic_map, multimap<int,int> &step_dynamic_map )
{
#ifdef ALWAYS_SWITCH
	apply_switch( num_nodes, member_matrix );
#endif
	int num_hide = max(1, (int)(frac_hide * member_matrix.size()) );
	printf("Mutating communities (frac_hide=%.2f => num_hide=%d)...\n", frac_hide, num_hide );
	
	// create list of dynamic identifiers
	vector<int> dynamic_indices;
	multimap<int, int>::iterator it = last_step_dynamic_map.begin(); 
	for (; it != last_step_dynamic_map.end(); ++it)
	{
		int dynamic_index = it->second;
		dynamic_indices.push_back( dynamic_index );
	}
	
	// Unmask previous
	printf("Re-adding %d hidden cluster(s).\n", (int)sub_member_matrix.size() );
	for (int i = 0; i < sub_member_matrix.size(); i++) 
	{
		member_matrix.push_back( sub_member_matrix[i] );
		dynamic_indices.push_back( sub_dynamic_indices[i] );
	}
	sub_member_matrix.clear();
	sub_dynamic_indices.clear();

	// Submarine events
	for( int event_index = 0; event_index < num_hide; event_index++)
	{
		// choose next
		if( member_matrix.empty() )
		{
			break;
		}
		int sub_cluster_index = irand(member_matrix.size()-1);
		int dynamic_index = dynamic_indices[sub_cluster_index];
		// store for next step
		sub_member_matrix.push_back( member_matrix[sub_cluster_index] );
		sub_dynamic_indices.push_back( dynamic_index );
		// remove from this step clustering
		member_matrix.erase( member_matrix.begin() + sub_cluster_index );
		// remove corresponding dynamic index
		dynamic_indices.erase( dynamic_indices.begin() + sub_cluster_index );		
#ifdef DEBUG_MUTATION
		printf("Hide: masking cluster C%d (M%d). %d clusters remaining.\n", sub_cluster_index+1, dynamic_index+1, (int)member_matrix.size() );
#endif
		Event event( step, "hide" );
		event.add( dynamic_index + 1 );
		events.push_back( event );
	}
	printf("Removed %d hidden cluster(s).\n", (int)sub_member_matrix.size() );
	
	// Create the mapping
	for(int step_cluster_index = 0; step_cluster_index < member_matrix.size(); step_cluster_index++)
	{
		step_dynamic_map.insert( make_pair(step_cluster_index, dynamic_indices[step_cluster_index]) );
	}
	
	// reorder again, now that we've changed
	for (int i=0; i<member_matrix.size(); i++)
	{
		sort(member_matrix[i].begin(), member_matrix[i].end());
	}
	return num_hide;
}

