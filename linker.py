#! /usr/bin/env python

import allocator

# segments table information
segmentTable = {}

# symbol table
symbolTable = {}

# relocation information
relocation = {}

# code segment data
textData = ''

# data segment data
dataData = ''

# bss segment data
bssData = ''

class SegmentInfo() :
    'Segment Infomation'
    readable = False
    writable = False
    present = False
    
    def __init__(self, name, addr, length, flags) :
        self.name = name
        self.addr = addr
        self.length = length
        self.setFlags(flags)

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

    def __init__(self, name, value, seg, type) :
        self.name = name
        self.value = value
        self.seg = seg
        self.setType(type)

    def setType(self, type) :
        
        if type == 'D' :
            self.defined = True
        elif type == 'U' :
            self.defined = False

class Relocation() :
    'relocation entity'

    def __init__(self, loc, seg, ref, type) :
        self.loc = loc
        self.seg = seg
        self.ref = ref
        self.type = type


class SymbolReloc() :
    'symbol relocation information.'
    def __init__(self, loc, ref) :
        self.loc = loc
        self.ref = ref


def readFile (fileName) :
    'read infomation from file.'
    global segmentTable, symbolTable, relocation, textData, dataData, bssData
    fp = open(fileName)
    magicNumber = fp.readline()
    print magicNumber

    # read number of segment, number of symbol table entries,
    #+ number of relocation entities.
    s = fp.readline()
    args = s.split(' ')
    nsegs = args[0]
    nsyms = args[1]
    nrels = args[2]

    # read segsments
    
    for i in range(1, int(nsegs, 16) + 1) :
        s = fp.readline()
        s = s.strip()
        members = s.split(' ')
        info = SegmentInfo(members[0], members[1], members[2], members[3])
        segmentTable[i] = info

    
    # read symbols
    for i in range(1, int(nsyms, 16) + 1) :
        s = fp.readline()
        s = s.strip()
        members = s.split(' ')
        info = Symbol(members[0], members[1], members[2], members[3])
        symbolTable[i] = info


    # read rels
    for i in range(1, int(nrels, 16) + 1) :
        s = fp.readline()
        s = s.strip()
        members = s.split(' ')
        info = Relocation(members[0], members[1], members[2], members[3])
        relocation[i] = info


    # read data
    data = ''
    for line in fp :
        data += line.strip() + ' '

    data = data.strip()
    
    for key in segmentTable:
        #global textData, dataData, bssData
        info = segmentTable[key]
        count = int(info.length, 16)
        if count == 0:
            continue
        
        if info.name == '.text' :
            textData += data[:3 * count - 1] + ' '
            data = data[3 * count:]
        elif info.name == '.data' :
            dataData += data[:3 * count - 1] + ' '
            data = data[3 * count:]
        elif info.name == '.bss' :
            bssData += data[:3 * count - 1] + ' '
            data = data[3 * count:]

    textData = textData.strip()
    dataData = dataData.strip()
    bssData = bssData.strip()

    fp.close()



# write object file routines
def my_cmp(s1, s2) :
    return cmp(s1.loc, s2.loc)


def writeFile_3_1(fileName) :
    'write result to file. (Project 3.1)'
    fp = open(fileName, 'w')

    for key in segmentTable:
        info = segmentTable[key]
        fp.write(info.name + ' ' + info.addr + ' ' + info.length + 
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
    

if __name__ == '__main__' :

    readFile('example.txt')
    writeFile_4_2('output.txt')
    print textData
    print dataData
    print bssData

