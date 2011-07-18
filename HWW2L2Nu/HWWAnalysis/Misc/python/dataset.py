class GDataset:
    def __init__(self):
        self._fields = {}
        pass

    def __getitem__(self,key):
        return self._fields.__getitem__(key)

    def __setitem__(self,key,value):
        self._fields.__setitem__(key,value)

    def __str__(self):

        theStr = 'Dataset '+self._fields['uid']+'\n' 
        for (key,val) in self._fields.iteritems():
            theStr += '   '+key+' '+str(val)+'\n'
        return theStr

