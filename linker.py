#! /usr/bin/env python

import re

import allocator

# object information
objectTable = {}

# global symbol table
#globalSymbolTable = {}

class Object(object) :
    'An object file information.'
    # file or archive name, if any
    name = ''
    # # of segments
    nseg = 0
    # # of symbols
    nsym = 0
    # # of relocs
    nrel = 0
    # hash names to segment numbers (below)
    segnames = {}
    # array of segments, index starts with 1
    segs = ['']
    # hash names to symbol numbers
    symnames = {}
    # array of symbols (below), index starts with 1
    syms = ['']
    # array of relocs (below)
    rels = []

    def __init__(self) :
        self.name = ''
        self.nseg = 0
        self.nsym = 0
        self.nrel = 0
        self.segnames = {}
        self.segs = ['']
        self.symnames = {}
        self.syms = ['']
        self.rels = []

class SegmentInfo() :
    'Segment Infomation'
    readable = False
    writable = False
    present = False
    data = ''
    
    def __init__(self, name, segNo, base, length, flags) :
        self.name = name
        self.segNo = segNo
        self.base = int(base, 16)
        self.length = int(length, 16)
        self.setFlags(flags)
        self.data = ''

    def setFlags(self, flags) :
        if 'R' in flags :
            self.readable = True
        if 'W' in flags :
            self.writable = True
        if 'P' in flags :
            self.present = True


class Symbol() :
    'Symbol table entity'
    defined = False

    def __init__(self, name, symNo, value, seg, type) :
        self.name = name
        self.symNo = symNo
        self.value = int(value, 16)
        self.seg = seg
        self.setType(type)

    def setType(self, type) :
        
        if type == 'D' :
            self.defined = True
        elif type == 'U' :
            self.defined = False

class GlobalSymbol(object) :
    'global symbol table entity.'

    def __init__(self, name, module, defined) :
        self.name = name
        self.module = module
        self.defined = defined

class Relocation() :
    'relocation entity'

    def __init__(self, loc, seg, ref, type) :
        self.loc = int(loc, 16)
        self.seg = seg
        self.ref = ref
        self.type = type


class SymbolReloc() :
    'symbol relocation information.'
    def __init__(self, loc, ref) :
        self.loc = loc
        self.ref = ref

def getline (fp) :
    line = fp.readline()
    # checker comment and blank line
    while True :
        m = re.match('\s*#', line)
        n = re.match('\s+', line)
        if m is not None or n is not None:
            line = fp.readline()
        else :
            break

    line = line.strip()
    return line

def readObj (fileName) :
    'read object infomation from file.'
    global objectTable
    fp = open(fileName)
    magicNumber = getline(fp)
    #print magicNumber

    o = Object()

    o.name = fileName
    
    objectTable[o.name] = o
    # read number of segment, number of symbol table entries,
    #+ number of relocation entities.
    s = getline(fp)
    args = s.split()
    o.nseg = int(args[0], 16)
    o.nsym = int(args[1], 16)
    o.nrel = int(args[2], 16)

    #print o.nseg, o.nsym, o.nrel
    # read segsments
    
    for i in range(1, o.nseg + 1) :
        s = getline(fp)
        members = s.split()
        info = SegmentInfo(members[0], i, members[1], members[2], members[3])
        
        o.segnames[info.name] = i
        o.segs.append(info)

    
    # read symbols
    for i in range(1, o.nsym + 1) :
        s = getline(fp)
        members = s.split()
        info = Symbol(members[0], i, members[1], members[2], members[3])
        
        o.symnames[info.name] = i
        o.syms.append(info)


    # read rels
    for i in range(0, o.nrel) :
        s = getline(fp)
        members = s.split()
        info = Relocation(members[0], members[1], members[2], members[3])
        o.rels.append(info)


    # read data
    data = ''
    while True :
        line = getline(fp)
        if line == '' :
            break
        data += line.strip() + ' '

    data = data.strip()
    readData(o, data)

    fp.close()

def readData(obj, data) :
    'read segment data'
    
    for i in range(1, obj.nseg + 1) :
        info = obj.segs[i]
        count = info.length
        if count == 0:
            continue
            
        info.data += data[:(3 * count - 1)] + ' '
        data = data[3 * count:]

    #for key in segmentData :
    #    segmentData[key] = segmentData[key].strip()
    for i in range(1, obj.nseg + 1) :
        obj.segs[i].data = obj.segs[i].data.strip()

