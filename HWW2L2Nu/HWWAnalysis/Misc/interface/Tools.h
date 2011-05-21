/*
 * Tools.h
 *
 *  Created on: Dec 14, 2010
 *      Author: ale
 */

#ifndef TOOLS_H_
#define TOOLS_H_

#include <stdexcept>
#include <sstream>
#include <algorithm>

#define THROW_RUNTIME(__STRING__) { \
	std::stringstream ss; \
	ss << __STRING__ << " - " <<__FILE__<<':'<<__LINE__<<"   "<<__PRETTY_FUNCTION__;\
	throw std::runtime_error(ss.str());\
}

namespace TermColors {

const char *const kEsc         = "\033[";
const char *const kReset       = "\033[0m";
const char *const kBlack       = "\033[30m";
const char *const kRed         = "\033[31m";
const char *const kGreen       = "\033[32m";
const char *const kYellow      = "\033[33m";
const char *const kBlue        = "\033[34m";
const char *const kMagenta     = "\033[35m";
const char *const kCyan        = "\033[36m";
const char *const kWhite       = "\033[37m";
const char *const kDarkGray     = "\033[1;30m";
const char *const kLightRed     = "\033[1;31m";
const char *const kLightGreen   = "\033[1;32m";
//const char *const Yellow       = "\033[1;33m";
const char *const kLightBlue    = "\033[1;34m";
const char *const kLightMagenta = "\033[1;35m";
const char *const kLightCyan    = "\033[1;36m";
//const char *const kWhite        = "\033[1;37m";


const char *const kBckBlack         = "\033[40m";
const char *const kBckRed           = "\033[41m";
const char *const kBckGreen         = "\033[42m";
const char *const kBckYellow        = "\033[43m";
const char *const kBckBlue          = "\033[44m";
const char *const kBckMagenta       = "\033[45m";
const char *const kBckCyan          = "\033[46m";
const char *const kBckWhite         = "\033[47m";
const char *const kBckDarkGray      = "\033[1;40m";
const char *const kBckLightRed      = "\033[1;41m";
const char *const kBckLightGreen    = "\033[1;42m";
//const char *const kBckYellow        = "\033[1;43m";
const char *const kBckLightBlue     = "\033[1;44m";
const char *const kBckLightMagenta  = "\033[1;45m";
const char *const kBckLightCyan     = "\033[1;46m";
//const char *const kBckWhite         = "\033[1;47m";

const char *const kUnderline = "\033[4m";
const char *const kBlink     = "\033[5m";
const char *const kBright    = "\033[1m";
const char *const kDark      = "\033[2m";
}

template <class T>
std::vector<T> minMax( const std::vector<T>& v ) {
    std::vector<T> minMax;
    if ( v.size() == 0 )
        return minMax;
    
    minMax.resize(2);
    // element 0 is max
    minMax[0] = *std::max_element(v.begin(),v.end());
    minMax[1] = *std::min_element(v.begin(),v.end());   

    return minMax;
}
#endif /* TOOLS_H_ */
