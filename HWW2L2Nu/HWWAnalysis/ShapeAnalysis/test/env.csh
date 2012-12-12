#! /bin/csh
setenv SOURCE "$CMSSW_BASE"
setenv SCRIPTS "$SOURCE/src/HWWAnalysis/ShapeAnalysis/scripts"
setenv PYTHON "$SOURCE/src/HWWAnalysis/ShapeAnalysis/python"

setenv PATH "${PATH}:${PYTHON}:${SCRIPTS}"
setenv PYTHONPATH "${PYTHONPATH}:${SCRIPTS}"
echo "$SCRIPTS added to PATH and PYTHONPATH"
setenv PYTHONPATH "${PYTHONPATH}:${PYTHON}"
echo "$PYTHON added to PATH"

