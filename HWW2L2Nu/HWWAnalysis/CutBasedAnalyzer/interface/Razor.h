#ifndef RAZOR_H_
#define RAZOR_H_

#include <TLorentzVector.h>

namespace razor {
    double MRstar(const TLorentzVector& ja, const TLorentzVector& jb);
    double gammaMRstar( const TLorentzVector& ja, const TLorentzVector& jb);
}
#endif /* RAZOR */
