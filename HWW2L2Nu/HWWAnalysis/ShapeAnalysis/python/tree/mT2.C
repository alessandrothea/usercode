#include <iostream>
#include <vector>

#include <TMinuit.h>



//---- global variable, used for minuit ----
std::vector<double>* VectX = new std::vector<double>;


//---- max (mt_1,mt_2) ----
void function(int& npar, double* d, double& r, double par[], int flag){
 int n = VectX->size();
 double maxmt2 = 0.0;


 double px1 = VectX->at(0);
 double py1 = VectX->at(1);
 double px2 = VectX->at(2);
 double py2 = VectX->at(3);
 double metx = VectX->at(4);
 double mety = VectX->at(5);

 double met1    = par[0];
 double metphi1 = par[1];
 double metx1 = met1 * cos (metphi1);
 double mety1 = met1 * sin (metphi1);

 double metx2 = metx - metx1;
 double mety2 = mety - mety1;
 double met2 = sqrt(metx2*metx2 + mety2*mety2);

 double p1 = sqrt(px1*px1 + py1*py1);
 double p2 = sqrt(px2*px2 + py2*py2);
 double mt1 = 2. * p1 * met1 * (1.-(px1*metx1+py1*mety1)/(p1*met1));
 double mt2 = 2. * p2 * met2 * (1.-(px2*metx2+py2*mety2)/(p2*met2));

 if (mt1>mt2) maxmt2 = mt1;
 else maxmt2 = mt2;

 r = sqrt(maxmt2);
}




float mT2(double pxl1, double pyl1, double pxl2, double pyl2, double metx, double mety) {

 if (VectX->size() != 6) { 
  VectX->push_back( pxl1 );
  VectX->push_back( pyl1 );
  VectX->push_back( pxl2 );
  VectX->push_back( pyl2 );
  VectX->push_back( metx );
  VectX->push_back( mety );
 }
 else {
  VectX->at(0) = pxl1 ;
  VectX->at(1) = pyl1 ;
  VectX->at(2) = pxl2 ;
  VectX->at(3) = pyl2 ;
  VectX->at(4) = metx ;
  VectX->at(5) = mety ;
 }

 double mT2 = 0.;

 double met = 10;
 double PI = 3.14159266;

 const int nParametri = 2;
 TMinuit minuit(nParametri);
 minuit.SetFCN(function);

 minuit.SetPrintLevel(-1); // quiet

 met = sqrt( metx*metx + mety*mety );

 double par[nParametri]={met/2.,0.0};
 double stepSize[nParametri]={met/100.,0.001};
 double minVal[nParametri]={met/100.,0.0};
 double maxVal[nParametri]={30.*met,2.*PI};
 string parName[nParametri]={"met1","metphi1"};
 for (int i=0; i<nParametri; i++){
  minuit.DefineParameter(i,parName[i].c_str(),par[i],stepSize[i],minVal[i],maxVal[i]);
 }

 minuit.Migrad();
//  double outParametri[nParametri];
//  double errParametri[nParametri];
//  for (int i=0; i<nParametri; i++){
//   minuit.GetParameter(i,outParametri[i],errParametri[i]);
//   std::cout << "outParametri[" << i << "] = " << outParametri[i] << " +/- " << errParametri[i] << std::endl;
//  }

 mT2 = minuit.fAmin;
//  std::cout << " "  << pxl1 << " ; " << pyl1 << " ; " << pxl2 << " ; " << pyl2 << " ; " << metx << " ; " << mety << " --> mT2 = " << mT2 << std::endl;
 return mT2;
}