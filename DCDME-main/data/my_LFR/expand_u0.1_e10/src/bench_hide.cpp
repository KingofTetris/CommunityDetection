#define OUTPUT_PREFIX "hide"
#define APP_NAME "bench_hide"

#include "settings.h"
#include "standard_include.cpp"
#include "parameters.cpp"
#include "generator_base.cpp"
#include "generator_switch.cpp"
#include "generator_hide.cpp"

// ------------------------------------------------------------------------------------------------------------

int main(int argc, char *argv[])
{
	HiddenParameters p;
	if (set_parameters(argc, argv, p) == false)
	{
		return -1;
	}
	init_rand( p.seed );
	
	cout << "\n** Using HiddenGenerator..." << endl;
	HiddenGenerator* gen = new HiddenGenerator( &p ); 
	if( gen->generate( p.steps ) == 0 )
	{
		cout << "Done." << endl;
	}
	return 0;
}
