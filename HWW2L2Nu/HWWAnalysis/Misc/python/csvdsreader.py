import csv
import os.path

from HWWAnalysis.Misc.dataset import GDataset, GDatasetList

class CSVDatasetReader:
    def __init__(self, path ):
        self._path = path if path[-1] == '/' else path + '/'
        self._exts = ['csv']

    def worksheets(self):
        ls = os.listdir(self._path)
#         fileList = [os.path.join(directory, f) 
#                     for f in fileList
#                     if os.path.splitext(f)[1] in fileExtList]
        
        return [ f for f in ls if os.path.splitext(f)[1] in self._exts]

    def read(self, wsname):
        ext = os.path.splitext(wsname)[1]
        if ext == '':
            label = wsname
            csvFileName = wsname+'.csv'
        elif ext in self._exts:
            label = wsname[:-len(ext)]
            csvFileName = wsname
        else:
            raise ValueError('Filetype '+ext+' not supported ('+wsname+')')


        csvFile = open(self._path+csvFileName)
        stuffReader = csv.reader( csvFile, delimiter=',')
        columns = stuffReader.next()
        if not 'uid' in columns:
            raise ValueError('Unique id not defined in '+self._path)

        print columns
        list = GDatasetList(label)
        list._columns = columns[:]
        for i,row in enumerate(stuffReader):
            ds = dict(zip(columns,row))
            gds = GDataset()
            gds._fields = ds
            list.add(i,gds)

        csvFile.close()
        return list


