#ifdef __CINT__

#pragma link off all globals;
#pragma link off all classes;
#pragma link off all functions;
#pragma link C++ nestedclasses;

#pragma link C++ class HWWEvent+;
#pragma link C++ class HWWNtuple+;
#pragma link C++ class HWWElectron+;
#pragma link C++ class HWWMuon+;
//FIXME #pragma link C++ class HWWJet+;
#pragma link C++ class HWWPFJet+;

#pragma link C++ class std::vector<HWWElectron>+;
#pragma link C++ class std::vector<HWWMuon>+;
//FIXME #pragma link C++ class std::vector<HWWJet>+;
#pragma link C++ class std::vector<HWWPFJet>+;

#endif
