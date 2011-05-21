Double_t cruijff( Double_t *x, Double_t * par) {

 // par[0] = normalization
 // par[1] = mean
 // par[2] = sigmaL
 // par[3] = sigmaR
 // par[4] = alphaL
 // par[5] = alphaR

 double dx = (x[0]-par[1]) ;
 double sigma = dx<0 ? par[2]: par[3] ;
 double alpha = dx<0 ? par[4]: par[5] ;
 double f = 2*sigma*sigma + alpha*dx*dx ;
 return par[0] * exp(-dx*dx/f); //+ par[6] + par[7]*dx +par[8]*dx*dx;

}
