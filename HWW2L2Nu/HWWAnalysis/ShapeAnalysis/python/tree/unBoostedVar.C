//////////////////////////////////////////////
//
// Written and designed by C. Rogan 23-08-12
// California Institute of Technology
//
//////////////////////////////////////////////


#include <TVector3.h>
#include <TLorentzVector.h>
#include <vector>

class HWWKinematics {
 public:
  //! constructor at least wants leptons and MET
  HWWKinematics(TLorentzVector l1, TLorentzVector l2, TVector3 met);
  virtual ~HWWKinematics() {}
  //! set the jets
  void setJets(std::vector<TLorentzVector> jets) { JETS = jets; }
  
  //! kinematic fuctions
  double CalcMRNEW();
  double CalcDeltaPhiRFRAME();
  double CalcDoubleDphiRFRAME();
  double CalcMR();

 private:
  TLorentzVector L1,L2;
  TVector3 MET;
  std::vector<TLorentzVector> JETS;
};


HWWKinematics::HWWKinematics(TLorentzVector l1, TLorentzVector l2, TVector3 met) {
  L1=l1;
  L2=l2;
  MET=met;
}


/////////////////////////////////////////////
// IMPORTANT - for all these, the MET
// needs to refer to the estimate of the 
// pt of the neutrino system, i.e. MET should be:
// MET = - sum_i pT_i
// where this is a vectoral sum and
// MUONS ARE INCLUDED in the sum!
// for example, if you are using PF MET
// then this is already the case
// if you are using calo MET, then you need to do:
// MET = caloMET - sum_i pT_i
// where this sum is over the muons
//////////////////////////////////////////////


// This is the pt corrected MR - here, we assume the pt
// of the Higgs is (MET+Pt+Qt);
// L1 and L2 are the 4-vectors for the 2 hemispheres, or in you case,
// the two leptons - setting mass to 0 should be fine
// MET is the MET 3 vector (don't forget to set the z-component of
// MET to 0)
// Also, 2 times this variable should give you the Higgs mass
double HWWKinematics::CalcMRNEW(){
  TVector3 vI = MET+L1.Vect()+L2.Vect();
  vI.SetZ(0.0);
  double L1pL2 = CalcMR(); //Note - this calls the old MR function
  double vptx = (L1+L2).Px();
  double vpty = (L1+L2).Py();
  TVector3 vpt;
  vpt.SetXYZ(vptx,vpty,0.0);
  
  float MR2 = 0.5*(L1pL2*L1pL2-vpt.Dot(vI)+L1pL2*sqrt(L1pL2*L1pL2+vI.Dot(vI)-2.*vI.Dot(vpt)));
  
  return sqrt(MR2);
  
}


// This is the pt corrected delta phi between the 2 leptons
// P and L2 are the 4-vectors for the 2 hemispheres, or in you case,
// the two leptons - setting mass to 0 should be fine
// MET is the MET 3 vector (don't forget to set the z-component of
// MET to 0)
// This function will do the correct Lorentz transformations of the 
// leptons for you
double HWWKinematics::CalcDeltaPhiRFRAME(){
  // first calculate pt-corrected MR
  float mymrnew = CalcMRNEW();
  
  // Now, boost lepton system to rest in z
  // (approximate accounting for longitudinal boost)
  TVector3 BL = L1.Vect()+L2.Vect();
  BL.SetX(0.0);
  BL.SetY(0.0);
  BL = (1./(L1.P()+L2.P()))*BL;
  L1.Boost(-BL);
  L2.Boost(-BL);
  
  // Next, calculate the transverse Lorentz transformation
  // to go to Higgs approximate rest frame
  TVector3 B = L1.Vect()+L2.Vect()+MET;
  B.SetZ(0.0);
  B = (-1./(sqrt(4.*mymrnew*mymrnew+B.Dot(B))))*B;
  
  L1.Boost(B);
  L2.Boost(B);
  
  //Now, re-calculate the delta phi
  // in the new reference frame:
  return L1.DeltaPhi(L2);
  
}

// This is the deltaphi between the di-lepton system and the Higgs
// boost in the approximate Higgs rest frame, or R-FRAME
// L1 and L2 are the 4-vectors for the 2 hemispheres, or in you case,
// the two leptons - setting mass to 0 should be fine
// MET is the MET 3 vector (don't forget to set the z-component of
// MET to 0)
// This function will do the correct Lorentz transformations of the 
// leptons for you
double HWWKinematics::CalcDoubleDphiRFRAME(){
  // first calculate pt-corrected MR
  float mymrnew = CalcMRNEW();
  
  TVector3 BL = L1.Vect()+L2.Vect();
  BL.SetX(0.0);
  BL.SetY(0.0);
  BL = (1./(L1.P()+L2.P()))*BL;
  L1.Boost(-BL);
  L2.Boost(-BL);
  
  //Next, calculate the transverse Lorentz transformation
  TVector3 B = L1.Vect()+L2.Vect()+MET;
  B.SetZ(0.0);
  B = (-1./(sqrt(4.*mymrnew*mymrnew+B.Dot(B))))*B;
  
  L1.Boost(B);
  L2.Boost(B);
  
  // Now, calculate the delta phi
  // between di-lepton axis and boost
  // in new reference frame
  
  return B.DeltaPhi(L1.Vect()+L2.Vect());
  
}

//////////////////////////////////////////////////
// below are function used by the above functions
// I wouldn't call these directly
//////////////////////////////////////////////////


//This is the updated MR definition that we use in the inclusive analysis 
//(no pt corrections or anything fancy)
// L1 and L2 are the 4-vectors for the 2 hemispheres, or in you case,
// the two leptons - setting mass to 0 should be fine
double HWWKinematics::CalcMR(){
  
  float MR = sqrt((L1.P()+L2.P())*(L1.P()+L2.P())-(L1.Pz()+L2.Pz())*(L1.Pz()+L2.Pz()));
  
  return MR;
}
