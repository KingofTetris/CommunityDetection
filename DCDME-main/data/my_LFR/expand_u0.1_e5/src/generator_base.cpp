#include "generator_base.h"

// --------------------------------------------------------------------------
// Clase: BaseGenerator
// --------------------------------------------------------------------------

BaseGenerator::BaseGenerator( Parameters* param )
{
	this->param = param;
	this->do_write_events = true;
}

/**
 * Main graph generation method
 */
int BaseGenerator::generate( int steps )
{
	return benchmark(steps, param->weighted, param->excess, param->defect, param->num_nodes, param->average_k, param->max_degree, param->tau, param->tau2, param->mixing_parameter, param->mixing_parameter2, param->beta, param->overlapping_nodes, param->overlap_membership, param->nmin, param->nmax, param->fixed_range);
}

/**
 * Main original graph generation method
 */
int BaseGenerator::benchmark(int steps, bool weighted, bool excess, bool defect, int num_nodes, double  average_k, int  max_degree, double  tau, double  tau2,
              double  mixing_parameter, double  mixing_parameter2, double  beta, int  overlapping_nodes, int  overlap_membership, int  nmin, int  nmax, bool  fixed_range) 
{
	double dmin = solve_dmin(max_degree, average_k, -tau);

	if (dmin==-1)
		return -1;

	int min_degree = int(dmin);

	double media1 = integer_average(max_degree, min_degree, tau);
	double media2 = integer_average(max_degree, min_degree+1, tau);

	if (fabs(media1-average_k)>fabs(media2-average_k))
		min_degree++;

	// range for the community sizes
	if (!fixed_range) 
	{
		nmax = max_degree;
		nmin = max(int(min_degree), 3);
		cout << "Community size range automatically set equal to ["<<nmin<<" , "<<nmax<<"]"<<endl;
	}
	
	
	deque <int> degree_seq ;		//  degree sequence of the nodes
	deque <double> cumulative;
	powerlaw(max_degree, min_degree, tau, cumulative);

	for (int i=0; i<num_nodes; i++) 
	{
		int nn=lower_bound(cumulative.begin(), cumulative.end(), ran4())-cumulative.begin()+min_degree;
		degree_seq.push_back(nn);
	}

	sort(degree_seq.begin(), degree_seq.end());

	if (deque_int_sum(degree_seq) % 2!=0)
	{
		degree_seq[max_element(degree_seq.begin(), degree_seq.end()) - degree_seq.begin()]--;
	}
	
	// Produce internal_degree and membership
	deque<deque<int> >  member_matrix;
	deque<int> num_seq;
	deque<int> internal_degree_seq;
	
	if (internal_degree_and_membership(mixing_parameter, overlapping_nodes, overlap_membership, num_nodes, member_matrix, excess, defect, degree_seq, num_seq, internal_degree_seq, fixed_range, nmin, nmax, tau2)==-1)
	{
		cerr << "Failed to generate internal degree and membership." << endl;
		return -1;
	}

	cout << "Generating individual time steps...\n" << endl;
	timeline.clear();
	multimap<int,int> step_dynamic_map, last_step_dynamic_map;
	for( int step = 1; step <= steps; step++ )
	{
		printf("*** Time step %d/%d...\n", step, steps);
		if( step == 1 )
		{
			for( int step_cluster_index = 0; step_cluster_index < member_matrix.size(); step_cluster_index++ )
			{
				// create dynamic cluster
				int dynamic_index = timeline.create_record();
				timeline.add( step, dynamic_index, step_cluster_index );
				step_dynamic_map.insert( make_pair(step_cluster_index, dynamic_index) );
#ifdef DEBUG_DYNAMIC
				printf("Birth: creating C%d (M%d)\n", dynamic_index + 1, step_cluster_index+1 );
#endif
#ifdef LOG_INITIAL_EVENTS
				// create event
				Event event( step, "birth" );
				event.add( dynamic_index + 1 );
				events.push_back( event );				
#endif
			}
		}
		else
		{
			// copy last
			last_step_dynamic_map.clear();
			multimap<int, int>::iterator it; 
			for (it = step_dynamic_map.begin(); it != step_dynamic_map.end(); ++it)
			{
				int step_cluster_index = it->first;
				int dynamic_index = it->second;
				last_step_dynamic_map.insert( make_pair(step_cluster_index, dynamic_index) );
#ifdef DEBUG_DYNAMIC
				printf("C%d [M%d]: ", step_cluster_index+1, dynamic_index+1 );
				print_int_deque( member_matrix[step_cluster_index] );
#endif
			}
			step_dynamic_map.clear();

			// apply generation step
		 	mutate( step, num_nodes, member_matrix, last_step_dynamic_map, step_dynamic_map );
			int step_k = (int)member_matrix.size();
			if( step_k == 1 )
			{
				cerr << "Failed generation process. Only a single community remaining." << endl;
				return -1;
			}
			printf("Assigned %d/%d nodes to a community\n", assigned_count(member_matrix), num_nodes );
						
			// update history
			for (it = step_dynamic_map.begin(); it != step_dynamic_map.end(); ++it)
			{
				int step_cluster_index = it->first;
				int dynamic_index = it->second;			
				// printf("Updating history step=%d dyn=%d\n",step_cluster_index,dynamic_index );
				timeline.add( step, dynamic_index, step_cluster_index );
#ifdef DEBUG_DYNAMIC
				// printf("T%d: Updating C%d->M%d\n", step, dynamic_index+1, step_cluster_index+1 );
				printf("C%d [M%d]: ", step_cluster_index+1, dynamic_index+1 );
				print_int_deque( member_matrix[step_cluster_index] );
#endif
			}
		}

		deque<set<int> > E;					// E is the adjacency matrix written in form of list of edges
		deque<deque<int> > member_list;	// row i contains the memberships of node i
		deque<deque<int> > link_list;		// row i contains degree of the node i respect to member_list[i][j]; there is one more number that is the external degree
		cout << "Building subgraphs for " << member_matrix.size() << " communities... " << endl;
		if (build_subgraphs(E, member_matrix, member_list, link_list, internal_degree_seq, degree_seq, excess, defect)==-1)
		{
			return -1;
		}
		
		cout << "Connecting communities... "<<endl;
		connect_all_the_parts(E, member_list, link_list);
		if (erase_links(E, member_list, excess, defect, mixing_parameter)==-1)
		{
		 	return -1;
		}
		 
		deque<map <int, double > > neigh_weigh;
		cout << "Inserting weights..."<<endl;
		insert_weights(E, member_list, beta, mixing_parameter2, neigh_weigh);
		 
		cout << "Recording network..."<<endl;
		print_network(step, weighted, E, member_list, member_matrix, num_seq, neigh_weigh, beta, mixing_parameter2, mixing_parameter);
	}
	
	cout << "Recording community history and events..." << endl;
	print_history( steps );
	return 0;
}

