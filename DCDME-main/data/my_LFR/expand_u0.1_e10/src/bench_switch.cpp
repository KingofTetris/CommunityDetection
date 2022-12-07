#define OUTPUT_PREFIX "switch"
#define APP_NAME "bench_switch"

#include "settings.h"
#include "standard_include.cpp"
#include "parameters.cpp"
#include "generator_base.cpp"
#include "generator_switch.cpp"

// ------------------------------------------------------------------------------------------------------------

int main(int argc, char *argv[])
{
	SwitchParameters p;
	if (set_parameters(argc, argv, p) == false)
	{
		return -1;
	}
	init_rand( p.seed );
	
	cout << "\n** Using SwitchGenerator..." << endl;
	SwitchGenerator* gen = new SwitchGenerator( &p ); 
	if( gen->generate( p.steps ) == 0 )
	{
		cout << "Done." << endl;
	}
	return 0;
}
