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

    
    def basicAllocator(self, segmentTable) :
        'allocator for project 4.1.'
        statistic = Statistic()
        
        for key in segmentTable :
            info = segmentTable[key]
            
            if info.name == '.text' :
                statistic.textSize += int(info.length, 16)
            elif info.name == '.data' :
                statistic.dataSize += int(info.length, 16)
            elif info.name == '.bss' :
                statistic.bssSize += int(info.length, 16)

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
        
        return statistic

    def commonBlockAllocator(self, segmentTable, symbolTable) :
        statistic = self.basicAllocator(segmentTable)
        for key in symbolTable :
            symbol = symbolTable[key]
            if symbol.defined == False and \
                   int(symbol.value, 16) != 0 :
                statistic.bssSize += int(symbol.value, 16)

        # update bssEndAddr
        statistic.bssEndAddr =\
                  statistic.bssStartAddr + statistic.bssSize
                

        return statistic

    def arbitraryAllocator(self, segmentTable, symbolTable) :
        'arbitrary allocator'
        statistic = AttributeStatistic()
        
        for key in segmentTable :
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
        