/**
 * bisection method to find the inferior limit, in order to have the expected average degree
 */
double BaseGenerator::solve_dmin(const double& dmax, const double &dmed, const double &gamma) 
{
	double dmin_l=1;
	double dmin_r=dmax;
	double average_k1=average_degree(dmin_r, dmin_l, gamma);
	double average_k2=dmin_r;
	if ((average_k1-dmed>0) || (average_k2-dmed<0)) 
	{
		cerr<<"\n***********************\nERROR: the average degree is out of range:";
		if (average_k1-dmed>0) 
		{
			cerr<<"\nyou should increase the average degree (bigger than "<<average_k1<<")"<<endl;
			cerr<<"(or decrease the maximum degree...)"<<endl;
		}
		if (average_k2-dmed<0) 
		{
			cerr<<"\nyou should decrease the average degree (smaller than "<<average_k2<<")"<<endl;
			cerr<<"(or increase the maximum degree...)"<<endl;
		}
		return -1;
	}
	while (fabs(average_k1-dmed)>1e-7) 
	{
		double temp=average_degree(dmax, ((dmin_r+dmin_l)/2.), gamma);
		if ((temp-dmed)*(average_k2-dmed)>0) 
		{
			average_k2=temp;
			dmin_r=((dmin_r+dmin_l)/2.);
		}
		else 
		{
			average_k1=temp;
			dmin_l=((dmin_r+dmin_l)/2.);
		}
	}
	return dmin_l;
}


int BaseGenerator::internal_degree_and_membership (double mixing_parameter, int overlapping_nodes, int max_mem_num, int num_nodes, deque<deque<int> >  & member_matrix,
	bool excess, bool defect,  deque<int> & degree_seq, deque<int> &num_seq, deque<int> &internal_degree_seq, bool fixed_range, int nmin, int nmax, double tau2) 
{
	if (num_nodes < overlapping_nodes) 
	{
		cerr<<"\n***********************\nERROR: there are more overlapping nodes than nodes in the whole network! Please, decrease the former ones or increase the latter ones"<<endl;
		return -1;
	}

	member_matrix.clear();
	internal_degree_seq.clear();
	deque<double> cumulative;

	// it assigns the internal degree to each node -------------------------------------------------------------------------
	int max_degree_actual=0;		// maximum internal degree
	for (int i = 0; i< degree_seq.size(); i++) 
	{
		double interno=(1-mixing_parameter)*degree_seq[i];
		int int_interno=int(interno);

		if (ran4()<(interno-int_interno))
			int_interno++;
		if (excess) 
		{
			while ( ( double(int_interno)/degree_seq[i] < (1-mixing_parameter) )  &&   (int_interno<degree_seq[i])   )
				int_interno++;
		}

		if (defect) 
		{
			while ( ( double(int_interno)/degree_seq[i] > (1-mixing_parameter) )  &&   (int_interno>0)   )
				int_interno--;
		}

		internal_degree_seq.push_back(int_interno);

		if (int_interno>max_degree_actual)
			max_degree_actual=int_interno;
	}


	// Assigns the community size sequence 
	powerlaw(nmax, nmin, tau2, cumulative);
	if (num_seq.empty()) 
	{
		int _num_=0;
		if (!fixed_range && (max_degree_actual+1)>nmin) 
		{
			_num_=max_degree_actual+1;			// this helps the assignment of the memberships (it assures that at least one module is big enough to host each node)
			num_seq.push_back(max_degree_actual+1);
		}

		while (true) 
		{
			int nn=lower_bound(cumulative.begin(), cumulative.end(), ran4())-cumulative.begin()+nmin;
			if (nn+_num_<=num_nodes + overlapping_nodes * (max_mem_num-1) ) 
			{
				num_seq.push_back(nn);
				_num_+=nn;
			}
			else
				break;
		}
		num_seq[min_element(num_seq.begin(), num_seq.end()) - num_seq.begin()]+=num_nodes + overlapping_nodes * (max_mem_num-1) - _num_;
	}


	int ncom = num_seq.size();
	deque<int> member_numbers;
	for (int i=0; i<overlapping_nodes; i++)
	{
		member_numbers.push_back(max_mem_num);
	}

	for (int i=overlapping_nodes; i<degree_seq.size(); i++)
	{
		member_numbers.push_back(1);
	}

	if (build_bipartite_network(member_matrix, member_numbers, num_seq)==-1) 
	{
		cerr << "It seems that the overlapping nodes need more communities that those I provided. Please increase the number of communities or decrease the number of overlapping nodes"<<endl;
		return -1;
	}

	deque<int> available;

	for (int i=0; i<num_nodes; i++)
		available.push_back(0);

	for (int i=0; i<member_matrix.size(); i++) 
	{
		for (int j=0; j<member_matrix[i].size(); j++)
			available[member_matrix[i][j]]+=member_matrix[i].size()-1;
	}

	//cout<<"available"<<endl;
	//prints(available);


	deque<int> available_nodes;

	for (int i=0; i<num_nodes; i++)
		available_nodes.push_back(i);


	deque<int> map_nodes;				// in the position i there is the new name of the node i

	for (int i=0; i<num_nodes; i++)
		map_nodes.push_back(0);


	for (int i=degree_seq.size()-1; i>=0; i--) 
	{
		int & degree_here=internal_degree_seq[i];
		int try_this = irand(available_nodes.size()-1);
		int kr=0;

		while (internal_degree_seq[i] > available[available_nodes[try_this]]) 
		{
			kr++;
			try_this = irand(available_nodes.size()-1);
			if (kr==3*num_nodes) 
			{
				if (change_community_size(num_seq)==-1) 
				{
					cerr<<"\n***********************\nERROR: this program needs more than one community to work fine"<<endl;
					return -1;

				}
				cout<<"it took too long to decide the memberships; I will try to change the community sizes"<<endl;
				cout<<"new community sizes"<<endl;
				for (int i=0; i<num_seq.size(); i++)
					cout<<num_seq[i]<<" ";
				cout<<endl<<endl;
				return (internal_degree_and_membership(mixing_parameter, overlapping_nodes, max_mem_num, num_nodes, member_matrix, excess, defect, degree_seq, num_seq, internal_degree_seq, fixed_range, nmin, nmax, tau2));
			}
		}
		map_nodes[available_nodes[try_this]]=i;
		available_nodes[try_this]=available_nodes[available_nodes.size()-1];
		available_nodes.pop_back();
	}


	for (int i=0; i<member_matrix.size(); i++) 
	{
		for (int j=0; j<member_matrix[i].size(); j++)
		{
			member_matrix[i][j]=map_nodes[member_matrix[i][j]];
		}
	}
	for (int i=0; i<member_matrix.size(); i++)
	{
		sort(member_matrix[i].begin(), member_matrix[i].end());
	}
	return 0;
}


