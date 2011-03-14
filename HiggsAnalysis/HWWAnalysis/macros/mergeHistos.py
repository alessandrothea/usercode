#!/usr/bin/env python
import sys

def GetLabels(iter):
    iter.Reset()
    labels = []
    labelObj = iter.Next();
    while labelObj:
        labels.append(labelObj.GetName())
        labelObj = iter.Next()
    return labels    
 
 
def testMerge():
    import ROOT
    lA = ['a','b','c','d']
    lB = ['x','e','f','g','h']
    
    hA = ROOT.TH1F('h1','h1',len(lA),0,len(lA))
    hB = ROOT.TH1F('h2','h2',len(lB),0,len(lB))

    for i in range(len(lA)):   
        hA.GetXaxis().SetBinLabel(i+1,lA[i])
    for i in range(len(lB)):   
        hB.GetXaxis().SetBinLabel(i+1,lB[i])

    hA.Fill(0)
    hB.Fill(0)

    hB.Fill(1)
    hB.Fill(3)

    list = ROOT.THashList()
    list.Add(hB)
    list.Add(hA)
    
    print hB,hA
    #check for matching
    nBinsB = hB.GetNbinsX()
    nBinsA = hA.GetNbinsX()
    
    cB = hB.GetBinContent(1)
    cA = hA.GetBinContent(nBinsA)
    
    print 'Bins',cB,cA
    
    labelsListB = hB.GetXaxis().GetLabels()
    labelsListA = hA.GetXaxis().GetLabels()
    labelsB = GetLabels(ROOT.TIter(labelsListB))
    labelsA = GetLabels(ROOT.TIter(labelsListA))
    
#    print labelsB
    nBins3 = nBinsB+nBinsA-1
    h3 = ROOT.TH1F('h3','h3',nBins3,0,nBins3)
    labels3 = labelsA[:]
    labels3.extend(labelsB[1:])
    print labels3
    for i in range(len(labels3)):
        h3.GetXaxis().SetBinLabel(i+1,labels3[i])

    h3.Reset()
#    print h3
#    c = ROOT.TCanvas('c','c')
    h3.Merge(list)
    h3.Draw()
    return h3
    
def mergeHists( path ):
  
    f = ROOT.TFile(path)
    
    dir='lepSelection'
    fStates = ['ll','ee','em','mm']
    
    for s in fStates:
        print '\n-',s+'Counters'
        hName = s+'Counters'
        hB = f.Get(hName)
        hA = f.Get(dir+'/'+hName)
        
        list = ROOT.THashList()
        list.Add(hB)
        list.Add(hA)
        
        print hB,hA
        #check for matching
        nBinsB = hB.GetNbinsX()
        nBinsA = hA.GetNbinsX()
        
        cB = hB.GetBinContent(1)
        cA = hA.GetBinContent(nBinsA)
        
        print 'Bins',cB,cA
        
        labelsListB = hB.GetXaxis().GetLabels()
        labelsListA = hA.GetXaxis().GetLabels()
        labelsB = GetLabels(ROOT.TIter(labelsListB))
        labelsA = GetLabels(ROOT.TIter(labelsListA))
        
#        print labelsB
        nBins3 = nBinsB+nBinsA-1
        h3 = ROOT.TH1F('h3'+s,'h3'+s,nBins3,0,nBins3)
        labels3 = labelsA[:]
        labels3.extend(labelsB[1:])
        print labels3
        for i in range(len(labels3)):
            h3.GetXaxis().SetBinLabel(i+1,labels3[i])

        h3.Reset()
#        print h3
        c = ROOT.TCanvas('c'+s,'c'+s)
        h3.Merge(list)
        h3.Draw()
        c.SetLogy()
        c.Print('c'+s+'.pdf')
        

#        print GetLabels(ROOT.TIter(labelsB))
#        print GetLabels(ROOT.TIter(labelsA))

if __name__ == "__main__":
    args = sys.argv[:]
    sys.argv.append( '-b' )
    import ROOT
    ROOT.gROOT.SetBatch()
    
    if len(args) is not 2:
        print '   Usage: selectEff <path>'
        sys.exit(0)
        
    ROOT.gSystem.Load('lib/libHWWNtuple.so')
  
    mergeHists(path)