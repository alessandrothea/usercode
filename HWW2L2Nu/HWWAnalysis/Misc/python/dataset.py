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

class GDatasetList:
    def __init__(self, label):
        self.label          = label
        self._columns       = []
        self._datasets      = []
        self._datasetsByRow = {}
        self._datasetsByUid = {}
        self._datasetsByNick = {}

    def add(self, row, gds ):

        if len(self._columns) == 0:
            raise RuntimeError('No columns defined')

        self._datasets.append(gds)
        self._datasetsByRow[row] = gds
        self._datasetsByUid[gds['uid']] = gds
        if 'nick' in self._columns:
            self._datasetsByNick[gds['nick']] = gds
        
    def findByNick(self,nick):
        if not nick in self._datasetsByNick.iterkeys():
            return None
        return self._datasetsByNick[nick]

    def findByUid(self,uid):
        if not uid in _datasetsByUid.iterkeys():
            return None
        return _datasetsByUid[uid]

    def findByRow(self, row):
        return self._datasetsByRow[row]

    def iterdatasets(self):
        return iter(self._datasets)

    def pprint(self):
        print 'Displaying',len(self._datasets),'datasets'
        rows = []
        rows.append(self._columns[:])
        for ds in self._datasets:
            row = [ str(ds[col]) for col in self._columns ]
            rows.append(row)

        widths = [ max([ len(rows[i][j]) for i in range(len(rows))]) for j in range(len(self._columns))]
        for row in rows:
            print ' | '.join( [ row[i].ljust(widths[i]) for i in range(len(widths))] )