def readGlobalSymbol(objectTable) :

    globalSymbolTable = {}
    for key in objectTable :
        module = objectTable[key].name
        syms = objectTable[key].syms

        for i in range(1, len(syms)) :
            symbol = syms[i]

            if symbol.name in globalSymbolTable :
                exist = globalSymbolTable[symbol.name]
                if exist.defined == True and \
                   symbol.defined == True :
                    print '''symbol '%s' redefines''' % (symbol.name)
                elif exist.defined == False and \
                     symbol.defined == True :
                    exist.defined = True
                    exist.module = key

            else :
                globalSymbol = GlobalSymbol(symbol.name, key,
                                            symbol.defined)
                
                globalSymbolTable[symbol.name] = globalSymbol

    # check for undefined symbol
    delElem = []
    for key in globalSymbolTable :
        globalSymbol = globalSymbolTable[key]
        if globalSymbol.defined == False :
            delElem .append(key)
            print '''symbol '%s' undefined''' % (globalSymbol.name)

    for i in range(0, len(delElem)) :
        del globalSymbolTable[delElem[i]]
        
    return globalSymbolTable

# write object file routines
def my_cmp(s1, s2) :
    return cmp(s1.loc, s2.loc)


def writeFile_3_1(fileName) :
    'write result to file. (Project 3.1)'
    fp = open(fileName, 'w')

    for key in segmentTable:
        info = segmentTable[key]
        fp.write(info.name + ' ' + info.base + ' ' + info.length + 
                 ' ' + str(info.readable) + ' ' + str(info.writable) +
                 ' ' + str(info.present) + '\n')


    orderSym = []
    for key in relocation:
        info = relocation[key]
        if info.ref[:3] == 'Sym' :
            symReloc = SymbolReloc(info.loc, info.ref[3:])
            orderSym.append(symReloc)

    orderSym.sort(my_cmp)

    for i in orderSym :
        info = symbolTable[int(i.ref, 16)]
        fp.write(info.name + ' ' + info.value + ' ' + info.seg +
                 ' ' + str(info.defined) + '\n')
                                        
    for key in symbolTable :
        for i in orderSym :
            if key == int(i.ref, 16) :
                break
        else :
            info = symbolTable[key]
            fp.write(info.name + ' ' + info.value + ' ' + info.seg +
                     ' ' + str(info.defined) + '\n')

    for key in relocation:
        info = relocation[key]
        fp.write(info.loc + ' ' + info.seg + ' ' + info.ref +
                 ' ' + info.type + '\n')
        
    fp.close()

def writeFile_4_1(fileName) :
    'write object code to file. (Project 4.1)'
    fp = open(fileName, 'w')

    alloc = allocator.Allocator()
    statistic = alloc.basicAllocator(segmentTable)

    fp.write('.text %x - %x\n' %
             (statistic.textStartAddr, statistic.textEndAddr))
    fp.write('.data %x - %x\n' %
             (statistic.dataStartAddr, statistic.dataEndAddr))
    fp.write('.bss %x - %x\n' %
             (statistic.bssStartAddr, statistic.bssEndAddr))

    fp.close()
    
def writeFile_4_2(fileName) :
    'write object code to file. (Project 4.2)'
    fp = open(fileName, 'w')

    alloc = allocator.Allocator()
    statistic = alloc.commonBlockAllocator(segmentTable, symbolTable)
    fp.write('.text %x - %x\n' %
             (statistic.textStartAddr, statistic.textEndAddr))
    fp.write('.data %x - %x\n' %
             (statistic.dataStartAddr, statistic.dataEndAddr))
    fp.write('.bss %x - %x\n' %
             (statistic.bssStartAddr, statistic.bssEndAddr))
    fp.close()

def writeFile_4_3(fileName) :
    'write object code to file. (Project 4.3)'
    fp = open(fileName, 'w')

    alloc = allocator.Allocator()

    statistic = alloc.arbitraryAllocator(segmentTable, symbolTable)
    fp.write('RP: %x - %x\n' %
             (statistic.RPStartAddr, statistic.RPEndAddr))
    fp.write('RWP: %x - %x\n' %
             (statistic.RWPStartAddr, statistic.RWPEndAddr))
    fp.write('RW: %x - %x\n' %
             (statistic.RWStartAddr, statistic.RWEndAddr))
    fp.close()

if __name__ == '__main__' :

    #readObj('example.txt')
    #readObj('example1.txt')
    readObj('ch4main.lk')
    readObj('ch4calif.lk')
    readObj('ch4mass.lk')
    readObj('ch4newyork.lk')
    #writeFile_4_2('output.txt')
    globalSymbolTable = readGlobalSymbol(objectTable)

    for key in globalSymbolTable :
        globalSymbol = globalSymbolTable[key]
        print key, globalSymbol.module, globalSymbol.defined
        
    #for key in objectTable :
    #    obj = objectTable[key]
    #    for name in obj.segnames :
    #        print key, name, obj.segs[obj.segnames[name]].data
