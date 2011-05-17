import ROOT

class TH1AddDirSentry:
    def __init__(self):
        self.status = ROOT.TH1.AddDirectoryStatus()
        ROOT.TH1.AddDirectory(False)
        
    def __del__(self):
        ROOT.TH1.AddDirectory(self.status)

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
