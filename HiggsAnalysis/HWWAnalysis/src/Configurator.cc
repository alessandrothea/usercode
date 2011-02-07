
/*
 * Configurator.cpp
 *
 *  Created on: Nov 20, 2010
 *      Author: ale
 */

#include "Configurator.h"
#include <iostream>

const std::string Configurator::DEFAULT = "default";
const std::string Configurator::OPTIONAL = "optional";


Configurator::Configurator() {
	// TODO Auto-generated constructor stub

}

Configurator::~Configurator() {
	// TODO Auto-generated destructor stub
}

//______________________________________________________________________________
void Configurator::addPar( const std::string& parName, const std::string& setName ) {

	std::set<std::string>& set = _parSets[setName];
	set.insert( parName );

}

//______________________________________________________________________________
void Configurator::addOptPar( const std::string& parName ) {
	addPar( parName, "optional" );
}

//______________________________________________________________________________
bool Configurator::load( TEnv* env ) {
    //
    //
    //

	if ( !this->_cfgLabel.empty() ) {
		if (env->Defined(_cfgLabel.c_str() ) ) {
    		_cfgType = env->GetValue(_cfgLabel.c_str(),"");
        } else {
            std::cout << "Configuration Label " << _cfgLabel << " not found" << std::endl;
            return false;
        }
	}

    if ( !checkCfg(env) ) {
        std::cout << "RC file " << env->GetRcName() << " is corrupted" << std::endl;
        return false;
    }


    import(env);

    return true;
}

//______________________________________________________________________________
bool Configurator::process( const std::string& cfgfile ) {
    //
    // Process configuration from file.
    // Calls CheckCfg to validate the file and FillMembers
    // to preform the filling.
    //
    TEnv env(cfgfile.c_str());

    return load(&env);

}

//______________________________________________________________________________
bool Configurator::checkCfg(TEnv *env)
{

	std::set<std::string>& defPars = _parSets[DEFAULT];
	std::set<std::string>& optPars = _parSets[OPTIONAL];

    std::cout << "Checking configuration " << (!_cfgType.empty() ? "(type "+_cfgType+")" : "" ) << std::endl;

    //defpars = FindCollection("default");
    Bool_t chk = kTRUE;
    chk &= checkSet(env, defPars);
    chk &= checkSet(env, optPars);

    // if the configuration has a specific type, check the type dependent parameters as well
    if ( !_cfgType.empty() ) chk &= checkSet(env, _parSets[_cfgType]);

    //if ( chk ) cout << "Pars ok" << endl;
    return chk;
}

//______________________________________________________________________________
bool Configurator::checkSet( TEnv* env, const std::set<std::string>& set ) {

	std::set<std::string>::iterator it;
	unsigned int notFound(0);
	for( it = set.begin(); it !=set.end(); ++it) {
		if ( !env->Defined((*it).c_str()) ) {
			++notFound;
			std::cout << "Parameter \"" << *it << "\" not found." << std::endl;
		}
	}

	if ( notFound != 0 )
	std::cout << "Error: " << notFound << " parameter(s) are missing." << std::endl;

	return (notFound == 0);
}

//______________________________________________________________________________
void Configurator::import( TEnv * env ) {
    //
	// Copies the parameters from env to the collections they have been assigned to.
	// _cfgType must be already set (done in process)
    //

   // TEnvRec* rec;
   // std::set<std::string> defpars = _parSets[DEFAULT];
    //std::set<std::string> optPars = _parSets[OPTIONAL];

	std::cout << "Importing configuration " << (!_cfgType.empty() ? "(type "+_cfgType+")" : "" ) << std::endl;

    importSet(env, _parSets[DEFAULT]);
    importSet(env, _parSets[OPTIONAL]);

    if ( _cfgType.empty() ) return;
    // import also the type specyfic required parameters
    importSet(env,_parSets[_cfgType]);

}

//______________________________________________________________________________
void Configurator::importSet( TEnv* env, const std::set<std::string>& set ) {
	//
	// Fills the fCfg with the parameters listed in set
	//
    TEnvRec *rec;
    std::set<std::string>::iterator it;
    for( it=set.begin(); it != set.end(); ++it) {
    	if ( (rec = env->Lookup((*it).c_str()) ) )
    		//        cout << "Entry name " << rec->GetName() << endl;
    		_theConfig.SetValue(rec->GetName(), rec->GetValue(), rec->GetLevel(), rec->GetType());
    }
}
//______________________________________________________________________________
void Configurator::print( const std::string& option ) {
	//
	// Print the parameter sets and the content of _theConfig
	//

	TString opt(option.c_str());
	opt.ToUpper();


	if ( opt.Contains('P') || opt.Contains("A") ) {

		//        std::cout << "Parameters required by " << GetName() << std::endl;
		//Info("Print","Configuration structure");

		std::map<std::string, std::set<std::string> >::iterator jt;
		for( jt = _parSets.begin(); jt != _parSets.end(); ++jt) {
			std::set<std::string>::iterator it;
			std::cout << "Configuration set [" << jt->first << "]" << std::endl;
			for( it=jt->second.begin(); it != jt->second.end(); ++it) {
				std::cout << "   " << *it << std::endl;
			}
		}
	}

	if ( opt.IsNull() || opt.Contains('C') || opt.Contains("A") ) {

		//Info("Print","Selected Config %s",fCfgValue.Data());
		_theConfig.Print();
	}
}



