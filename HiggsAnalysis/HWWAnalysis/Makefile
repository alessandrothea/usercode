CXX:=g++
CxxFlags:=-g -ggdb -pedantic -ansi -pthread -pipe -fvisibility-inlines-hidden -felide-constructors -fmessage-length=0 -ftemplate-depth-300 -Wall -Wno-non-template-friend -Wno-long-long -Wimplicit -Wreturn-type -Wunused -Wparentheses -Wno-deprecated -Werror=return-type -Werror=missing-braces -Werror=unused-value -Werror=address -Werror=format -Werror=sign-compare -Werror=write-strings -Werror=strict-overflow -fdiagnostics-show-option 
CPPVERBOSE:=true
ROOTCINT:=rootcint -v4

ifdef ROOTSYS
ROOTCFLAGS=$(shell root-config --cflags)
ROOTLIBS=$(shell root-config --libs)
ROOTGLIBS=$(shell root-config --glibs)
else
$(error root not configured properly)
endif

Echo=

BuildPath:=tmp
LibPath:=lib
BinPath:=bin
LdFlags:= -L$(LibPath)

DUMMY := $(shell [ ! -d $(BuildPath) ] && mkdir -p $(BuildPath) )
DUMMY := $(shell [ ! -d $(LibPath) ] && mkdir -p $(LibPath) )
DUMMY := $(shell [ ! -d $(BinPath) ] && mkdir -p $(BinPath) )

RootDict   := G___HWWDict
Executives := runHWW selectHWW
Library    := HWWNtuple
LinkDef    := include/HWWLinkDef.h

Binaries   :=$(Executives:%=$(BinPath)/%.exe)
SharedLibrary := $(Library:%=$(LibPath)/lib%.so)

Includes := -Iinclude

CxxFlags+= $(ROOTCFLAGS) -fPIC $(Includes)
LdFlags+=$(ROOTLIBS) -lEG -lTreePlayer
RootDictSource=$(BuildPath)/$(RootDict).cc
RootDictHeader=$(BuildPath)/$(RootDict).h
RootDictObject=$(RootDictSource:.cc=.o)

BinSources := src/ETHZNtupleReader.cc \
		src/ETHZNtupleSelector.cc \
		src/ETHZHltChecker.cc \
		src/HWWSelectorB.cc \
		src/HWWCandidates.cc \
		src/Configurator.cc \
		src/CommandLine.cc \
		src/UserAnalyzer.cc \
		src/HWWAnalyzer.cc 

LibSources := src/HWWNtuple.cc src/HWWEvent.cc
LibHeaders := $(LibSources:src/%.cc=include/%.h)

BinObjects := $(patsubst src/%.cc,$(BuildPath)/%.o,$(BinSources))
LibObjects := $(patsubst src/%.cc,$(BuildPath)/%.o,$(LibSources)) $(RootDictObject)

Dependencies := $(BinObjects:.o=.d) $(LibObjects:.o=.d)

#$(warning $(LibSources))
#$(warning '$(LibObjects)')
#$(warning $())
#$(warning $(RootDictObject))

all: $(Binaries) $(SharedLibrary)

lib: $(SharedLibrary)

dict: $(RootDictSource)

$(LibPath)/lib%.so: $(LibObjects) $(RootDictObject)
	@echo Building $@
	$(CXX) --shared $(CxxFlags) $(LdFlags) $^ -o $@

$(BinPath)/%.exe: src/%.cc $(SharedLibrary) $(BinObjects)
	@echo Compiling $@
	$(CXX) $(CxxFlags) $(LdFlags) $(LibObjects) $(BinObjects) $< -o $@
#	$(CXX) $(CxxFlags) $(LdFlags) -l$(Library) $(BinObjects) $< -o $@
	
clean:
	@echo Cleaning up:
	@echo   $(Executives) $(SharedLibrary) $(Dependencies)
ifdef CPPVERBOSE
	rm -f $(Binaries) $(SharedLibrary)
	rm -f $(RootDictSource) $(RootDictHeader) $(Dependencies)
	rm -f $(BinObjects) $(LibObjects)
else
	@rm -f $(Binaries) $(SharedLibrary)
	@rm -f $(RootDictSource) $(RootDictHeader) $(Dependencies)
	@rm -f $(BinObjects) $(LibObjects)
endif


$(RootDictObject): $(RootDictSource)
	@echo Compiling $(<F)
	$(CXX) -c $(CxxFlags) -I. $< -o $@

$(RootDictSource): $(LibHeaders) $(LinkDef)
	@echo Building $(@F) dictionary...
ifdef CPPVERBOSE
	$(ROOTCINT) -f $@ -c -p $(Includes) -I. $(LibHeaders) $(LinkDef)
else
	@$(ROOTCINT) -f $@ -c -p $(Includes) -I. $(HDRS) $(LinkDef)
endif

$(BuildPath)/%.o: src/%.cc
	@echo Compiling $(<F)
ifdef CPPVERBOSE
	$(CXX) -c $(CxxFlags) $< -o $@
else
	@$(CXX) -c $(CxxFlags) $< -o $@
endif


#dependencies
$(BuildPath)/%.d: src/%.cc
	@echo Making dependency for file $<...
	@touch $@
	@set -e; rmkdepend -f- -Y -w3000 -- $(CxxFlags) $< 2> /dev/null \
        | sed 's!$(<D)/\($*\)\.o[ :]*!$(BuildPath)/\1.o $@ : !g' > $@; \
        [ -s $@ ] || rm -f $@

ifneq ($(MAKECMDGOALS),clean)
ifneq ($(Dependencies),)
-include $(Dependencies)
endif
endif
