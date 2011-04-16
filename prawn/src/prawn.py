'''
Created on Apr 10, 2011

@author: ale
'''

import optparse

def prawn():
    pass

class PrawnOptionParser( optparse.OptionParser ):
    def __init__(self):
        optparse.OptionParser.__init__(self, conflict_handler='resolve', usage='%prog --help or %prog --comand [options]')

if __name__ == "__main__":
    prawn()