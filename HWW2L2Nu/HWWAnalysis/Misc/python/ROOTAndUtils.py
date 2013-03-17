import ROOT

#---
class TH1AddDirSentry:
    def __init__(self):
        self.status = ROOT.TH1.AddDirectoryStatus()
        ROOT.TH1.AddDirectory(False)
        
    def __del__(self):
        ROOT.TH1.AddDirectory(self.status)
#---
class TH1Sumw2Sentry:
    def __init__(self):
        self.status = ROOT.TH1.GetDefaultSumw2()
        ROOT.TH1.SetDefaultSumw2()

    def __del__(self):
        ROOT.TH1.SetDefaultSumw2(self.status)

def openROOTFile(path, option=''):
    f =  ROOT.TFile.Open(path,option)
    if not f.__nonzero__() or not f.IsOpen():
        raise NameError('File '+path+' not open')
    return f

def getROOTObj(d,name):
    o = d.Get(name)
    if not o.__nonzero__():
        raise NameError('Object '+name+' doesn\'t exist in '+d.GetName())
    return o

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