/**
 this function changes the community sizes merging the smallest communities
 */
int BaseGenerator::change_community_size(deque<int> &seq) 
{
	if (seq.size()<=2)
		return -1;

	int min1=0;
	int min2=0;

	for (int i=0; i<seq.size(); i++)
		if (seq[i]<=seq[min1])
			min1=i;

	if (min1==0)
		min2=1;

	for (int i=0; i<seq.size(); i++)
		if (seq[i]<=seq[min2] && seq[i]>seq[min1])
			min2=i;

	seq[min1]+=seq[min2];
	int c=seq[0];
	seq[0]=seq[min2];
	seq[min2]=c;
	seq.pop_front();
	return 0;
}


/**
  this function builds a bipartite network with num_seq and member_numbers which are the degree sequences. In member matrix links of the communities are stored
  this means member_matrix has num_seq.size() rows and each row has num_seq[i] elements
*/
int BaseGenerator::build_bipartite_network(deque<deque<int> >& member_matrix, const deque<int> & member_numbers, const deque<int> &num_seq) 
{
	deque<set<int> > en_in;			// this is the Ein of the subgraph
	deque<set<int> > en_out;		// this is the Eout of the subgraph

	{
		set<int> first;
		for (int i=0; i<member_numbers.size(); i++) 
		{
			en_in.push_back(first);
		}
	}

	{
		set<int> first;
		for (int i=0; i<num_seq.size(); i++) 
		{
			en_out.push_back(first);
		}
	}


	multimap <int, int> degree_node_out;
	deque<pair<int, int> > degree_node_in;

	for (int i=0; i<num_seq.size(); i++)
		degree_node_out.insert(make_pair(num_seq[i], i));

	for (int i=0; i<member_numbers.size(); i++)
		degree_node_in.push_back(make_pair(member_numbers[i], i));

	sort(degree_node_in.begin(), degree_node_in.end());


	deque<pair<int, int> >::iterator itlast = degree_node_in.end();
	while (itlast != degree_node_in.begin()) 
	{
		itlast--;
		multimap <int, int>::iterator itit= degree_node_out.end();
		deque <multimap<int, int>::iterator> erasenda;

		for (int i=0; i<itlast->first; i++) 
		{
			if (itit!=degree_node_out.begin()) 
			{
				itit--;
				en_in[itlast->second].insert(itit->second);
				en_out[itit->second].insert(itlast->second);
				erasenda.push_back(itit);
			}
			else
				return -1;
		}

		for (int i=0; i<erasenda.size(); i++) 
		{
			if (erasenda[i]->first>1)
				degree_node_out.insert(make_pair(erasenda[i]->first - 1, erasenda[i]->second));
			degree_node_out.erase(erasenda[i]);
		}
	}

	// this is to randomize the subgraph 
	for (int node_a=0; node_a<num_seq.size(); node_a++) 
	{
		for (int krm=0; krm<en_out[node_a].size(); krm++) 
		{
			int random_mate = irand(member_numbers.size()-1);
			if (en_out[node_a].find(random_mate)==en_out[node_a].end()) 
			{
				deque <int> external_nodes;
				for (set<int>::iterator it_est=en_out[node_a].begin(); it_est!=en_out[node_a].end(); it_est++)
					external_nodes.push_back(*it_est);

				int	old_node=external_nodes[irand(external_nodes.size()-1)];
				deque <int> not_common;

				for (set<int>::iterator it_est=en_in[random_mate].begin(); it_est!=en_in[random_mate].end(); it_est++)
					if (en_in[old_node].find(*it_est)==en_in[old_node].end())
						not_common.push_back(*it_est);

				if (not_common.empty())
					break;

				int node_h=not_common[irand(not_common.size()-1)];
				en_out[node_a].insert(random_mate);
				en_out[node_a].erase(old_node);

				en_in[old_node].insert(node_h);
				en_in[old_node].erase(node_a);

				en_in[random_mate].insert(node_a);
				en_in[random_mate].erase(node_h);

				en_out[node_h].erase(random_mate);
				en_out[node_h].insert(old_node);
			}
		}
	}

	member_matrix.clear();
	deque <int> first;
	for (int i=0; i<en_out.size(); i++) 
	{
		member_matrix.push_back(first);
		for (set<int>::iterator its=en_out[i].begin(); its!=en_out[i].end(); its++)
			member_matrix[i].push_back(*its);
	}
	return 0;
}


