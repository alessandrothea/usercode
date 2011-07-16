import gdata  
import gdata.docs  
import gdata.spreadsheet  
import gdata.spreadsheet.service  

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
