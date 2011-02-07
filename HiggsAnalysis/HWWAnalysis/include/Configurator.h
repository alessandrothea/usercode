/*
 * Configurator.h
 *
 *  Created on: Nov 20, 2010
 *      Author: ale
 */

#ifndef CONFIGURATOR_H_
#define CONFIGURATOR_H_

#include "TEnv.h"
#include <map>
#include <set>

class Configurator {
private:
	static const std::string DEFAULT;
	static const std::string OPTIONAL;
public:
	Configurator();
	virtual ~Configurator();

    void setCfgLabel(std::string _cfgLabel) { this->_cfgLabel = _cfgLabel; }
    void setCfgType(std::string _cfgType) { this->_cfgType = _cfgType; }
    std::string getCfgLabel() const { return _cfgLabel; }
    std::string getCfgType() const { return _cfgType; }

    virtual void addPar( const std::string&, const std::string& set = DEFAULT);
    virtual void addOptPar( const std::string& );
    virtual int         getValue(const std::string& name, int dflt) { return _theConfig.GetValue(name.c_str(), dflt); }
    virtual double      getValue(const std::string& name, double dflt) { return _theConfig.GetValue(name.c_str(), dflt); }
    virtual std::string getValue(const std::string& name, const std::string& dflt ) { return _theConfig.GetValue(name.c_str(), dflt.c_str()); }

    virtual bool process( const std::string& rcfile );
    virtual bool load( TEnv* env );

    virtual bool checkCfg( TEnv *env);
    virtual void print( const std::string& opt = "");
protected:
    virtual void import( TEnv* );
    virtual void importSet( TEnv* env, const std::set<std::string>& set );
private:
    bool checkSet( TEnv* env, const std::set<std::string>& set );
	std::string _cfgLabel;
	std::string _cfgType;
	std::map<std::string, std::set<std::string> > _parSets;

	TEnv _theConfig;

};

#endif /* CONFIGURATOR_H_ */