int BaseGenerator::build_subgraphs(deque<set<int> > & E, const deque<deque<int> > & member_matrix, deque<deque<int> > & member_list,
                    deque<deque<int> > & link_list, const deque<int> & internal_degree_seq, const deque<int> & degree_seq, const bool excess, const bool defect) 
{
	E.clear();
	member_list.clear();
	link_list.clear();

	int num_nodes=degree_seq.size();
	{
		deque<int> first;
		for (int i=0; i<num_nodes; i++)
			member_list.push_back(first);
	}

	for (int i=0; i<member_matrix.size(); i++)
	{
		for (int j=0; j<member_matrix[i].size(); j++)
		{
			member_list[member_matrix[i][j]].push_back(i);
		}
	}

	for (int i=0; i<member_list.size(); i++) 
	{
		deque<int> liin;
		for (int j=0; j<member_list[i].size(); j++) 
		{
			compute_internal_degree_per_node(internal_degree_seq[i], member_list[i].size(), liin);
			liin.push_back(degree_seq[i] - internal_degree_seq[i]);
		}
		link_list.push_back(liin);
	}


	// this is done to check if the sum of the internal degree is an even number. if not, the program will change it in such a way to assure that.
	for (int i=0; i<member_matrix.size(); i++) 
	{
		int internal_cluster=0;
		for (int j=0; j<member_matrix[i].size(); j++) 
		{
			int right_index= lower_bound(member_list[member_matrix[i][j]].begin(), member_list[member_matrix[i][j]].end(), i) - member_list[member_matrix[i][j]].begin();
			internal_cluster+=link_list[member_matrix[i][j]][right_index];
		}

		if (internal_cluster % 2 != 0) 
		{
			bool default_flag=false;
			if (excess)
				default_flag=true;
			else if (defect)
				default_flag=false;
			else if (ran4()>0.5)
				default_flag=true;
			if (default_flag) 
			{
				// if this does not work in a reasonable time the degree sequence will be changed
				for (int j=0; j<member_matrix[i].size(); j++) 
				{
					int random_mate=member_matrix[i][irand(member_matrix[i].size()-1)];
					int right_index= lower_bound(member_list[random_mate].begin(), member_list[random_mate].end(), i) - member_list[random_mate].begin();
					if ((link_list[random_mate][right_index]<member_matrix[i].size()-1) && (link_list[random_mate][link_list[random_mate].size()-1] > 0 )) {

						link_list[random_mate][right_index]++;
						link_list[random_mate][link_list[random_mate].size()-1]--;
						break;
					}
				}
			}
			else 
			{
				for (int j=0; j<member_matrix[i].size(); j++) 
				{
					int random_mate=member_matrix[i][irand(member_matrix[i].size()-1)];
					int right_index= lower_bound(member_list[random_mate].begin(), member_list[random_mate].end(), i) - member_list[random_mate].begin();
					if (link_list[random_mate][right_index] > 0 ) 
					{
						link_list[random_mate][right_index]--;
						link_list[random_mate][link_list[random_mate].size()-1]++;
						break;
					}
				}
			}
		}
	}


	// This is done to check if the sum of the internal degree is an even number. if not, the program will change it in such a way to assure that.
	{
		set<int> first;
		for (int i=0; i<num_nodes; i++)
			E.push_back(first);
	}

	for (int i=0; i<member_matrix.size(); i++) 
	{
		deque<int> internal_degree_i;
		for (int j=0; j<member_matrix[i].size(); j++) 
		{
			int right_index= lower_bound(member_list[member_matrix[i][j]].begin(), member_list[member_matrix[i][j]].end(), i) - member_list[member_matrix[i][j]].begin();
			internal_degree_i.push_back(link_list[member_matrix[i][j]][right_index]);
		}
		if (build_subgraph(E, member_matrix[i], internal_degree_i)==-1)
			return -1;
	}
	return 0;
}

/**
  This function is to build a network with the labels stored in nodes and the degree seq in degrees (correspondence is based on the vectorial index)
  the only complication is that you don't want the npdes to have neighbors they already have
*/
int BaseGenerator::build_subgraph(deque<set<int> > & E, const deque<int> & nodes, const deque<int> & degrees) 
{
	if( degrees.size() < MIN_CLUSTER_SIZE ) 
	{
		cerr << "Warning: Some communities should have less than " << MIN_CLUSTER_SIZE << " nodes." << endl;
		return -1;
	}

	// labels will be placed in the end
	deque<set<int> > en; // this is the E of the subgraph
	{
		set<int> first;
		for (int i=0; i<nodes.size(); i++)
			en.push_back(first);
	}

	multimap <int, int> degree_node;
	for (int i=0; i<degrees.size(); i++)
		degree_node.insert(degree_node.end(), make_pair(degrees[i], i));

	int var=0;
	while (degree_node.size() > 0) 
	{
		multimap<int, int>::iterator itlast= degree_node.end();
		itlast--;

		multimap <int, int>::iterator itit= itlast;
		deque <multimap<int, int>::iterator> erasenda;

		int inserted=0;
		for (int i=0; i<itlast->first; i++) 
		{
			if (itit!=degree_node.begin()) 
			{
				itit--;
				en[itlast->second].insert(itit->second);
				en[itit->second].insert(itlast->second);
				inserted++;
				erasenda.push_back(itit);
			}
			else
				break;
		}
		for (int i=0; i<erasenda.size(); i++) 
		{
			if (erasenda[i]->first>1)
				degree_node.insert(make_pair(erasenda[i]->first - 1, erasenda[i]->second));
			degree_node.erase(erasenda[i]);
		}
		var+= itlast->first - inserted;
		degree_node.erase(itlast);
	}

	// this is to randomize the subgraph 
	for (int node_a=0; node_a<degrees.size(); node_a++) 
	{
		for (int krm=0; krm<en[node_a].size(); krm++) 
		{
			int random_mate=irand(degrees.size()-1);
			while (random_mate==node_a)
				random_mate=irand(degrees.size()-1);
			if (en[node_a].insert(random_mate).second) 
			{
				deque <int> out_nodes;
				for (set<int>::iterator it_est=en[node_a].begin(); it_est!=en[node_a].end(); it_est++) if ((*it_est)!=random_mate)
						out_nodes.push_back(*it_est);

				int old_node=out_nodes[irand(out_nodes.size()-1)];
				en[node_a].erase(old_node);
				en[random_mate].insert(node_a);
				en[old_node].erase(node_a);
				deque <int> not_common;

				for (set<int>::iterator it_est=en[random_mate].begin(); it_est!=en[random_mate].end(); it_est++)
					if ((old_node!=(*it_est)) && (en[old_node].find(*it_est)==en[old_node].end()))
						not_common.push_back(*it_est);

				int node_h=not_common[irand(not_common.size()-1)];

				en[random_mate].erase(node_h);
				en[node_h].erase(random_mate);
				en[node_h].insert(old_node);
				en[old_node].insert(node_h);
			}
		}
	}
	
	// now I try to insert the new links into the already done network. If some multiple links come out, I try to rewire them
	deque < pair<int, int> > multiple_edge;
	for (int i=0; i<en.size(); i++) 
	{
		for (set<int>::iterator its=en[i].begin(); its!=en[i].end(); its++) if (i<*its ) 
		{
				bool already = !(E[nodes[i]].insert(nodes[*its]).second);		// true is the insertion didn't take place
				if (already)
					multiple_edge.push_back(make_pair(nodes[i], nodes[*its]));
				else
					E[nodes[*its]].insert(nodes[i]);
		}
	}

	for (int i=0; i<multiple_edge.size(); i++) 
	{
		int &a = multiple_edge[i].first;
		int &b = multiple_edge[i].second;
		
		// now, I'll try to rewire this multiple link among the nodes stored in nodes.
		int stopper_ml=0;
		while (true) 
		{
			stopper_ml++;
			int random_mate=nodes[irand(degrees.size()-1)];
			while (random_mate==a || random_mate==b)
			{
				random_mate=nodes[irand(degrees.size()-1)];
			}
			if (E[a].find(random_mate)==E[a].end()) 
			{
				deque <int> not_common;
				for (set<int>::iterator it_est=E[random_mate].begin(); it_est!=E[random_mate].end(); it_est++)
					if ((b!=(*it_est)) && (E[b].find(*it_est)==E[b].end()) && (binary_search(nodes.begin(), nodes.end(), *it_est)))
						not_common.push_back(*it_est);

				if (not_common.size()>0) 
				{
					int node_h=not_common[irand(not_common.size()-1)];
					E[random_mate].insert(a);
					E[random_mate].erase(node_h);
					E[node_h].erase(random_mate);
					E[node_h].insert(b);
					E[b].insert(node_h);
					E[a].insert(random_mate);
					break;
				}
			}

			if (stopper_ml==2*E.size()) 
			{
				cout<<"sorry, I need to change the degree distribution a little bit (one less link)"<<endl;
				break;
			}
		}
	}
	return 0;
}

