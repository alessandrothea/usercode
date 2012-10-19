#!/usr/bin/env python

import os
import optparse
import sys
import hwwinfo
import hwwsamples
import hwwtools
import ROOT

from HWWAnalysis.Misc.ROOTAndUtils import TH1AddDirSentry


if __name__ == '__main__':
    usage = 'usage: %prog [options]'
    parser = optparse.OptionParser(usage)
    parser.add_option('-i','--input'     , dest='input'          , help='Input Path for the source histograms'       , default=None)
    parser.add_option('-N','--Ntoys'     , dest='ntoys'          , help='Number of toys'       , type='int', default=1)

    hwwtools.addOptions(parser)
    hwwtools.loadOptDefaults(parser)
    (opt, args) = parser.parse_args()

    sys.argv.append( '-b' )
    ROOT.gROOT.SetBatch()

    if not opt.debug:
        pass
    elif opt.debug == 2:
        print 'Logging level set to DEBUG (%d)' % opt.debug
        logging.basicConfig(level=logging.DEBUG)
    elif opt.debug == 1:
        print 'Logging level set to INFO (%d)' % opt.debug
        logging.basicConfig(level=logging.INFO)


    siname = 'hww-{lumi:.2f}fb.mH{mass}.{channel}_shape'
    masses = [m for m in hwwinfo.masses if m <= 250] if opt.mass == 0 else [opt.mass]

    dcdir = opt.input+'/datacards'
    shdir = dcdir+'/shapes'

    for k in xrange(opt.ntoys):
        toypath = 'toys/instance_%d/' % k
        toydcpath = toypath+'datacards'
        toyshpath = toypath+'datacards/shapes'

        hwwtools.ensuredir( toydcpath )
        hwwtools.ensuredir( toydcpath+'/pseudo' )
        if os.path.exists(toyshpath):
            os.unlink(toyshpath)
        os.symlink(os.path.abspath(shdir),toyshpath)
        rndm = ROOT.TRandom3()

        for chan in opt.chans:
            for mass in masses:
                print chan, mass

                basename = siname.format(lumi=opt.lumi, mass=mass, channel=chan)
                dcpath  = os.path.join(dcdir,basename+'.txt')
                shpath = os.path.join(shdir,basename+'.root')
    #             print os.path.exists(dcpath),dcpath
    #             print os.path.exists(shpath),shpath

                fsh = ROOT.TFile.Open(shpath)
                data_si = fsh.Get('histo_Data')
                if not data_si.__nonzero__():
                    fsh.Close()
                    raise ValueError('cant\'t find histo_data')
                print 'histo_Data',data_si.GetEntries(),data_si.Integral()
                sentry = TH1AddDirSentry()

                data_toy = data_si.Clone('histo_Toy')
                data_toy.Reset()

                toyentries = rndm.Poisson(data_si.GetEntries())
                print 'Filling the toy with',toyentries,'entries'
                
                data_toy.FillRandom(data_si,toyentries)

                newshpath = os.path.join(toydcpath+'/pseudo',basename+'.root')
                newfsh = ROOT.TFile.Open(newshpath,'recreate')
                data_toy.SetDirectory(newfsh)
                newfsh.Write()
                newfsh.Close()

                newdcpath = os.path.join(toydcpath,basename+'.txt')
                newdc = open(newdcpath,'w')

                dc = open(dcpath,'r')
                for line in dc:
                    if line.startswith('shapes  data_obs'):
                        line = line.replace('shapes/','pseudo/')
                        line = line.replace('histo_Data','histo_Toy')

                    if line.startswith('observation'):
                        line = 'observation %d\n' % toyentries
                    newdc.write(line)

                dc.close()
                newdc.close()

                del sentry
            
