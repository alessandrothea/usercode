
#include "HWWAnalysis/CutBasedAnalyzer/interface/Razor.h"

namespace razor {

//
// this is the 'new' MRstar
//
double MRstar(const TLorentzVector& ja, const TLorentzVector& jb){
  double A = ja.P();
  double B = jb.P();
  double az = ja.Pz();
  double bz = jb.Pz();
  TVector3 jaT, jbT;
  jaT.SetXYZ(ja.Px(),ja.Py(),0.0);
  jbT.SetXYZ(jb.Px(),jb.Py(),0.0);

  double temp = sqrt((A+B)*(A+B)-(az+bz)*(az+bz)-
                     (jbT.Dot(jbT)-jaT.Dot(jaT))*(jbT.Dot(jbT)-jaT.Dot(jaT))/(jaT+jbT).Mag2());

  return temp;
}



//
// this is the 'new' MRstar, times 'gamma_{R*}' - I would recommend making 'R*' with this as
// the denominator and 'M_{T}^{R}' as the numerator (the next function in this file)
//
double gammaMRstar(const TLorentzVector& ja, const TLorentzVector& jb){
  double A = ja.P();
  double B = jb.P();
  double az = ja.Pz();
  double bz = jb.Pz();
  TVector3 jaT, jbT;
  jaT.SetXYZ(ja.Px(),ja.Py(),0.0);
  jbT.SetXYZ(jb.Px(),jb.Py(),0.0);
  double ATBT = (jaT+jbT).Mag2();

  double temp = sqrt((A+B)*(A+B)-(az+bz)*(az+bz)-
                     (jbT.Dot(jbT)-jaT.Dot(jaT))*(jbT.Dot(jbT)-jaT.Dot(jaT))/(jaT+jbT).Mag2());

  double mybeta = (jbT.Dot(jbT)-jaT.Dot(jaT))/
    sqrt(ATBT*((A+B)*(A+B)-(az+bz)*(az+bz)));

  double mygamma = 1./sqrt(1.-mybeta*mybeta);

  //gamma times MRstar                                                                                                                                                                                                                     
  temp *= mygamma;

  return temp;
}

}
