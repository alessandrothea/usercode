// #include "DataFormats/Common/interface/Wrapper.h"

//Add includes for your classes here
#include "HWWAnalysis/DataFormats/interface/HWWEvent.h"
#include "HWWAnalysis/DataFormats/interface/HWWNtuple.h"
#include "HWWAnalysis/DataFormats/interface/DileptonView.h"
#include <vector>
#include <map>
#include <TLorentzVector.h>

namespace {
   struct HWWAnalysis_DataFormats {
       HWWEvent     dummyEvent;
       HWWLepton    dummyLepton;
       HWWElectron  dummyElectron;
       HWWMuon      dummyMuon;
       HWWPFJet     dummyJet;
       HWWSlimBTags dummySlimBtags;
       std::vector<HWWElectron>     dummy11;
       std::vector<HWWMuon>         dummy12;
       std::vector<HWWPFJet>        dummy13;
       std::vector<HWWSlimBTags>    dummy14;
       HWWNtuple dummy5;

//        hww::EventView               dummy20;
//        edm::Wrapper<hww::EventView> dummy21;
//        std::vector<hww::EventView>  dummy22;
//        edm::Wrapper<std::vector<hww::EventView> > dummy23;

       hww::DileptonView               dummy30;
       edm::Wrapper<hww::DileptonView> dummy31;
       std::vector<hww::DileptonView>  dummy32;
       edm::Wrapper<std::vector<hww::DileptonView> > dummy33;
       
       edm::Ptr<reco::RecoCandidate>  dummyRecoPtr;
       std::vector<edm::Ptr<reco::RecoCandidate> > dummyRecoPtrVec;

   
      edm::Wrapper<std::map<std::string,int> > dummyStrIntMap;
//add 'dummy' Wrapper variable for each class type you put into the Event
//       edm::Wrapper<YOUR_CLASS_GOES_HERE> dummy1;
//       std::vector<YOUR_CLASS_GOES_HERE> dummy2;
//       edm::Wrapper<std::vector<YOUR_CLASS_GOES_HERE> > dummy3;
/*
    These classes are commented out because they are used more rarely. If you need them, move them
    outside the comments and make the corresponding change in classes_def.xml
      
uncomment_h_here

      edm::Ref<std::vector<YOUR_CLASS_GOES_HERE> > dummy4;
      edm::RefVector<std::vector<YOUR_CLASS_GOES_HERE> > dummy5;
      edm::RefProd<std::vector<YOUR_CLASS_GOES_HERE> > dummy6;
*/

   };
}
