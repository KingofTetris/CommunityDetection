#define OUTPUT_PREFIX "birthdeath"
#define APP_NAME "bench_birthdeath"

#include "settings.h"
#include "standard_include.cpp"
#include "parameters.cpp"
#include "generator_base.cpp"
#include "generator_switch.cpp"
#include "generator_birthdeath.cpp"

// ------------------------------------------------------------------------------------------------------------

int main(int argc, char *argv[])
{
	BirthDeathParameters p;
	if (set_parameters(argc, argv, p) == false)
	{
		return -1;
	}
	init_rand( p.seed );
	
	cout << "\n** Using BirthDeathGenerator..." << endl;
	BirthDeathGenerator* gen = new BirthDeathGenerator( &p ); 
	if( gen->generate( p.steps ) == 0 )
	{
		cout << "Done." << endl;
	}
	return 0;
}