int BaseGenerator::connect_all_the_parts(deque<set<int> > & E, const deque<deque<int> > & member_list, const deque<deque<int> > & link_list) 
{
	//printf("Listing degrees...\n");
	deque<int> degrees;
	for (int i=0; i < link_list.size(); i++)
	{
		// printf("%d/%d => %d\n", i, (int)link_list.size(), (int)link_list[i].size() );
		if( link_list[i].size() == 0 )
		{
			degrees.push_back(0);
		}
		else
		{
			degrees.push_back(link_list[i][link_list[i].size()-1]);
		}
	}

	deque<set<int> > en; // this is the en of the subgraph
	{
		set<int> first;
		for (int i=0; i<member_list.size(); i++)
		{
			en.push_back(first);
		}
	}

	multimap <int, int> degree_node;
	for (int i=0; i<degrees.size(); i++)
	{
		degree_node.insert(degree_node.end(), make_pair(degrees[i], i));
	}

	int var = 0;
	while (degree_node.size() > 0) 
	{
		multimap<int, int>::iterator itlast= degree_node.end();
		itlast--;
		multimap <int, int>::iterator itit= itlast;
		deque <multimap<int, int>::iterator> erasenda;
		int inserted=0;
		for (int i=0; i<itlast->first; i++) 
		{
			if (itit!=degree_node.begin()) 
			{
				itit--;
				bool found_unassigned1 = find(unassigned.begin(), unassigned.end(), itlast->second) != unassigned.end();
				bool found_unassigned2 = find(unassigned.begin(), unassigned.end(), itit->second) != unassigned.end();
				if( !(found_unassigned1 || found_unassigned2) )
				{
					en[itlast->second].insert(itit->second);
					en[itit->second].insert(itlast->second);
					inserted++;
					erasenda.push_back(itit);
				}
				else
				{
					// Ignore bad pair
				}
			}
			else
				break;
		}
		for (int i=0; i<erasenda.size(); i++) 
		{
			if (erasenda[i]->first>1)
			{
				degree_node.insert(make_pair(erasenda[i]->first - 1, erasenda[i]->second));
			}
			degree_node.erase(erasenda[i]);
		}
		var+= itlast->first - inserted;
		degree_node.erase(itlast);
	}

	// this is to randomize the subgraph 
	printf("Randomizing subgraph...\n");
	for (int node_a=0; node_a<degrees.size(); node_a++) 
	{
		for (int krm=0; krm<en[node_a].size(); krm++) 
		{
			int random_mate=irand(degrees.size()-1);
			bool found_unassigned = find(unassigned.begin(), unassigned.end(), random_mate) != unassigned.end();
			while( random_mate == node_a || found_unassigned )
			{
				random_mate=irand(degrees.size()-1);
				found_unassigned = find(unassigned.begin(), unassigned.end(), random_mate) != unassigned.end();
			}
				
			if (en[node_a].insert(random_mate).second) 
			{
				deque <int> out_nodes;
				for (set<int>::iterator it_est=en[node_a].begin(); it_est!=en[node_a].end(); it_est++) 
				{
					if ((*it_est)!=random_mate)
					{
						if( find(unassigned.begin(), unassigned.end(), (*it_est)) == unassigned.end() )
						{
							out_nodes.push_back(*it_est);
						}
					}
				}

				int old_node=out_nodes[irand(out_nodes.size()-1)];
				en[node_a].erase(old_node);
				en[random_mate].insert(node_a);
				en[old_node].erase(node_a);

				deque <int> not_common;
				for (set<int>::iterator it_est=en[random_mate].begin(); it_est!=en[random_mate].end(); it_est++)
				{
					if ((old_node!=(*it_est)) && (en[old_node].find(*it_est)==en[old_node].end()))
					{
						not_common.push_back(*it_est);
					}
				}

				int node_h=not_common[irand(not_common.size()-1)];
				en[random_mate].erase(node_h);
				en[node_h].erase(random_mate);
				en[node_h].insert(old_node);
				en[old_node].insert(node_h);
			}
		}
	}
	

	
	// now there is a rewiring process to avoid "mate nodes" (nodes with al least one membership in common) to link each other
	int var_mate=0;

	for (int i=0; i<degrees.size(); i++) 
	{
		for (set<int>::iterator itss= en[i].begin(); itss!=en[i].end(); itss++) 
		{
			if (they_are_mate(i, *itss, member_list)) 
			{
				var_mate++;
			}
		}
	}	

	int stopper_mate=0;
	int mate_trooper=10;

	while (var_mate>0) 
	{
		int best_var_mate=var_mate;
		// rewiring
		for (int a=0; a<degrees.size(); a++) 
			for (set<int>::iterator its= en[a].begin(); its!=en[a].end(); its++) 
				if (they_are_mate(a, *its, member_list)) 
				{
					int b=*its;
					int stopper_m=0;
					while (true) 
					{
						stopper_m++;
						int random_mate=irand(degrees.size()-1);
						bool found_unassigned = find(unassigned.begin(), unassigned.end(), random_mate) != unassigned.end();
						while (random_mate==a || random_mate==b || found_unassigned)
						{
							random_mate=irand(degrees.size()-1);
							found_unassigned = find(unassigned.begin(), unassigned.end(), random_mate) != unassigned.end();
						}
						if (!(they_are_mate(a, random_mate, member_list)) && (en[a].find(random_mate)==en[a].end())) 
						{
							deque <int> not_common;

							for (set<int>::iterator it_est=en[random_mate].begin(); it_est!=en[random_mate].end(); it_est++)
							{
								if ((b!=(*it_est)) && (en[b].find(*it_est)==en[b].end()))
								{
									not_common.push_back(*it_est);
								}
							}

							if (not_common.size()>0) 
							{
								int node_h=not_common[irand(not_common.size()-1)];
								en[random_mate].erase(node_h);
								en[random_mate].insert(a);
								en[node_h].erase(random_mate);
								en[node_h].insert(b);
								en[b].erase(a);
								en[b].insert(node_h);
								en[a].insert(random_mate);
								en[a].erase(b);
								if (!they_are_mate(b, node_h, member_list))
									var_mate-=2;
								if (they_are_mate(random_mate, node_h, member_list))
									var_mate-=2;								
								break;
							}
						}
						if (stopper_m==en[a].size())
							break;
					}
					break;		// this break is done because if you erased some link you have to stop this loop (en[i] changed)
				}

		if (var_mate==best_var_mate) 
		{
			stopper_mate++;
			if (stopper_mate==mate_trooper)
				break;
		}
		else
			stopper_mate=0;
	}

	for (int i=0; i<en.size(); i++) 
	{
		for (set<int>::iterator its=en[i].begin(); its!=en[i].end(); its++) if (i<*its) 
		{
			E[i].insert(*its);
			E[*its].insert(i);
		}
	}
	return 0;
}


