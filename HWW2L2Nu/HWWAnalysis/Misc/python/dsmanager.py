import sys
import csv

from HWWAnalysis.Misc.dataset import *
from HWWAnalysis.Misc.googledsreader import *
from HWWAnalysis.Misc.csvdsreader import *


class GDatasetManager:
    def __init__(self, csvpath='.', gkey=None):
        self._lists = {}
        self._csvpath = csvpath
        self._gkey    = gkey


#     def downloadTabList(self):
#         spreadsheet_feed = self._client.GetFeed( self.feedUrl() )
#         tabList = [ entry.title.text  for (i,entry) in enumerate(spreadsheet_feed.entry) ]
#         return tabList

    def load(self, id ):
        googleTag = 'google:'
        csvTag = 'csv:'
        if id.startswith(googleTag):
            wsname = id[len(googleTag):]
            reader = GoogleDatasetCellReader()
            dslist =  reader.read(wsname)
            self._lists[dslist.label] = dslist

        elif id.startswith(csvTag):
            fname = id[len(csvTag):]
            reader = CSVDatasetReader( path = self._csvpath )
            dslist = reader.read(fname)
            self._lists[dslist.label] = dslist
        else:
            raise ValueError('id '+id+' not supported')
        return dslist

    def _dump(self,list, path):
        csvFile = open(path, 'wb')
        stuffWriter =  csv.writer(csvFile, delimiter=',',quotechar='|', quoting=csv.QUOTE_MINIMAL)
        rows = []
        rows.append(list._columns[:])
        for ds in list._datasets:
            row = [ ds[col] for col in list._columns ]
            rows.append(row)

        stuffWriter.writerows(rows)
        csvFile.close()

    def dumpCSV(self, label, path=None):
        if not label in self._lists:
            return label+'not found'
        if not path:
            path = label+'.csv'
        
        list = self._lists[label]
        self._dump(list, path)

    def dumpAllCSV(self, path = ''):
        for (label,list) in self._lists.iteritems():
            self._dump(list,path+label+'.csv')



