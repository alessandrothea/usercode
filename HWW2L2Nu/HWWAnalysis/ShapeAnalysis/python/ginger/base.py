#______________________________________________________________________________
class Labelled(object):
    ''' Generic base classes for objects which have a latex/tlatex representation'''
    def __init__(self,name,title=None,latex=None,tlatex=None):
        self.name    = name
        self._title  = title
        self._latex  = latex
        self._tlatex = tlatex

    #---
    def __str__(self):
        s = [self.name]
        if self._title: s.append(self._title)
        return self.__class__.__name__+'('+', '.join(s)+')'
    
    #---
    def __repr__(self):
        return '%s(%s)' % (self.__class__.__name__,self.name)

    #---
    def _getbyorder(self,attrs):
        for x in attrs:
            if getattr(self,x): return getattr(self,x)

    def __getattr__(self,key):
        if key=='title': 
            return self._getbyorder(['_title','name'])
        elif key == 'latex':
            return self._getbyorder(['_latex','_title','name'])
        elif key == 'tlatex':
            return self._getbyorder(['_tlatex','_title','name'])
        else:
            raise AttributeError('%s instance has no attribute \'%s\'' % (self.__class__.__name__,key) )

    def __setattr__(self,key,val):
        if key in ['title','latex','tlatex']:
            self.__dict__['_'+key] = val
        else:
            self.__dict__[key] = val

    #---
    def getTLatex(self):
        return ROOT.TLatex(0.,0.,self.tlatex)
