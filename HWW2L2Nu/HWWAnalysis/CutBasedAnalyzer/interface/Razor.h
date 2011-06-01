#ifndef RAZOR_H_
#define RAZOR_H_

// #include <TLorentzVector.h>
#include "DataFormats/Math/interface/LorentzVector.h"

namespace razor {
//     double MRstar(const TLorentzVector& ja, const TLorentzVector& jb);
//     double gammaMRstar( const TLorentzVector& ja, const TLorentzVector& jb);

    double MRstar(const math::XYZTLorentzVector& ja, const math::XYZTLorentzVector& jb);
    double gammaMRstar(const math::XYZTLorentzVector& ja, const math::XYZTLorentzVector& jb);
}
#endif /* RAZOR */
