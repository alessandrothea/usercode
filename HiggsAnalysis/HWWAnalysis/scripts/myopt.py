from string import lstrip
from sys import exit 
import re

def str2bool(s):
    if s is True or s is False:
        return s
    s = str(s).strip().lower()
    return not s in ['false','f','n','0','']

class option:

    def __init__(self,names,val=None,help=''):
        if( type(names) == tuple ):
            self.init(names[0],names[1],names[2])
        else:
            self.init(names,val,help)
            
    def init(self,names,val,help):
        self.names = [ n for n in names.split(',') ]
        if( type(val) == type ):
            self.val=val('')
        else:
            self.val   = val
        self.help=help

    def parse(self,val):    
        if type(self.val) == bool:
            self.val=str2bool(val)
        else:
            self.val=type(self.val)(val)

    def __str__(self):
        st=""
        for n in self.names:
            st += n+" "
        st += str(self.val) + " " + str(self.help)
        return st

class options:
    map={}
    opts=[]
    name=""
    
    def __init__(self,opts):
        self.sec_reg = re.compile("\[(.*)\]")
        self.com_reg = re.compile("#.*$")
        self.param_reg = re.compile("([^=]*)=(.*)")
        for o in opts:
            ## print o
            opt=option(o)
            self.opts.append(opt)
            for n in opt.names:
                self.map[n]=opt

    def parse(self,args):
        a=iter(args)
        self.ename=args[0]
        a.next()
        while a:
            try:
                v=a.next()
                if( v.startswith('-') ):
                    key=lstrip(v,'-')
                    if( key == 'help' ):
                        self.help(self.name)
                    val = a.next()    
                    if( self.map.has_key(key) ):
                        o=self.map[key]
                        o.parse(val)
                else:
                    try:
                        f = open(v,'r')
                        self.parseFile(f)
                    except IOError:
                        f = None

            except StopIteration:
                break  

    def parseFile(self,fd):
        # read all lines removing comments
        lines = [ l.strip() for l in fd.read().split('\n') if re.sub(self.com_reg,"",l) != "" ]
        
        curopt = None
        curval = "" 
        for line in lines:
            print line
            search = self.param_reg.search(line)
            if search:
                if( curopt ): ## parse last option
                    curopt.parse(curval)
                key = search.groups()[0].strip()
                if( self.map.has_key(key) ):
                    curopt = self.map[key]
                    curval = search.groups()[1].strip().strip('"')
            elif curopt:
                curval += ","+line.strip().strip('"')
                
        if( curopt ): ## parse last option
            curopt.parse(curval)

    def dump(self):
        print str(self)
        ## print "------------------------------------------------------------"
        ## for op in self.opts:
        ##     print op.names[0].ljust(22)+"  ="+str(op.val).rjust(35)

    def help(self,name):
        print "usage: "+name+" [options]"
        print "options:"
        for o in self.opts:
            names = "" 
            # print "\t",
            for n in o.names:
                names += ("-"+n+" ").ljust(10)
            print "    "+names.ljust(20)+"   "+o.help.ljust(55)+("   ["+str(o.val)+"]").ljust(30)    
            ## print "\t: "+o.help
        print
        exit()


    def __getitem__(self,key):
        return self.map[key] 
    
    def __getattr__(self,name):
        return self.map[name].val

    def __str__(self):
        ret  = "------------------------------------------------------------\n"
        ret += "---" + self.name
        ret += "------------------------------------------------------------\n"
        for op in self.opts:
            ret += op.names[0].ljust(22)+"  ="+str(op.val).rjust(35)+"\n"
        return ret    
