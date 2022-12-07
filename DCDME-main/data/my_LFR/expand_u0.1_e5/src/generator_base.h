#ifndef GENERATOR_BASE_H
#define GENERATOR_BASE_H

#include "history.cpp"

class BaseGenerator 
{
	Parameters* param;
		
public:
	BaseGenerator( Parameters* param );
	~BaseGenerator() {};
	
	int generate( int steps );
	virtual int mutate( int step, int num_nodes, deque<deque<int> > &member_matrix, multimap<int,int> &last_step_dynamic_map, multimap<int,int> &step_dynamic_map ) { return 0; };
	
protected:
	/** write events? */
	bool do_write_events;
	/** currently unassigned nodes */
	deque<int> unassigned;
	/** dynamic community timeline */
	DynamicTimeline timeline;
	/** list of all events */
	vector<Event> events;

	int benchmark(int steps, bool weighted, bool excess, bool defect, int num_nodes, double  average_k, int  max_degree, double  tau, double  tau2,
		double mixing_parameter, double  mixing_parameter2, double  beta, int  overlapping_nodes, int  overlap_membership, int  nmin, int  nmax, bool  fixed_range);

	int internal_degree_and_membership (double mixing_parameter, int overlapping_nodes, int max_mem_num, int num_nodes, deque<deque<int> >  & member_matrix,
		bool excess, bool defect,  deque<int> & degree_seq, deque<int> &num_seq, deque<int> &internal_degree_seq, bool fixed_range, int nmin, int nmax, double tau2);
		
	int change_community_size(deque<int> &seq);
	
	int build_bipartite_network(deque<deque<int> >  & member_matrix, const deque<int> & member_numbers, const deque<int> &num_seq);
	
	int build_subgraphs(deque<set<int> > & E, const deque<deque<int> > & member_matrix, deque<deque<int> > & member_list,
		deque<deque<int> > & link_list, const deque<int> & internal_degree_seq, const deque<int> & degree_seq, const bool excess, const bool defect);
	
	int build_subgraph(deque<set<int> > & E, const deque<int> & nodes, const deque<int> & degrees);
	
	int connect_all_the_parts(deque<set<int> > & E, const deque<deque<int> > & member_list, const deque<deque<int> > & link_list);
	
	int erase_links(deque<set<int> > & E, const deque<deque<int> > & member_list, const bool excess, const bool defect, const double mixing_parameter);
	
	int insert_weights(deque<set<int> > & en, const deque<deque<int> > & member_list, const double beta, const double mu, deque<map <int, double > > & neigh_weigh);
	
	int propagate(deque<map <int, double > > & neigh_weigh, const deque<deque<int> > & member_list, deque<deque<double> > & wished, deque<deque<double> > & factual, int i, double & tot_var, double *strs, const deque<int> & internal_kin_top);
	
	double solve_dmin(const double& dmax, const double &dmed, const double &gamma);
	
	int print_network(int step, bool weighted, deque<set<int> > & E, const deque<deque<int> > & member_list, const deque<deque<int> > & member_matrix, deque<int> & num_seq, deque<map <int, double > > & neigh_weigh, double beta, double mu, double mu0);
	
	int print_history(int steps);
};

#endif // GENERATOR_BASE_H
