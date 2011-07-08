import csv

from HWWAnalysis.Misc.dataset import GDataset

class CSVDatasetReader:
    def __init__(self, path ):
        self._path = path

    def read(self, manager):
        csvFile = open(self._path)
        stuffReader = csv.reader( csvFile, delimiter=',')
        columns = stuffReader.next()
        if not 'uid' in columns:
            raise ValueError('Unique id not defined in '+self._path)

        print columns
        manager._columns = columns[:]
        for i,row in enumerate(stuffReader):
            ds = dict(zip(columns,row))
            gds = GDataset()
            gds._fields = ds
            manager.add(i,gds)

        csvFile.close()


