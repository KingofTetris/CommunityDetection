#define OUTPUT_PREFIX "mergesplit"
#define APP_NAME "bench_mergesplit"

#include "settings.h"
#include "standard_include.cpp"
#include "parameters.cpp"
#include "generator_base.cpp"
#include "generator_switch.cpp"
#include "generator_mergesplit.cpp"

// ------------------------------------------------------------------------------------------------------------

int main(int argc, char *argv[])
{
	MergeSplitParameters p;
	if (set_parameters(argc, argv, p) == false)
	{
		return -1;
	}
	init_rand( p.seed );
	
	cout << "\n** Using MergeSplitGenerator..." << endl;
	MergeSplitGenerator* gen = new MergeSplitGenerator( &p ); 
	if( gen->generate( p.steps ) == 0 )
	{
		cout << "Done." << endl;
	}
	return 0;
}
