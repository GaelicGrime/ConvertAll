#!/usr/bin/env python3

#****************************************************************************
# unitatom.py, provides class to hold data on each available unit
#
# ConvertAll, a units conversion program
# Copyright (C) 2016, Douglas W. Bell
#
# This is free software; you can redistribute it and/or modify it under the
# terms of the GNU General Public License, either Version 2 or any later
# version.  This program is distributed in the hope that it will be useful,
# but WITTHOUT ANY WARRANTY.  See the included LICENSE file for details.
#*****************************************************************************

import re
import copy
import unitdata


class UnitAtom(object):
    """Reads and stores a single unit conversion.
    """
    partialExp = 1000
    badOpRegEx = re.compile(r'[^\d\.eE\+\-\*/]')
    eqnRegEx = re.compile(r'\[(.*?)\](.*)')
    def __init__(self, dataStr):
        dataList = dataStr.split('#')
        unitList = dataList.pop(0).split('=', 1)
        self.name = unitList.pop(0).strip()
        self.equiv = ''
        self.factor = 1.0
        self.fromEqn = ''   # used only for non-linear units
        self.toEqn = ''     # used only for non-linear units
        if unitList:
            self.equiv = unitList[0].strip()
            if self.equiv[0] == '[':   # used only for non-linear units
                try:
                    self.equiv, self.fromEqn = UnitAtom.eqnRegEx.\
                                               match(self.equiv).groups()
                    if ';' in self.fromEqn:
                        self.fromEqn, self.toEqn = self.fromEqn.split(';', 1)
                        self.toEqn = self.toEqn.strip()
                    self.fromEqn = self.fromEqn.strip()
                except AttributeError:
                    raise unitdata.UnitDataError(_('Bad equation for "{0}"').
                                                 format(self.name))
            else:                # split factor and equiv unit for linear
                parts = self.equiv.split(None, 1)
                if len(parts) > 1 and \
                         UnitAtom.badOpRegEx.search(parts[0]) == None:
                                      # only allowed digits and operators
                    try:
                        self.factor = float(eval(parts[0]))
                        self.equiv = parts[1]
                    except:
                        pass
        self.comments = [comm.strip() for comm in dataList]
        self.comments.extend([''] * (2 - len(self.comments)))
        self.exp = 1
        self.viewLink = None
        self.typeName = ''

    def description(self):
        """Return name and 1st comment (usu. full name) if applicable.
        """
        if self.comments[0]:
            return '{0}  ({1})'.format(self.name, self.comments[0])
        return self.name

    def unitValid(self):
        """Return True if unit and exponent are valid.
        """
        if self.equiv and \
                -UnitAtom.partialExp < self.exp < UnitAtom.partialExp:
            return True
        return False

    def unitText(self, absExp=False):
        """Return text for unit name with exponent or absolute value of exp.
        """
        exp = self.exp
        if absExp:
            exp = abs(self.exp)
        if exp == 1:
            return self.name
        if -UnitAtom.partialExp < exp < UnitAtom.partialExp:
            return '{0}^{1}'.format(self.name, exp)
        if exp > 1:
            return '{0}^'.format(self.name)
        else:
            return '{0}^-'.format(self.name)

    def matchWords(self, wordList):
        """Return True if unit name and comments match word list.
        """
        dataStr = ' '.join((self.name, self.comments[0],
                             self.comments[1])).lower()
        for word in wordList:
            if dataStr.find(word) == -1:
                return False
        return True

    def copy(self):
        """Return a copy of the unit so the exponent can be changed.
        """
        return copy.copy(self)

    def __lt__(self, other):
        """Less than comparison for sorting.
        """
        return self.name.lower() < other.name.lower()

    def __eq__(self, other):
        """Equality test.
        """
        return self.name.lower() == other.name.lower()
