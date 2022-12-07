// ------------------------------------------------------------------------------------------------------------
// I/O-related Functions
// ------------------------------------------------------------------------------------------------------------

/**
 * Write weighted edge list.
 */
void write_edge_list( const char *fname, deque<set<int> > &E, deque<map <int, double > > & weights, bool directed )
{
	ofstream out(fname);
	int edges = E.size();
	int row, col;
	for (int u=0; u<edges; u++) 
	{
		set<int>::iterator itb=E[u].begin();
		while (itb!=E[u].end())
		{
			row = u+1;
			col = *(itb++)+1;
			if( directed )
			{
				out << row << " " <<  col << " " << weights[u][*(itb)] << endl;
			}
			else if( row < col )
			{
				out << row << " " <<  col << " " << weights[u][*(itb)] << endl;
			}
		}
	}
}

/**
 * Write unweighted edge list.
 */
void write_edge_list( const char *fname, deque<set<int> > &E, bool directed )
{
	ofstream out(fname);
	int edges = E.size();
	int row, col;
	for (int u=0; u<edges; u++) 
	{
		set<int>::iterator itb=E[u].begin();
		while (itb!=E[u].end())
		{
			row = u+1;
			col = *(itb++)+1;
			if( directed )
			{
				out << row << " " <<  col << endl;
			}
			else if( row < col )
			{
				out << row << " " <<  col << endl;
			}			
		}
	}
	out.close();
}

/**
 Write list of communities to a file, one line per node (default in original code)
 */
void write_communities_bynode( const char *fname, const deque<deque<int> > & member_list )
{
	ofstream out(fname);
	for (int i=0; i< member_list.size(); i++) 
	{
		out << i+1 <<"\t";
		for (int j=0; j< member_list[i].size(); j++)
		{
			out << member_list[i][j] + 1 <<" ";
		}
		out << endl;
	}
	out.close();
}

/**
 Write list of communities to a file, one line per community
 */
void write_communities_bycommunity( const char *fname, const deque<deque<int> > &member_matrix )
{
	ofstream out(fname);
	for (int i=0; i< member_matrix.size(); i++) 
	{
		for (int j=0; j< member_matrix[i].size(); j++) 
		{
			// NB: increment
			out << member_matrix[i][j] + 1 << " ";
		}
		out<<endl;
	}
	out.close();
}

void erase_file_if_exists(string s) 
{
	char b[100];
	cast_string_to_char(s, b);

	ifstream in1(b);
	if (in1.is_open()) 
	{
		char rmb[120];
		sprintf(rmb, "rm %s", b);
		int erase= system(rmb);
	}
}

void print_memberships( deque<deque<int> > &member_matrix )
{
	for (int i=0; i<member_matrix.size(); i++) 
	{
		printf("C%d: ",i+1);
		for (int j=0; j<member_matrix[i].size(); j++) 
		{
			printf("%d ",member_matrix[i][j]);
		}
		printf("\n");
	}
}

void print_int_deque( deque<int> v )
{
	for (int j = 0; j < v.size(); j++) 
	{
		printf("%d ",v[j]);
	}
	printf("\n");
}

int median_cluster_size( const deque<deque<int> > &member_matrix )
{
	vector <int> sizes;
	for (int i=0; i < member_matrix.size(); i++) 
	{
		sizes.push_back( (int)member_matrix[i].size() );
	}
	sort(sizes.begin(), sizes.end());
	
	int k = (int)sizes.size();
	int i = k / 2;
	if( (k%2)==0 )
	{
		return (sizes[i-1]+sizes[i])/2; 
	}
	return sizes[i];
}

int assigned_count( const deque<deque<int> > &member_matrix )
{
	set<int> assigned;
	for (int i=0; i<member_matrix.size(); i++) 
	{
		for (int j=0; j<member_matrix[i].size(); j++) 
		{
			assigned.insert(member_matrix[i][j]);
		}
	}
	return (int)assigned.size();
}

// ------------------------------------------------------------------------------------------------------------
// Data structure related Functions
// ------------------------------------------------------------------------------------------------------------

/** 
 Computes the sum of a deque<int>
 */
int deque_int_sum(const deque<int> & a) 
{
	int s=0;
	for (int i=0; i<a.size(); i++)
	{
		s+=a[i];
	}
	return s;
}

bool they_are_mate(int a, int b, const deque<deque<int> > & member_list) 
{
	for (int i=0; i<member_list[a].size(); i++) 
	{
		if (binary_search(member_list[b].begin(), member_list[b].end(), member_list[a][i]))
			return true;
	}
	return false;
}

int internal_kin(deque<set<int> > & E, const deque<deque<int> > & member_list, int i) 
{
	int var_mate2=0;
	for (set<int>::iterator itss= E[i].begin(); itss!=E[i].end(); itss++) if (they_are_mate(i, *itss, member_list))
			var_mate2++;
	return var_mate2;
}

/**
 Return the overlap between E and member_matrix_j
 */
int internal_kin_only_one(set<int> & E, const deque<int> & member_matrix_j) 
{		
	int var_mate2=0;
	for (set<int>::iterator itss= E.begin(); itss!=E.end(); itss++) 
	{
		if (binary_search(member_matrix_j.begin(), member_matrix_j.end(), *itss))
			var_mate2++;
	}
	return var_mate2;
}

// ------------------------------------------------------------------------------------------------------------
// Graph-related Functions
// ------------------------------------------------------------------------------------------------------------

/**
 * Computes the integral of a power law.
 */
double integral (double a, double b) 
{
	if (fabs(a+1.)>1e-10)
	{
		return (1./(a+1.)*pow(b, a+1.));
	}
	return (log(b));
}


// it returns the average degree of a power law
double average_degree(const double &dmax, const double &dmin, const double &gamma) 
{
	return (1./(integral(gamma, dmax)-integral(gamma, dmin)))*(integral(gamma+1, dmax)-integral(gamma+1, dmin));
}

// it computes the correct (i.e. discrete) average of a power law
double integer_average (int n, int min, double tau) 
{
	double a=0;
	for (double h=min; h<n+1; h++)
	{
		a+= pow((1./h),tau);
	}
	double pf=0;
	for (double i=min; i<n+1; i++)
	{
		pf+=1/a*pow((1./(i)),tau)*i;
	}
	return pf;
}

int compute_internal_degree_per_node(int d, int m, deque<int> & a) 
{
	// d is the internal degree
	// m is the number of memebership
	a.clear();
	int d_i= d/m;

	for (int i=0; i<m; i++)
		a.push_back(d_i);

	for (int i=0; i<d%m; i++)
		a[i]++;

	return 0;
}