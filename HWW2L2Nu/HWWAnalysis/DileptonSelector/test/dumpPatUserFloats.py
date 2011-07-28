#!/usr/bin/env python
import ROOT
import DataFormats.FWLite as fwlite #import Events, Handle
import sys
import optparse


def dumpTheFloat( fileName, variables ):
    events = fwlite.Events( fileName )

    # create handleEl outside of loop
    handleEl  = fwlite.Handle ('std::vector<pat::Electron>')
    handleMu  = fwlite.Handle ('std::vector<pat::Muon>')

    # a label is just a tuple of strings that is initialized just
    # like and edm::InputTag
    labelEl = ("boostedElectrons")
    labelMu = ("boostedMuons")


    if len(variables)==0:
        elDone = False
        muDone = False
        for event in events:
            event.getByLabel(labelEl,handleEl)
            event.getByLabel(labelMu,handleMu)

            electrons = handleEl.product()
            muons = handleMu.product()
#             print len(electrons)
#             print len(muons)
            hline = '-'*80
            if not elDone:
                for e in electrons:
                    print hline
                    names = e.userFloatNames()

                    for name in names:
                        print name, e.userFloat(name)

                    print hline
                    for elId in e.electronIDs():
                        print elId.first, elId.second

                    elDone = True
                    break

            if not muDone: 
                for m in muons:
                    print hline
                    names = m.userFloatNames()

                    for name in names:
                        print name, m.userFloat(name)
                    muDone = True
                    break

            if elDone and muDone:
                break;
    else:
        print '|'.join([v.ljust(20) for v in variables])
        for event in events:
            event.getByLabel(labelEl,handleEl)
            event.getByLabel(labelMu,handleMu)

            electrons = handleEl.product()
            muons = handleMu.product()
            for e in electrons:
                names = e.userFloatNames()
                for v in variables:
                    if not v in names:
                        raise RuntimeError(v+" not found!")
                print '|','| '.join([str(e.userFloat(v)).ljust(20) for v in variables])

if __name__ == '__main__':


    usage = 'usage: %prog [options]'
    parser = optparse.OptionParser(usage)

    parser.add_option('-v', '--varlist', dest='varlist', help='variables', default='' )
    (opt, args) = parser.parse_args()

    sys.argv.append('-b')
    ROOT.gROOT.SetBatch()        # don't pop up canvases

    fileName = args[0]

    variables = opt.varlist.split(',') if opt.varlist != '' else []
    
    print len(variables),'aa'
    dumpTheFloat( fileName, variables )