int BaseGenerator::erase_links(deque<set<int> > & E, const deque<deque<int> > & member_list, const bool excess, const bool defect, const double mixing_parameter) 
{
	int num_nodes= member_list.size();
	int eras_add_times=0;
	if (excess) 
	{
		for (int i=0; i<num_nodes; i++) 
		{
			while ( (E[i].size()>1) &&  double(internal_kin(E, member_list, i))/E[i].size() < 1 - mixing_parameter) 
			{
				cout<<"degree sequence changed to respect the option -sup ... "<<++eras_add_times<<endl;
				deque<int> deqar;
				for (set<int>::iterator it_est=E[i].begin(); it_est!=E[i].end(); it_est++)
					if (!they_are_mate(i, *it_est, member_list))
						deqar.push_back(*it_est);
				if (deqar.size()==E[i].size()) 
				{	
					// this shouldn't happen...
					cerr<<"sorry, something went wrong: there is a node which does not respect the constraints. (option -sup)"<<endl;
					return -1;
				}
				int random_mate=deqar[irand(deqar.size()-1)];
				E[i].erase(random_mate);
				E[random_mate].erase(i);
			}
		}
	}

	if (defect) 
	{
		for (int i=0; i<num_nodes; i++)
			while ( (E[i].size()<E.size()) &&  double(internal_kin(E, member_list, i))/E[i].size() > 1 - mixing_parameter) 
			{
				cout<<"degree sequence changed to respect the option -inf ... "<<++eras_add_times<<endl;
				int stopper_here=num_nodes;
				int stopper_=0;
				int random_mate=irand(num_nodes-1);
				while ( ( (they_are_mate(i, random_mate, member_list)) || E[i].find(random_mate)!=E[i].end())  && (stopper_<stopper_here) ) 
				{
					random_mate=irand(num_nodes-1);
					stopper_++;
				}
				if (stopper_==stopper_here) 
				{	
					// this shouldn't happen...
					cerr<<"sorry, something went wrong: there is a node which does not respect the constraints. (option -inf)"<<endl;
					return -1;
				}
				E[i].insert(random_mate);
				E[random_mate].insert(i);
			}
	}
	return 0;
}

int BaseGenerator::insert_weights(deque<set<int> > & en, const deque<deque<int> > & member_list, const double beta, const double mu, deque<map <int, double > > & neigh_weigh) 
{
	double tstrength=0;

	for (int i=0; i<en.size(); i++)
		tstrength+=pow(en[i].size(), beta);
	double strs[en.size()]; // strength of the nodes

	// build a matrix like this: deque < map <int, double > > each row corresponds to link - weights
	for (int i=0; i<en.size(); i++) 
	{
		map<int, double> new_map;
		neigh_weigh.push_back(new_map);
		for (set<int>::iterator its=en[i].begin(); its!=en[i].end(); its++)
		{
			neigh_weigh[i].insert(make_pair(*its, 0.));
		}
		strs[i]=pow(double(en[i].size()), beta);
	}

	deque<double> s_in_out_id_row(3);
	s_in_out_id_row[0]=0;
	s_in_out_id_row[1]=0;
	s_in_out_id_row[2]=0;
	deque<deque<double> > wished;	// 3 numbers for each node: internal, idle and extra strength. the sum of the three is strs[i]. wished is the theoretical, factual the factual one.
	deque<deque<double> > factual;

	for (int i=0; i<en.size(); i++) 
	{
		wished.push_back(s_in_out_id_row);
		factual.push_back(s_in_out_id_row);
	}

	double tot_var=0;
	for (int i=0; i<en.size(); i++) 
	{
		wished[i][0]=(1. -mu)*strs[i];
		wished[i][1]=mu*strs[i];
		factual[i][2]=strs[i];
		tot_var+= wished[i][0] * wished[i][0] + wished[i][1] * wished[i][1] + strs[i] * strs[i];
	}

	deque<int> internal_kin_top;
	for (int i=0; i<en.size(); i++)
		internal_kin_top.push_back(internal_kin(en, member_list, i));

	double precision = 1e-9;
	double precision2 = 1e-2;
	double not_better_than = pow(tstrength, 2) * precision;

	int step=0;
	while (true) 
	{
		time_t t0=time(NULL);
		double pre_var=tot_var;

		for (int i=0; i<en.size(); i++)
		{
			propagate(neigh_weigh, member_list, wished, factual, i, tot_var, strs, internal_kin_top);
		}

		//check_weights(neigh_weigh, member_list, wished, factual, tot_var, strs);
		double relative_improvement=double(pre_var - tot_var)/pre_var;
		//cout<<"tot_var "<<tot_var<<"\trelative improvement: "<<relative_improvement<<endl;
		if (tot_var<not_better_than)
			break;
		if (relative_improvement < precision2)
			break;

		time_t t1= time(NULL);
		int deltat= t1 - t0;
		step++;
	}
	//check_weights(neigh_weigh, member_list, wished, factual, tot_var, strs);
	return 0;
}


