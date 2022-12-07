// --------------------------------------------------------------------------
// Class: Event
// --------------------------------------------------------------------------

class Event
{
public:
	Event( const int step, const string name );
	
	void add( const int index );
	
	string name;
	int step;
	vector<int> indices;
};

Event::Event( const int step, const string name )
{
	this->name = name;
	this->step = step;
}

void Event::add( const int index )
{
	indices.push_back( index );
}

void write_events( const char *fname, vector<Event> &events )
{
	ofstream out(fname);
	vector<Event>::iterator it;
	for(it = events.begin(); it != events.end(); it++)
	{
		out << (*it).step << "," << (*it).name;
		for( int i = 0; i < (*it).indices.size(); i++ )
		{
			out << "," <<  (*it).indices[i];
		} 
		out << endl;
	}
	out.close();
}

// --------------------------------------------------------------------------
// Class: Event
// --------------------------------------------------------------------------

typedef map<int,int> DynamicRecord;

class DynamicTimeline
{
public:
	void clear();
	void add( const int step, const int dynamic_index, const int step_cluster_index );
	
	int create_record();
	int copy_record( const int index );
	DynamicRecord &get_record( const int index );
	const int size();
	void write( const char *fname, const int steps );
	
protected:
	vector<DynamicRecord> records;
};


void DynamicTimeline::clear()
{
	records.clear();
}

int DynamicTimeline::create_record()
{
	int next_index = size();
	DynamicRecord dyn;
	records.push_back( dyn );
	return next_index;
}

int DynamicTimeline::copy_record( const int index )
{
	int next_index = size();
	DynamicRecord dupe;
	dupe.insert(records[index].begin(), records[index].end());
	records.push_back( dupe );
	return next_index;
}

DynamicRecord &DynamicTimeline::get_record( const int index )
{
	return records[index];
}

const int DynamicTimeline::size()
{
	return records.size();
}

void DynamicTimeline::add( const int step, const int dynamic_index, const int step_cluster_index )
{
	// printf("dyn=%d step=%d step_cluster=%d\n", dynamic_index, step, step_cluster_index );
	records[dynamic_index].insert(make_pair(step,step_cluster_index));
}

void DynamicTimeline::write( const char *fname, const int steps )
{
	ofstream out(fname);
	for (int dynamic_index = 0; dynamic_index < size(); dynamic_index++) 
	{
		out << "M" << (dynamic_index+1) << ":";
		DynamicRecord rec = get_record( dynamic_index );
		for( int step = 1; step <= steps; step++ )
		{
			map<int, int>::iterator p = rec.find( step );
			if(p != rec.end())
			{
				// NB: increment
				int step_cluster_index = p->second + 1;
				out << step << "=" << step_cluster_index;
				if( step < steps )
				{
					out << ",";
				}
			}
		}
		out << endl;
	}
	out.close();
}