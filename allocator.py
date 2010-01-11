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

        
class Allocator(object) :

    def __init__(self) :
        pass
    
    def allocator_4_1(self, segmentTable) :
        statistic = Statistic()
        
        for key in segmentTable :
            info = segmentTable[key]
            
            if info.name == '.text' :
                statistic.textSize += int(info.length)
            elif info.name == '.data' :
                statistic.dataSize += int(info.length)
            elif info.name == '.bss' :
                statistic.bssSize += int(info.length)

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
