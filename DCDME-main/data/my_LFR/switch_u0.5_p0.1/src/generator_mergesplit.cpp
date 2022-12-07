#define MIN_CLUSTER_SPLIT_SIZE 2*MIN_CLUSTER_SIZE

class MergeSplitParameters: public SwitchParameters
{
public:
	MergeSplitParameters();
	~MergeSplitParameters() {};
	
	int num_merge;
	int num_split;
	virtual bool set(string &, string &);
	virtual bool arrange();
	virtual void usage();
};

MergeSplitParameters::MergeSplitParameters() : SwitchParameters() 
{
	num_merge = 1;
	num_split = 1;
	command_flags.push_back("-merge");		//15	
	command_flags.push_back("-split");		//16	
}

bool MergeSplitParameters::arrange() 
{
	if (num_merge<0) 
	{
		cerr<<"\n***********************\nERROR:\t invalid number of merge events"<<endl;
		return false;
	}
	if (num_split<0) 
	{
		cerr<<"\n***********************\nERROR:\t invalid number of split events"<<endl;
		return false;
	}
	
	if( !SwitchParameters::arrange() )
	{
		return false;
	}
	cout<<"merge events per step:\t"<< num_merge <<endl;
	cout<<"split events per step:\t"<< num_split <<endl;
	return true;
}

bool MergeSplitParameters::set(string & flag, string & num) 
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
			cerr<<"\n***********************\nERROR: the number of merge events must be an integer"<<endl;
			return false;
		}
		num_merge = cast_int(err);
		return true;
	}
	else if (flag==command_flags[16]) 
	{
		if (fabs(err-int (err))>1e-8) 
		{
			cerr<<"\n***********************\nERROR: the number of split events must be an integer"<<endl;
			return false;
		}
		num_split = cast_int(err);
		return true;
	}	
	return SwitchParameters::set(flag,num);
}

void MergeSplitParameters::usage()
{
	SwitchParameters::usage();
	cout<<"-merge\t\t[number of merge events per time step]"<<endl;
	cout<<"-split\t\t[number of split events per time step]"<<endl;
}

// ------------------------------------------------------------------------------------------------------------

class MergeSplitGenerator: public SwitchGenerator
{
public:
	MergeSplitGenerator( MergeSplitParameters* param );
	~MergeSplitGenerator() {};
	virtual int mutate( int step, int num_nodes, deque<deque<int> > &member_matrix, multimap<int,int> &last_step_dynamic_map, multimap<int,int> &step_dynamic_map );
	
	int num_merge, num_split;
};

class MergeSplitsCluster
{
public:
	int index;
	deque<int> members;
	deque<int> dynamic_indices;
};

MergeSplitGenerator::MergeSplitGenerator(MergeSplitParameters* param) : SwitchGenerator(param) 
{
	num_merge = param->num_merge;
	num_split = param->num_split;
}