int BaseGenerator::propagate(deque<map <int, double > > & neigh_weigh, const deque<deque<int> > & member_list, deque<deque<double> > & wished, deque<deque<double> > & factual, int i, double & tot_var, double *strs, const deque<int> & internal_kin_top) 
{
	{		// in this case I rewire the idle strength
		double change=factual[i][2]/neigh_weigh[i].size();
		double oldpartvar=0;
		for (map<int, double>::iterator itm=neigh_weigh[i].begin(); itm!=neigh_weigh[i].end(); itm++) if (itm->second + change > 0)
				for (int bw=0; bw<3; bw++)
					oldpartvar+= (factual[itm->first][bw] - wished[itm->first][bw]) * (factual[itm->first][bw] - wished[itm->first][bw]);

		for (int bw=0; bw<3; bw++)
			oldpartvar+= (factual[i][bw] - wished[i][bw]) * (factual[i][bw] - wished[i][bw]);

		double newpartvar=0;
		for (map<int, double>::iterator itm=neigh_weigh[i].begin(); itm!=neigh_weigh[i].end(); itm++) if (itm->second + change > 0) 
		{
				if (they_are_mate(i, itm->first, member_list)) 
				{
					factual[itm->first][0]+=change;
					factual[itm->first][2]-=change;

					factual[i][0]+=change;
					factual[i][2]-=change;
				}
				else 
				{
					factual[itm->first][1]+=change;
					factual[itm->first][2]-=change;

					factual[i][1]+=change;
					factual[i][2]-=change;
				}

				for (int bw=0; bw<3; bw++)
					newpartvar+= (factual[itm->first][bw] - wished[itm->first][bw]) * (factual[itm->first][bw] - wished[itm->first][bw]);

				itm->second+= change;
				neigh_weigh[itm->first][i]+=change;
			}

		for (int bw=0; bw<3; bw++)
			newpartvar+= (factual[i][bw] - wished[i][bw]) * (factual[i][bw] - wished[i][bw]);

		tot_var+= newpartvar - oldpartvar;

	}

	int internal_neigh=internal_kin_top[i];
	if (internal_neigh!=0) 
	{		// in this case I rewire the difference strength
		double changenn=(factual[i][0] - wished[i][0]);
		double oldpartvar=0;
		for (map<int, double>::iterator itm=neigh_weigh[i].begin(); itm!=neigh_weigh[i].end(); itm++) 
		{
			if (they_are_mate(i, itm->first, member_list)) 
			{
				double change = changenn/internal_neigh;
				if (itm->second - change > 0)
					for (int bw=0; bw<3; bw++)
						oldpartvar+= (factual[itm->first][bw] - wished[itm->first][bw]) * (factual[itm->first][bw] - wished[itm->first][bw]);
			}
			else 
			{
				double change = changenn/(neigh_weigh[i].size() - internal_neigh);
				if (itm->second + change > 0)
					for (int bw=0; bw<3; bw++)
						oldpartvar+= (factual[itm->first][bw] - wished[itm->first][bw]) * (factual[itm->first][bw] - wished[itm->first][bw]);
			}
		}

		for (int bw=0; bw<3; bw++)
			oldpartvar+= (factual[i][bw] - wished[i][bw]) * (factual[i][bw] - wished[i][bw]);

		double newpartvar=0;
		for (map<int, double>::iterator itm=neigh_weigh[i].begin(); itm!=neigh_weigh[i].end(); itm++) 
		{
			if (they_are_mate(i, itm->first, member_list)) 
			{
				double change = changenn/internal_neigh;
				if (itm->second - change > 0) 
				{
					factual[itm->first][0]-=change;
					factual[itm->first][2]+=change;

					factual[i][0]-=change;
					factual[i][2]+=change;

					for (int bw=0; bw<3; bw++)
						newpartvar+= (factual[itm->first][bw] - wished[itm->first][bw]) * (factual[itm->first][bw] - wished[itm->first][bw]);

					itm->second-= change;
					neigh_weigh[itm->first][i]-=change;
				}
			}
			else 
			{
				double change = changenn/(neigh_weigh[i].size() - internal_neigh);
				if (itm->second + change > 0) 
				{

					factual[itm->first][1]+=change;
					factual[itm->first][2]-=change;

					factual[i][1]+=change;
					factual[i][2]-=change;

					for (int bw=0; bw<3; bw++)
						newpartvar+= (factual[itm->first][bw] - wished[itm->first][bw]) * (factual[itm->first][bw] - wished[itm->first][bw]);

					itm->second+= change;
					neigh_weigh[itm->first][i]+=change;
				}
			}
		}

		for (int bw=0; bw<3; bw++)
			newpartvar+= (factual[i][bw] - wished[i][bw]) * (factual[i][bw] - wished[i][bw]);
		tot_var+=newpartvar - oldpartvar;
	}
	//check_weights(neigh_weigh, member_list, wished, factual, tot_var, strs);
	return 0;
}

