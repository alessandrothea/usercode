#  _____         _    
# |_   _|___ ___| |___
#   | | / _ | _ \ (_-<
#   |_| \___|___/_/__/
#

import os.path
import hwwinfo


def confirm(prompt=None, resp=False):
    """prompts for yes or no response from the user. Returns True for yes and
    False for no.
    
    'resp' should be set to the default value assumed by the caller when
    user simply types ENTER.
    >>> confirm(prompt='Create Directory?', resp=True)
    Create Directory? [y]|n: 
    True
    >>> confirm(prompt='Create Directory?', resp=False)
    Create Directory? [n]|y: 
    False
    >>> confirm(prompt='Create Directory?', resp=False)
    Create Directory? [n]|y: y
    True
    """
    
    if prompt is None:
        prompt = 'Confirm'

    if resp:
        prompt = '%s [%s]|%s: ' % (prompt, 'y', 'n')
    else:
        prompt = '%s [%s]|%s: ' % (prompt, 'n', 'y')
        
    while True:
        ans = raw_input(prompt)
        if not ans:
            return resp
        if ans not in ['y', 'Y', 'n', 'N']:
            print 'please enter y or n.'
            continue
        if ans == 'y' or ans == 'Y':
            return True
        if ans == 'n' or ans == 'N':
            return False

def getChain( sample, mass, path, tag='Data2011', tname='latino' ):
    import ROOT
    files = []
    try:
        all = hwwinfo.samples(mass, tag)
        files = all[sample]
    except Exception as e:
        print 'Exception',e
        return None

    chain = ROOT.TChain(tname)
    for f in files: chain.Add(os.path.join(path,f))
    
    return chain

    

def loadOptDefaults(parser,rc='shape.rc'):
    '''
    Load the default options from the configuation file.
    The new defaults options shall be written in python, as they are interpreted
    '''
#     import imp
    filename='shape.py'
    if os.path.exists(filename):
        handle = open(filename,'r')
        vars = {}
        exec(handle,vars)
        handle.close()


#         cfo = imp.load_source('pycfg',filename,handle)
        for opt_name, opt_value in vars.iteritems():
            if opt_name[0] == '-': continue
            opt_longname = '--'+opt_name
            if not parser.has_option(opt_longname): continue

#             value = getattr(cfo,opt_name)

            o = parser.get_option(opt_longname)
            o.default = opt_value
            parser.defaults[opt_name] = opt_value

            print ' - new default value:',opt_name,'=',opt_value
        return


    if not os.path.exists(rc):
        print rc,'not found'
        return

    f = open(rc)
    for line in f:
        if line[0] == '#':
            continue
        tokens = line.split(':')
        if len(tokens) < 2:
            continue
        opt_name = tokens[0]
        opt_longname = '--'+tokens[0]
        if parser.has_option(opt_longname):
            strval = line[line.index(':')+1:-1]
            value = eval(strval)
            o = parser.get_option(opt_longname)
            o.default = value
            parser.defaults[opt_name] = value

            print ' - new default value:',opt_name,'=',value

class list_maker:
    def __init__(self, var ):
        self._var = var

    def __call__(self,option, opt_str, value, parser):
        if not hasattr(parser.values,self._var):
               setattr(parser.values,self._var,[])

        try:
           array = value.split(',')
           setattr(parser.values, self._var, array)

        except:
                   print 'Malformed option (comma separated list expected):',value


# def make_cat_list(option, opt_str, value, parser):

#     if not hasattr(parser.values,'cats'):
#         setattr(parser.values,'cats',[])

#     try:
#         cats = value.split(',')
#         parser.values.cats = cats

#     except:
#         print 'Malformed option (comma separated list expected):',value


def addOptions(parser):
    parser.add_option('-l' , '--lumi'     , dest='lumi'     , type='float'    , help='Luminosity'                  , default=None)
    parser.add_option('-v' , '--variable' , dest='variable' , help='variable' , default=None)
    parser.add_option('-m' , '--mass'     , dest='mass'     , type='int'      , help='run on one mass point only ' , default=0)
    parser.add_option('-d' , '--debug'    , dest='debug'    , action='count'  , help='Debug level'                 , default=0)
    parser.add_option('-c' , '--chans'    , dest='chans'    , type='string'   , action='callback'                  , callback=list_maker('chans') , help='list of channels' , default=['0j'])
