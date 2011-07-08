import sys
import csv

from HWWAnalysis.Misc.dataset import GDataset

class GDatasetManager:
    def __init__(self):
        self._columns       = []
        self._datasets      = []
        self._datasetsByRow = {}
        self._datasetsByUid = {}
        self._datasetsByNick = {}

#     def downloadTabList(self):
#         spreadsheet_feed = self._client.GetFeed( self.feedUrl() )
#         tabList = [ entry.title.text  for (i,entry) in enumerate(spreadsheet_feed.entry) ]
#         return tabList

    def load(self,reader):
        reader.read(self)

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

    def dumpCSV(self, path):
        csvFile = open(path, 'wb')
        stuffWriter =  csv.writer(csvFile, delimiter=',',quotechar='|', quoting=csv.QUOTE_MINIMAL)
        rows = []
        rows.append(self._columns[:])
        for ds in self._datasets:
            row = [ ds[col] for col in self._columns ]
            rows.append(row)

        stuffWriter.writerows(rows)
        csvFile.close()

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