int BaseGenerator::print_network( int step, bool weighted, deque<set<int> > & E, const deque<deque<int> > & member_list, const deque<deque<int> > & member_matrix, deque<int> & num_seq, deque<map <int, double > > & neigh_weigh, double beta, double mu, double mu0) 
{
	int edges=0;
	int num_nodes=member_list.size();
	deque<double> double_mixing;
	int inactive = 0;
	for (int i=0; i < E.size(); i++) 
	{
		if( E[i].size() == 0 )
		{
			inactive++;
		}
		else
		{
			double one_minus_mu = double(internal_kin(E, member_list, i))/E[i].size();
			double_mixing.push_back(1.0 - one_minus_mu);
			edges += E[i].size();
		}
	}

	double density=0;
	double sparsity=0;
	for (int i = 0; i < member_matrix.size(); i++) 
	{
		double media_int=0;
		double media_est=0;
		for (int j=0; j < member_matrix[i].size(); j++) 
		{
			double kinj = double(internal_kin_only_one(E[member_matrix[i][j]], member_matrix[i]));
			media_int+= kinj;
			media_est+=E[member_matrix[i][j]].size() - double(internal_kin_only_one(E[member_matrix[i][j]], member_matrix[i]));
		}
		double pair_num=(member_matrix[i].size()*(member_matrix[i].size()-1));
		double pair_num_e=((num_nodes-member_matrix[i].size())*(member_matrix[i].size()));
		if (pair_num!=0)
			density+=media_int/pair_num;
		if (pair_num_e!=0)
			sparsity+=media_est/pair_num_e;
	}
	density = density/member_matrix.size();
	sparsity = sparsity/member_matrix.size();
	cout << "Network of "<<num_nodes<<" vertices and "<<edges/2<<" edges"<<"; average degree = "<<double(edges)/num_nodes;
	cout << "; " << inactive << " vertices with no edges" << endl;
	cout << "average mixing parameter (topology): "<< average_func(double_mixing)<<" +/- " << sqrt (variance_func(double_mixing))<<endl;
	cout << "p_in: "<<density<<"\tp_out: "<<sparsity<<endl;

	// Write network
	char buffer[1024];
	sprintf(buffer, "%s.t%02d.edges",OUTPUT_PREFIX,step);
	if( weighted )
	{
		cout << "Writing undirected weighted graph..." << endl;
		write_edge_list(buffer, E, neigh_weigh, false);
	}
	else
	{
		cout << "Writing undirected unweighted graph..." << endl;
		write_edge_list(buffer, E, false);
	}

	// Write communities
	cout << "Writing " << member_matrix.size() << " communities..." << endl;
#ifdef WRITE_COMMUNITY_PERLINE
	sprintf(buffer,"%s.t%02d.comm",OUTPUT_PREFIX,step);
	write_communities_bycommunity( buffer, member_matrix );
#else
	sprintf(buffer,"%s_community.t%02d.dat",OUTPUT_PREFIX, step);
	write_communities_bynode( buffer, member_list );
#endif

	// Write stats
	sprintf(buffer,"%s.t%02d.stats",OUTPUT_PREFIX,step);
	ofstream statout(buffer);
	deque<int> degree_seq;

	for (int i=0; i<E.size(); i++)
		degree_seq.push_back(E[i].size());

	statout << "degree distribution (probability density function of the degree in logarithmic bins) "<<endl;
	log_histogram(degree_seq, statout, 10);
	statout<<"degree distribution (degree-occurrences) "<<endl;
	int_histogram(degree_seq, statout);
	statout<<endl<<"--------------------------------------"<<endl;
	statout<<"community distribution (size-occurrences)"<<endl;
	int_histogram(num_seq, statout);
	statout<<endl<<"--------------------------------------"<<endl;
	statout<<"mixing parameter (topology)"<<endl;
	not_norm_histogram(double_mixing, statout, 20, 0, 0);
	statout<<endl<<"--------------------------------------"<<endl;

	deque<double> inwij;
	deque<double> outwij;
	//deque<double> inkij;
	//deque<double> outkij;
	double csi=(1. - mu) / (1. - mu0);
	double csi2=mu /mu0;
	double tstrength=0;
	deque<double> one_minus_mu2;
	for (int i=0; i<neigh_weigh.size(); i++) 
	{
		double internal_strength_i=0;
		double strength_i=0;
		for (map<int, double>::iterator itm = neigh_weigh[i].begin(); itm!=neigh_weigh[i].end(); itm++) 
		{
			if (they_are_mate(i, itm->first, member_list)) 
			{
				inwij.push_back(itm->second);
				//inkij.push_back(csi * pow(E[i].size(), beta-1));
				internal_strength_i+=itm->second;
			}
			else 
			{
				outwij.push_back(itm->second);
				//outkij.push_back(csi2 * pow(E[i].size(), beta-1));
			}
			tstrength+=itm->second;
			strength_i+=itm->second;
		}
		if( strength_i == 0 )
		{
			continue;
		}
		one_minus_mu2.push_back(1 - internal_strength_i/strength_i);
	}

	//cout<<"average strength "<<tstrength / E.size()<<"\taverage internal strenght: "<<average_internal_strenght<<endl;
	cout<<"average mixing parameter (weights): " << average_func(one_minus_mu2) << " +/- "<<sqrt(variance_func(one_minus_mu2))<<endl;
	statout<<"mixing parameter (weights)"<< endl;
	not_norm_histogram(one_minus_mu2, statout, 20, 0, 0);
	statout<<endl<<"--------------------------------------"<<endl;

	cout<<"average weight of an internal link "<<average_func(inwij)<<" +/- "<<sqrt(variance_func(inwij))<<endl;
	cout<<"average weight of an external link "<<average_func(outwij)<<" +/- "<<sqrt(variance_func(outwij))<<endl;

	//cout<<"average weight of an internal link expected "<<tstrength / edges * (1. - mu) / (1. - mu0)<<endl;
	//cout<<"average weight of an external link expected "<<tstrength / edges * (mu) / (mu0)<<endl;

	statout<<"internal weights (weight-occurrences)"<<endl;
	not_norm_histogram(inwij, statout, 20, 0, 0);
	statout<<endl<<"--------------------------------------"<<endl;

	statout<<"external weights (weight-occurrences)"<<endl;
	not_norm_histogram(outwij, statout, 20, 0, 0);
	cout<<endl;
	return 0;
}

int BaseGenerator::print_history( int steps ) 
{
	char buffer[1024];
	
	// Write history file
	sprintf(buffer, "%s.timeline",OUTPUT_PREFIX);
	cout << "Writing timeline for " << timeline.size() << " communities to " << buffer << " ..." << endl;
	timeline.write( buffer, steps );
	
	// Write events file?
	if( this->do_write_events )
	{
		sprintf(buffer, "%s.events",OUTPUT_PREFIX);
		cout << "Writing " << events.size() << " events to " << buffer << " ..." << endl;
		write_events( buffer, events );
	}
	return 0;
}
