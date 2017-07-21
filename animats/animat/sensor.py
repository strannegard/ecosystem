# -*- coding: utf-8 -*-
#
#    pyAnimat - Simulate Animats using Transparent Graphs as a way to AGI
#    Copyright (C) 2017  Nils Svangård, Claes Strannegård
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

#    Jonas Colmsjö, 2017-07-21: Converted to Python 3, added support for
#    several agents, fixed logging etc.

from .node import *


# Setup logging
# =============

DEBUG_MODE = False

def debug(*args, end=''):
    if DEBUG_MODE: print('DEBUG:sensor:', *args)

def error(*args):
    print('ERROR:sensor:', *args)

def warn(*args):
    print('WARNING:sensor:', *args)


# The code
# ========

class SensorNode(Node):
    def __init__(self, name, sense=None):
        Node.__init__(self, name, permanent=True)
        self.sense=sense

    def __str__(self):
        return "SensorNode - sense:" + str(self.sense) + ", " + super().__str__()

    # JC, replaced self.sense with observation and call from Environment.percept (via Network.tick)
    # Not sure how this fits in: if x == 't': x = 1
    def tick(self, time, observation=None):
        if Node.tick(self, time):
            if self.sense is not None:
                debug('Using self.sense')
                x = self.sense(time)
            else:
                debug('Using observation ', observation)
                x = observation.get(self.name[1:],0)

            if x: self.activate(time)
            else: self.deactivate(time)
            return True
        else:
            return False
