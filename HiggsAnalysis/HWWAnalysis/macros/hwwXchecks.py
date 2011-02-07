# from ROOT import TChain, TCanvas, gSystem, TH1F
import ROOT

ROOT.gSystem.Load('lib/libHWWNtuple.so')
# from ROOT import HWWNtuple

tree = ROOT.TChain('hwwSkim')
tree.AddFile('output/ZJets-skimmed.root')

c = ROOT.TCanvas("c1","c1", 800, 800)
c.Divide(2,3)
c.cd(1)

#etaCut = 'TMath::Abs(ev.Els.ElP.Eta()) <'+str(1.442)
#tree.Draw('ev.Els.ElSigmaIetaIeta',etaCut)
#c.cd(2)
#tree.Draw('ev.Els.ElP.Eta()','ev.Els.ElSigmaIetaIeta < 0.01')
#c.cd(3)
#tree.Draw('ev.Els.ElP.Eta()','ev.Els.ElSigmaIetaIeta > 0.01')
#c.cd(4)
#tree.Draw('ev.Els.ElP.Eta():ev.Els.ElSigmaIetaIeta')
#c.cd(5)
#tree.Draw('(ev->Els[0].ElP+ev->Els[1].ElP).Mag()');

# tree.Draw('ev.Els.ElDeltaPhiSuperClusterAtVtx',etaCut)
# c.cd(3)
# tree.Draw('ev.Els.ElDeltaPhiSuperClusterAtVtx',etaCut)
# c.cd(4)
# tree.Draw('ev.Els.ElNumberOfMissingInnerHits',etaCut)

eemass = ROOT.TH1F('eemass','eemass', 100, 10.,300.)

ev = ROOT.HWWNtuple()
tree.SetBranchAddress('ev', ROOT.AddressOf(ev))

tree.GetEntry(0);
print tree.GetEntriesFast()
for i in range( tree.GetEntriesFast() ):
    tree.GetEntry(i);
    if ev.NEles == 2:
        mass = (ev.Els[0].ElP+ev.Els[1].ElP).Mag()
        eemass.Fill(mass)


eemass.Draw()
