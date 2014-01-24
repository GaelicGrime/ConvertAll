#!/usr/bin/env python3

#****************************************************************************
# unitdata.py, reads unit data from file
#
# ConvertAll, a units conversion program
# Copyright (C) 2014, Douglas W. Bell
#
# This is free software; you can redistribute it and/or modify it under the
# terms of the GNU General Public License, either Version 2 or any later
# version.  This program is distributed in the hope that it will be useful,
# but WITTHOUT ANY WARRANTY.  See the included LICENSE file for details.
#*****************************************************************************

import sys
import os.path
try:
    from __main__ import dataFilePath, lang
except ImportError:
    dataFilePath = None
    lang = ''
import unitatom


class UnitDataError(Exception):
    """General exception for unit data problems.
    """
    pass


class UnitData(dict):
    """Reads unit data nad stores in a dictionary based on unit name.
    """
    def __init__(self):
        dict.__init__(self)
        self.sortedKeys = []
        self.typeList = []

    def findDataFile(self):
        """Search for data file, return line list or None.
        """
        modPath = os.path.abspath(sys.path[0])
        if modPath.endswith('.zip'):  # for py2exe
            modPath = os.path.dirname(modPath)
        pathList = [dataFilePath, os.path.join(modPath, '../data/'), modPath]
        fileList = ['units.dat']
        if lang and lang != 'C':
            fileList[0:0] = ['units_{0}.dat'.format(lang),
                             'units_{0}.dat'.format(lang[:2])]
        for path in pathList:
            if path:
                for fileName in fileList:
                    try:
                        with open(os.path.join(path, fileName), 'r',
                                  encoding='utf-8') as f:
                            lineList = f.readlines()
                        return lineList
                    except IOError:
                        pass
        raise UnitDataError(_('Can not read "units.dat" file'))

    def readData(self):
        """Read all unit data from file, return number loaded.
        """
        lines = self.findDataFile()
        for i in range(len(lines)):     # join continuation lines
            delta = 1
            while lines[i].rstrip().endswith('\\'):
                lines[i] = ''.join([lines[i].rstrip()[:-1], lines[i+delta]])
                lines[i+delta] = ''
                delta += 1
        units = [unitatom.UnitAtom(line) for line in lines if
                 line.split('#', 1)[0].strip()]   # remove comment lines
        typeText = ''
        for unit in units:               # find & set headings
            if unit.name.startswith('['):
                typeText = unit.name[1:-1].strip()
                self.typeList.append(typeText)
            unit.typeName = typeText
        units = [unit for unit in units if unit.equiv]  # keep valid units
        for unit in units:
            self[unit.name.lower().replace(' ', '')] = unit
        self.sortedKeys = list(self.keys())
        self.sortedKeys.sort()
        if len(self.sortedKeys) < len(units):
            raise UnitDataError(_('Duplicate unit names found'))
        return len(units)

    def findPartialMatch(self, text):
        """Return first partially matching unit or None.
        """
        text = text.lower().replace(' ', '')
        if not text:
            return None
        for name in self.sortedKeys:
            if name.startswith(text):
                return self[name]
        return None

    def findSortPos(self, text):
        """Return unit whose abbrev comes immediately after text.
        """
        text = text.lower().replace(' ', '')
        for name in self.sortedKeys:
            if text <= name:
                return self[name]
        return self[self.sortedKeys[-1]]

    def filteredList(self, type='', srchStr=''):
        """Return list of units matching type and search string,
           if given.
        """
        units = list(self.values())
        if type:
            units = [unit for unit in units if unit.typeName == type]
        if srchStr.strip():
            srchWords = [word.lower() for word in srchStr.split()]
            srchUnits = []
            for unit in units:
                if unit.matchWords(srchWords):
                    srchUnits.append(unit)
            units = srchUnits
        return units
