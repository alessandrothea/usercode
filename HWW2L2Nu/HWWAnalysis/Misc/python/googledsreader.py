import gdata  
import gdata.docs  
import gdata.spreadsheet  
import gdata.spreadsheet.service  
import HWWAnalysis.Misc.odict as odict

from HWWAnalysis.Misc.dataset import GDataset

defaultWSKey = '0AmbqMj_rTADpdEZWRnU1TjZ5N3AtdVFqb0tMVUpqb1E'

class GoogleDatasetCellReader:
    '''GoogleDatasetCellReader'''
    def __init__(self,tab):
        self._tab     = tab
        self._client  = gdata.spreadsheet.service.SpreadsheetsService()  
        self._skey    = defaultWSKey

    def feedUrl(self):
        return 'https://spreadsheet.google.com/feeds/worksheets/'+self._skey+'/public/values'

    def read(self, manager):
        spreadsheet_feed = self._client.GetFeed( self.feedUrl() )
        tabList = [ entry.title.text  for (i,entry) in enumerate(spreadsheet_feed.entry) ]
        try:
            tabIndex = tabList.index(self._tab)
        except:
            return None

        ws_entry = spreadsheet_feed.entry[tabIndex]  
        wskey = ws_entry.id.text.rsplit('/')[-1]  

        # can be retrieved from the entry itself
        ws_feedurl = 'https://spreadsheet.google.com/feeds/cells/'+self._skey+'/'+wskey+'/public/values'

        cell_feed = self._client.GetFeed(ws_feedurl)  

        # scan the table, find max col and max row
        cols = set()
        rows = set()
        for entry in cell_feed.entry:
            element = entry.extension_elements[0]
            c = int(element.attributes['col'])
            r = int(element.attributes['row'])
            cols.add(c)
            rows.add(r)

        ncols = max(cols)
        nrows = max(rows)
        # build an empty table
        table = [[None]*ncols for i in xrange(nrows)]
 
        # reloop to fill
        for entry in cell_feed.entry:
            element = entry.extension_elements[0]

            c = int(element.attributes['col'])
            r = int(element.attributes['row'])

#             print r-1,c-1,element.text
            table[r-1][c-1] = element.text

        # the header is the first row. This might change
        columns = table.pop(0)
        if not 'uid' in columns or not 'nevents' in columns:
            raise RuntimeError('The columns uid and nevents are required. Add them to the table')
        manager._columns = columns
#         header = odict.OrderedDict(zip(hrow,range(len(hrow))))
        header = dict(enumerate(columns))

        for r,row in enumerate(table):
            ds = {}
            for c,cell in enumerate(row):
                ds[header[c]] = cell
            
            print ds
            if not ds['uid'] or not ds['nevents']:
                # skip rows with not uid or no nEvents
                continue
            gds = GDataset()
            gds._fields = ds
            manager.add(r,gds)


        # find the header somehow
#         print header
#         print len(table),len(table[0]),'---',' '.join(table[0])

#         print table
#         print 'r:',max(rows),rows
#         print 'c:',max(cols),cols
            
#         for i, entry in enumerate(cell_feed.entry):
# #             print entry
#             print entry.title.text,
#             print len(entry.extension_elements),
#             for (j,elem) in enumerate(entry.extension_elements):
#                 print j,elem.tag, elem.attributes['row'], elem.attributes['col'], elem.text
        # to be continued
 
class GoogleDatasetReader:
    '''GoogleDatasetReader'''
    def __init__(self, tab):
        self._tab     = tab
        self._client  = gdata.spreadsheet.service.SpreadsheetsService()  
        self._skey    = defaultWSKey
    
    def feedUrl(self):
        return 'https://spreadsheet.google.com/feeds/worksheets/'+self._skey+'/public/values'

    def read(self, manager):
        spreadsheet_feed = self._client.GetFeed( self.feedUrl() )
        tabList = [ entry.title.text  for (i,entry) in enumerate(spreadsheet_feed.entry) ]
        try:
            tabIndex = tabList.index(self._tab)
        except:
            return None

        ws_entry = spreadsheet_feed.entry[tabIndex]  
        wskey = ws_entry.id.text.rsplit('/')[-1]  
        
        ws_feedurl = 'https://spreadsheet.google.com/feeds/list/'+self._skey+'/'+wskey+'/public/values'

        worksheets_feed = self._client.GetFeed(ws_feedurl)  

        dsList = {}
        # check for non
        header = {}
        # remember the order
        for i, entry in enumerate(worksheets_feed.entry):
            ds = {}
            columnId = 0
            for (j,elem) in enumerate(entry.extension_elements):
                if elem.tag[0] == '_':
                    continue

                ds[ elem.tag ] = elem.text if elem.text else ''

                if not elem.tag in header.iterkeys():
                    header[elem.tag] = columnId
                    manager._columns.append(elem.tag)
                elif columnId != header[elem.tag]:
                    raise ValueError('Corrupted Table: tag/column '+elem.tag+' index mismatch! j = '+str(columnId)+' header[tag] = '+str(header[elem.tag])+'. Missing column name' )
                
                # increase the counter
                columnId += 1

            if not 'uid' in ds.iterkeys():
                raise ValueError('Unique id not defined for in row '+str(i))
            gds = GDataset()
            gds._fields = ds
            manager.add(i,gds)
