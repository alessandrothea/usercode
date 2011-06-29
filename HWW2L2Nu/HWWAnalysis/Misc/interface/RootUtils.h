#ifndef _HWWAnalysis_Misc_RootUtils_h_
#define _HWWAnalysis_Misc_RootUtils_h_

class TFileDirectory;

namespace hww {
TH1D* makeLabelHistogram( const std::string& name, const std::string& title, std::map<int,std::string> labels);
TH1D* makeLabelHistogram( TFileDirectory*, const std::string& name, const std::string& title, std::map<int,std::string> labels);

}

#endif /* _HWWAnalysis_Misc_RootUtils_h_ */