int MergeSplitGenerator::mutate( int step, int num_nodes, deque<deque<int> > &member_matrix, multimap<int,int> &last_step_dynamic_map, multimap<int,int> &step_dynamic_map )
{
#ifdef ALWAYS_SWITCH
	apply_switch( num_nodes, member_matrix );
#endif
	printf("Mutating %d communities (num_merge=%d,num_split=%d)...\n", (int)member_matrix.size(), num_merge, num_split );

	vector<MergeSplitsCluster> available;
	vector<MergeSplitsCluster> unavailable;
	multimap<int, int>::iterator lit;
	for (int i = 0; i < member_matrix.size(); i++)
	{
		MergeSplitsCluster mc;
		mc.index = i;
		mc.members = member_matrix[i];
		lit = last_step_dynamic_map.begin(); 
		for (; lit != last_step_dynamic_map.end(); ++lit)
		{
			if( lit->first == i )
			{
				mc.dynamic_indices.push_back( lit->second );
			}
		}
		available.push_back(mc);
	}
	
	// Split events
	deque<int>::iterator it;
	int actual_split = 0;
	for( int event_num = 0; event_num < num_split; event_num++)
	{
		if( available.empty() )
		{
			printf("Warning: no clusters available for a split event\n");
			break;
		}
		int max_size = 0;
		for( int i = 0; i < available.size(); i++ )
		{
			max_size = max( max_size, (int)available[i].members.size() );
		}
		if( max_size < MIN_CLUSTER_SPLIT_SIZE )
		{ 
			printf("Warning: no sufficiently large cluster available for a split event\n");
			break;
		}
		
		// select next
		int available_pos, total_size;
		MergeSplitsCluster split_cluster;
		do
		{
			available_pos = irand(available.size()-1);
			split_cluster = available[available_pos];
			total_size = (int)(split_cluster.members.size());
		}
		while(total_size < MIN_CLUSTER_SPLIT_SIZE);
		// no longer available
		available.erase( available.begin() + available_pos );
		// create an extra cluster
		MergeSplitsCluster created_cluster;
		for( int i = 0; i < total_size/2; i++ )
		{
			int member_pos = irand(split_cluster.members.size()-1);
			int item_index = split_cluster.members[member_pos];
			split_cluster.members.erase( split_cluster.members.begin() + member_pos );
			created_cluster.members.push_back( item_index );
		}
#ifdef DEBUG_MUTATION
		printf("Split: Cluster C%d of size %d to clusters of sizes (%d,%d)\n", split_cluster.index+1, total_size, (int)split_cluster.members.size(),	(int)created_cluster.members.size() );
#endif
		// duplicate any dynamic cluster related to the split step cluster
		it = split_cluster.dynamic_indices.begin();
		for (; it != split_cluster.dynamic_indices.end(); ++it)
		{
			int dynamic_split_index = (int)*it;
			int dynamic_created_index = timeline.copy_record( dynamic_split_index );
			created_cluster.dynamic_indices.push_back( dynamic_created_index );
			// also create an event
			Event event( step, "split" );
#ifdef DEBUG_MUTATION
			printf("Split: Splitting M%d -> (M%d,M%d)\n", dynamic_split_index + 1, dynamic_split_index + 1, dynamic_created_index + 1 );
#endif
			event.add( dynamic_split_index + 1 );
			events.push_back( event );
		}
		// add the new clusters 
		unavailable.push_back( split_cluster );
		unavailable.push_back( created_cluster );
		actual_split++;
	}
	
	// Merge events
	int actual_merge = 0;
	for( int event_num = 0; event_num < num_merge; event_num++)
	{
		if( available.size() < 2 )
		{
			printf("Warning: no clusters available for a merge event\n");
			break;
		}
		// select next
		int available_pos1, available_pos2;
		do
		{
			available_pos1 = irand(available.size()-1);
			available_pos2 = irand(available.size()-1);
		}
		while(available_pos1 == available_pos2);
		MergeSplitsCluster merge_cluster2 = available[available_pos2];
#ifdef DEBUG_MUTATION
		printf("Merge: Clusters (C%d,C%d) of sizes (%d,%d) merged\n", available[available_pos1].index+1, merge_cluster2.index+1, (int)available[available_pos1].members.size(),	(int)merge_cluster2.members.size() );
#endif		
		// create events
		deque<int>::iterator it1 = available[available_pos1].dynamic_indices.begin();
		for (; it1 != available[available_pos1].dynamic_indices.end(); ++it1)
		{
			int dynamic_split_index1 = (int)*it1;
			deque<int>::iterator it2 = merge_cluster2.dynamic_indices.begin();
			for (; it2 != merge_cluster2.dynamic_indices.end(); ++it2)
			{
				int dynamic_split_index2 = (int)*it2;
				Event event( step, "merge" );
				event.add( dynamic_split_index1 + 1 );
				event.add( dynamic_split_index2 + 1 );
				events.push_back( event );
#ifdef DEBUG_MUTATION
				printf("Merge: Merging (M%d,M%d)\n", dynamic_split_index1 + 1, dynamic_split_index2 + 1 );
#endif				
			}
		}
		// update first membership
		for (it = merge_cluster2.members.begin(); it != merge_cluster2.members.end(); ++it)
		{
			int node_index = *it;
			// prevent dupes
			deque<int>::iterator fit = find(available[available_pos1].members.begin(), available[available_pos1].members.end(), node_index);
			if (fit == available[available_pos1].members.end())
			{
				available[available_pos1].members.push_back(node_index);
			}
		}
		// update dynamic list in first
		it = merge_cluster2.dynamic_indices.begin();
		for (; it != merge_cluster2.dynamic_indices.end(); ++it)
		{
			int dynamic_split_index2 = (int)*it;
			available[available_pos1].dynamic_indices.push_back( dynamic_split_index2 );
		}
		// 2nd is no longer available
		available.erase( available.begin() + available_pos2 );
		actual_merge++;
	}
	
	// pool everything
	vector<MergeSplitsCluster>::iterator cit = unavailable.begin();
	for (; cit != unavailable.end(); ++cit)
	{
		available.push_back( *cit );
	}
	
	// rebuild membership matrix with new member lists
	step_dynamic_map.clear();
	member_matrix.clear();
	cit = available.begin();
	for (; cit != available.end(); ++cit)
	{
		int step_cluster_index = member_matrix.size();
		member_matrix.push_back( (*cit).members );
		it = (*cit).dynamic_indices.begin();
		// also update mapping...
		for (; it != (*cit).dynamic_indices.end(); ++it)
		{
			step_dynamic_map.insert( make_pair(step_cluster_index, (int)(*it)) );
		}
	}

	// reorder again, now that we've changed
	for (int i = 0; i< member_matrix.size(); i++)
	{
		sort(member_matrix[i].begin(), member_matrix[i].end());
	}
	
	printf("Successful events: %d split(s), %d merge(s)\n", actual_split, actual_merge );
	return actual_split + actual_merge;
}

