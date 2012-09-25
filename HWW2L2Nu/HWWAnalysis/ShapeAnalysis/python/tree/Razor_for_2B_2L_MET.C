//////////////////////////////////////////////
//
// Written and designed by C. Rogan 18-09-12
// California Institute of Technology
//
//////////////////////////////////////////////


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


#include "TLorentzVector.h"
#include "TVector3.h"




//////////////////////////////////////////////////
// below are function used by the above functions
// I wouldn't call these directly
//////////////////////////////////////////////////


//This is the old MR definition that we use in the inclusive analysis 
//(no pt corrections or anything fancy)
// B1 and B2 are the 4-vectors for the 2 B's, L1/L2 for the 2 leptons setting mass to 0 should be fine for theses
// M is the MET 3 vector (don't forget to set the z-component of
// MET to 0)
double CalcMR(TLorentzVector B1, TLorentzVector B2, TLorentzVector L1, TLorentzVector L2){
    double E = B1.P()+B2.P()+L1.P()+L2.P();
    double Pz = B1.Pz()+B2.Pz()+L1.Pz()+L2.Pz();

    float MR = sqrt(E*E-Pz*Pz);

    return MR;
}



//////////////////////////////////////////////////
// below are function to be used
//////////////////////////////////////////////////



// This is the pt corrected MR - here, we assume the pt
// of the sqrt{shat} system is (B1t+B2t+L1t+L2t);
// B1 and B2 are the 4-vectors for the 2 B's, L1/L2 for the 2 leptons setting mass to 0 should be fine
// M is the MET 3 vector (don't forget to set the z-component of
// MET to 0)
double CalcMRNEW(TLorentzVector B1, TLorentzVector B2, TLorentzVector L1, TLorentzVector L2, TVector3 M){
    TVector3 vI = M+B1.Vect()+B2.Vect()+L1.Vect()+L2.Vect();
    vI.SetZ(0.0);
    double PpQ = CalcMR(B1,B2,L1,L2); //Note - this calls the old MR function
    double vptx = (B1+B2+L1+L2).Px();
    double vpty = (B1+B2+L1+L2).Py();
    TVector3 vpt;
    vpt.SetXYZ(vptx,vpty,0.0);

    float MR2 = 0.5*(PpQ*PpQ-vpt.Dot(vI)+PpQ*sqrt(PpQ*PpQ+vI.Dot(vI)-2.*vI.Dot(vpt)));

    return sqrt(MR2);

}


// This is the pt corrected delta phi between the 2 (b+l) systems
// B1 and B2 are the 4-vectors for the 2 B's, L1/L2 for the 2 leptons setting mass to 0 should be fine
// M is the MET 3 vector (don't forget to set the z-component of
// MET to 0)
// This function will do the correct Lorentz transformations of the 
// leptons and b's for you, taking them to the 'approximate CM frame'
double CalcDeltaPhiRFRAME(TLorentzVector B1, TLorentzVector B2, TLorentzVector L1, TLorentzVector L2, TVector3 M){
    // first calculate pt-corrected MR
    float mymrnew = CalcMRNEW(B1,B2,L1,L2,M);

    TVector3 BL = B1.Vect()+B2.Vect()+L1.Vect()+L2.Vect();
    BL.SetX(0.0);
    BL.SetY(0.0);
    BL = (1./(B1.P()+B2.P()+L1.P()+L2.P()))*BL;
    B1.Boost(-BL);
    B2.Boost(-BL);
    L1.Boost(-BL);
    L2.Boost(-BL);

    //Next, calculate the transverse Lorentz transformation
    TVector3 B = B1.Vect()+B2.Vect()+L1.Vect()+L2.Vect()+M;
    B.SetZ(0.0);
    B = (-1./(sqrt(4.*mymrnew*mymrnew+B.Dot(B))))*B;

    B1.Boost(B);
    B2.Boost(B);
    L1.Boost(B);
    L2.Boost(B);

    //Now, re-calculate the delta phi
    // in the new reference frame:
    return (B1+L1).DeltaPhi(B2+L2);

}

// This is the deltaphi between the (2b+2l) system and the CM boost
// boost in the approximate CM rest frame, or R-FRAME
// B1 and B2 are the 4-vectors for the 2 B's, L1/L2 for the 2 leptons setting mass to 0 should be fine
// M is the MET 3 vector (don't forget to set the z-component of
// MET to 0)
// This function will do the correct Lorentz transformations of the 
// leptons and b's for you, taking them to the 'approximate CM frame'
double CalcDoubleDphiRFRAME(TLorentzVector B1, TLorentzVector B2, TLorentzVector L1, TLorentzVector L2, TVector3 M){
    // first calculate pt-corrected MR
    float mymrnew = CalcMRNEW(B1,B2,L1,L2,M);

    TVector3 BL = B1.Vect()+B2.Vect()+L1.Vect()+L2.Vect();
    BL.SetX(0.0);
    BL.SetY(0.0);
    BL = (1./(B1.P()+B2.P()+L1.P()+L2.P()))*BL;
    B1.Boost(-BL);
    B2.Boost(-BL);
    L1.Boost(-BL);
    L2.Boost(-BL);

    //Next, calculate the transverse Lorentz transformation
    TVector3 B = B1.Vect()+B2.Vect()+L1.Vect()+L2.Vect()+M;
    B.SetZ(0.0);
    B = (-1./(sqrt(4.*mymrnew*mymrnew+B.Dot(B))))*B;

    B1.Boost(B);
    B2.Boost(B);
    L1.Boost(B);
    L2.Boost(B);

    // Now, calculate the delta phi
    // between di-lepton axis and boost
    // in new reference frame

    return B.DeltaPhi(B1.Vect()+B2.Vect()+L1.Vect()+L2.Vect());

}

