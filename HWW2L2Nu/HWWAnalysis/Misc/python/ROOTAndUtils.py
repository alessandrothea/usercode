import ROOT

class TH1AddDirSentry:
    def __init__(self):
        self.status = ROOT.TH1.AddDirectoryStatus()
        ROOT.TH1.AddDirectory(False)
        
    def __del__(self):
        ROOT.TH1.AddDirectory(self.status)

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
