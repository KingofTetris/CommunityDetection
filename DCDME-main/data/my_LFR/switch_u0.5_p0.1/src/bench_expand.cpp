#define OUTPUT_PREFIX "expand"
#define APP_NAME "bench_expand"

#include "settings.h"
#include "standard_include.cpp"
#include "parameters.cpp"
#include "generator_base.cpp"
#include "generator_switch.cpp"
#include "generator_expand.cpp"

// ------------------------------------------------------------------------------------------------------------

int main(int argc, char *argv[])
{
	ExpandContractParameters p;
	if (set_parameters(argc, argv, p) == false)
	{
		return -1;
	}
	init_rand( p.seed );
	
	cout << "\n** Using ExpandContractGenerator..." << endl;
	ExpandContractGenerator* gen = new ExpandContractGenerator( &p ); 
	if( gen->generate( p.steps ) == 0 )
	{
		cout << "Done." << endl;
	}
	return 0;
}
