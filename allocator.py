#! /usr/bin/env python

import linker


class Statistic(object) :
    def __init__(self) :
        self.textSize = 0
        self.dataSize = 0
        self.bssSize = 0
        
        self.textStartAddr = 0
        self.dataStartAddr = 0
        self.bssStartAddr = 0

        self.textEndAddr = 0
        self.dataEndAddr = 0
        self.bssEndAddr = 0

    #def setTextSize(self, textSize) :
    #    self.textSize = textSize

    #def setDataSize(self, dataSize) :
    #    self.dataSize = dataSize

    #def setBssSize(self, bssSize) :
    #    self.bssSize = bssSize

class AttributeStatistic(object) :
    def __init__(self) :
        self.RPSize = 0
        self.RWSize = 0
        self.RWPSize = 0

        self.RPStartAddr = 0
        self.RWStartAddr = 0
        self.RWPStartAddr = 0

        self.RPEndAddr = 0
        self.RWEndAddr = 0
        self.RWPEndAddr = 0

        
class Allocator(object) :

    def __init__(self) :
        pass

    
    def basicAllocator(self, objectTable) :
        'allocator for .text, .data and .bss.'
        statistic = Statistic()
        
        for key in objectTable :
            obj = objectTable[key]

            segnames = obj.segnames
            segs = obj.segs

            for name in segnames :
                
                if name == '.text' :
                    obj.bases[name] = statistic.textSize
                    statistic.textSize += segs[segnames[name]].length
                elif name == '.data' :
                    obj.bases[name] = statistic.dataSize
                    statistic.dataSize += segs[segnames[name]].length
                elif name == '.bss' :
                    obj.bases[name] = statistic.bssSize
                    statistic.bssSize += segs[segnames[name]].length

        statistic.textStartAddr = 0x1000
        statistic.textEndAddr =\
                  statistic.textStartAddr + statistic.textSize

        multiple = ((statistic.textEndAddr + 1) / 0x1000) + 1
        
        statistic.dataStartAddr = multiple * 0x1000
        statistic.dataEndAddr =\
                  statistic.dataStartAddr + statistic.dataSize
        
        multiple = ((statistic.dataEndAddr + 1) / 4) + 1
        
        statistic.bssStartAddr = multiple * 4
        statistic.bssEndAddr =\
                  statistic.bssStartAddr + statistic.bssSize

        for key in objectTable :
            obj = objectTable[key]
            bases = obj.bases
            if '.text' in bases :
                bases['.text'] += statistic.textStartAddr
            elif '.data' in bases :
                bases['.data'] += statistic.dataStartAddr
            elif '.bss' in bases :
                bases['.bss'] += statistic.bssStartAddr
        
        return statistic

    def commonBlockAllocator(self, objectTable) :
        'allocator for basic allocator and common block.'
        statistic = self.basicAllocator(objectTable)
        multiple = ((statistic.bssEndAddr + 1) / 4) + 1
        commonBlockBase = multiple * 4
        for key in objectTable :
            
            obj = objectTable[key]
            
            symnames = obj.symnames
            syms = obj.syms
            for name in symnames :
                symbol = syms[symnames[name]]
                if symbol.defined == False and \
                   symbol.value != 0 :
                    symbol.defined = True
                    value = symbol.value
                    symbol.value = commonBlockBase
                    multiple = (commonBlockBase + value + 1) / 4 + 1
                    commonBlockBase = multiple * 4
            
        # update bssEndAddr
        statistic.bssEndAddr = commonBlockBase
        statistic.bssSize = statistic.bssEndAddr - statistic.bssStartAddr
        
        return statistic

    def arbitraryAllocator(self, objectTable) :
        'arbitrary allocator'
        statistic = AttributeStatistic()
        
        for key in objectTable :
            
            info = segmentTable[key]

            if info.readable == True and \
               info.present == True  and \
               info.writable == False :
                statistic.RPSize += int(info.length, 16)
            elif info.readable == True and \
                 info.writable == True and \
                 info.present == True :
                statistic.RWPSize += int(info.length, 16)
            elif info.readable == True and \
                 info.writable == True and \
                 info.present == False :
                statistic.RWSize += int(info.length, 16)

        statistic.RPStartAddr = 0x1000
        statistic.RPEndAddr =\
                  statistic.RPStartAddr + statistic.RPSize

        multiple = ((statistic.RPEndAddr + 1) / 0x1000) + 1
        statistic.RWPStartAddr = multiple * 0x1000
        statistic.RWPEndAddr =\
                  statistic.RWPStartAddr + statistic.RWPSize
        
        multiple = ((statistic.RWPEndAddr + 1) / 4) + 1
        statistic.RWStartAddr = multiple * 4
        statistic.RWEndAddr =\
                  statistic.RWStartAddr + statistic.RWSize

        # allocate common block
        for key in symbolTable :
            symbol = symbolTable[key]
            if symbol.defined == False and \
                   int(symbol.value, 16) != 0 :
                statistic.RWSize += int(symbol.value, 16)

        # update bssEndAddr
        statistic.RWEndAddr =\
                  statistic.RWStartAddr + statistic.RWSize
        
        return statistic
        
