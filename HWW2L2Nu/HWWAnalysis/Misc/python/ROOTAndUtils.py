import ROOT

#----
import sys

class Tee(object):
    def __init__(self, name, mode='w'):
        self.file = open(name, mode)
        self.stdout = sys.stdout
        sys.stdout = self

    def __del__(self):
        self.file.close()
        del self.stdout

    def write(self, data):
        self.file.write(data)
        self.stdout.write(data)

    def flush(self):
        self.file.flush()
        self.stdout.flush()
#---
class TH1AddDirSentry:
    def __init__(self, status=False):
        self.status = ROOT.TH1.AddDirectoryStatus()
        ROOT.TH1.AddDirectory(status)

    def __del__(self):
        ROOT.TH1.AddDirectory(self.status)

    def __enter__(self):
        return self

    def __exit__(self, type, value, tb):
        self.__del__()
#---
class TH1Sumw2Sentry:
    def __init__(self,sumw2=True):
        self.status = ROOT.TH1.GetDefaultSumw2()
        ROOT.TH1.SetDefaultSumw2(sumw2)

    def __del__(self):
        ROOT.TH1.SetDefaultSumw2(self.status)

    def __enter__(self, type, value, tb):
        return self

    def __exit__(self):
        self.__del__()

#---
class TStyleSentry:
    def __init__(self, style):

        if isinstance(style,str):
            style = ROOT.gROOT.GetStyle(style)
        elif not isinstance(style,ROOT.TStyle):
            raise TypeError('TStyleSentry needs a TStyle')
        # use TROOT.GetStyle to get a reference to the TStyle
        # ROOT.gStyle would return a reference to TStyle*
        self._oldstyle = ROOT.gROOT.GetStyle(ROOT.gStyle.GetName())
        style.cd()

    def __del__(self):
        # restore the old style
        self._oldstyle.cd()

    def __enter__(self):
        return self

    def __exit__(self, type, value, tb):
        self.__del__()

# ---
class PadPrinter(object):
    _tcanvas_winframe_width  = 4
    _tcanvas_winframe_height = 28

    # ---
    def __init__(self,prefix='',types=['pdf','png']):
        self.prefix = prefix
        self.types  = types

    # ---
    def saveas(self, pad, filename):

        oldpad = ROOT.gPad.func()
        ww = int(pad.GetWNDC()*pad.GetWw())
        wh = int(pad.GetHNDC()*pad.GetWh())

        nm = '%s_%s' % (filename,pad.GetName())

        c = ROOT.TCanvas(nm, nm, ww+self._tcanvas_winframe_width, wh+self._tcanvas_winframe_height)
        c.cd()

        newpad = pad.DrawClone()
        newpad.SetPad(0,0,1,1)

        for ext in self.types:
            c.Print('%s/%s.%s' % (self.prefix,filename,ext))

        oldpad.cd()

    # ---
    def saveall(self, **pads):

        for filename,pad in pads.iteritems():
            self.saveas(pad,filename)

    # ---
    def savefromcanvas(self, canvas, **pads):
        # waiting for python 2.7
        #args = {n:canvas.GetPad(i) for n,i in pads.iteritems()}
        args = dict( [ (n,canvas.GetPad(i)) for n,i in pads.iteritems() ] )

        self.saveall(**args)

    __call__ = saveall


# ---
def openROOTFile(path, option=''):
    f =  ROOT.TFile.Open(path,option)
    if not f.__nonzero__() or not f.IsOpen():
        raise NameError('File '+path+' not open')
    return f

# ---
def getROOTObj(d,name):
    o = d.Get(name)
    if not o.__nonzero__():
        raise NameError('Object '+name+' doesn\'t exist in '+d.GetName())
    return o

# ---
def ROOTInheritsFrom( objClass, theClass ):
    c = ROOT.gROOT.GetClass(objClass)
    return c.InheritsFrom(theClass)

class ObjFinder:
    def __init__(self, classname):
        self.classname = classname

    def find(self, rootFile ):
        if not rootFile.__nonzero__() or not rootFile.IsOpen():
            raise ValueError('ROOTFile '+rootFile.GetName()+' is not valid')
        return self.findRecursive( rootFile )

    def findRecursive( self, dir ):
        keys = dir.GetListOfKeys();
        dirname = dir.GetName()+'/' if not ROOTInheritsFrom(dir.IsA().GetName(),'TFile') else ''

        subdirs = [d.ReadObj() for d in filter( lambda key: ROOTInheritsFrom(key.GetClassName(),'TDirectoryFile'), keys) ]
        paths   = [ dirname+obj.GetName() for obj in filter( lambda key:ROOTInheritsFrom( key.GetClassName(),self.classname), keys) ]
        for d in subdirs:
            paths.extend( [dirname+p for p in self.findRecursive(d)] )
        return paths

    def tree(self, rootFile):
        if not rootFile.__nonzero__() or not rootFile.IsOpen():
            raise ValueError('ROOTFile '+rootFile.GetName()+' is not valid')
        return self.treeRecursive( rootFile )

    def treeRecursive( self, dir ):
        keys = dir.GetListOfKeys();
        fullname = dir.GetPath()
        fullname = fullname[fullname.index(':')+1:]
#         dirname = fullname+'/' if not ROOTInheritsFrom(dir.IsA().GetName(),'TFile') else ''
        dirname = fullname+'/' if fullname != '/' else '/'
        print fullname

        subdirs = [d.ReadObj() for d in filter( lambda key: ROOTInheritsFrom(key.GetClassName(),'TDirectoryFile'), keys) ]
        paths   = [dirname+obj.GetName() for obj in filter( lambda key:ROOTInheritsFrom( key.GetClassName(),self.classname), keys) ]

        branch = []

        for d in subdirs:
            branch.append( (dirname+d.GetName(), self.treeRecursive(d)) )

        branch.extend( paths )
        return branch



class BlankCommentFile:
    def __init__(self, fp):
        self.fp = fp

    def __iter__(self):
        return self

    def next(self):
        line = self.fp.next().strip()
        if not line or line.startswith('#'):
            return self.next()
        return line
