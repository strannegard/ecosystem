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

import os
import datetime
import itertools
import random

from . import agent as agentModule
from .network import *
from .sensor import *
from .motor import *

import agents


# Setup logging
# =============

DEBUG_MODE = True

def debug(*args):
    if DEBUG_MODE: print('DEBUG:environment:', *args)

def error(*args):
    print('ERROR:environment:', *args)

def warn(*args):
    print('WARNING:environment:', *args)


# The code
# =========

def makeRewardDict(reward, needs):
    if type(reward) != dict:
        reward = {k:reward for k in list(needs.keys())}
    return reward

class EnvironmentConfig:
    def __init__(self, conf):
#        worldmap = "rrrrrrrrrr\ngggggggggg\n0000000000\nbbbbbbbbbb\nxxxxxxxxxx"
        self.worldmap = conf.get("world")

        self.world = [list(x) for x in conf.get("world").split("\n")]
        self.blocks = conf.get("blocks", {})
        self.is_torus = conf.get("torus", False)
        self.transform = conf.get("transform", {})
        self.objectives = conf.get("objectives", ["water", "glucose"])
        self.rewardMatrix = conf.get("rewards", {})
        self.maxIterations = conf.get("iterations", 100)
        self.enable_playback = conf.get("playback", False)

class Environment(agents.Environment):
    def __init__(self, config=None, objectives=None, wss=None, fieldConfig=None):
        super().__init__()
        self.wss = wss
        self.fieldConfig = fieldConfig
        self.config = config
        self.world = config.world
        self.objectives = objectives or config.objectives
        if self.config.enable_playback:
            self.playback = open( os.path.join(config.outputPath, "playback_script.py"), "w")
            print("import turtle;t = turtle.Turtle()", file=self.playback)

    def _playback(self, agent, action, nx=0, ny=0):
        if self.config.enable_playback:
            if action == 'up' or action == 'down' or action == 'right' or action == 'left':
                x,y = agent.position
                wrap = False
                if abs(nx-x) > 1 or abs(ny-y) > 1:
                    wrap = True
                if wrap: print("t.color((1,0,0));t.dot(3);t.penup()", file=self.playback)
                if self.config.is_torus:
                    nx = nx%self.getWidth()
                    ny = ny%self.getHeight()
                print("t.setpos(%d,%d)" % (nx*10, ny*10), file=self.playback)
                if wrap: print("t.pendown();t.color((1,1,0));t.dot(3);t.color((0,0,0))", file=self.playback)
            elif action == 'turn_right':
                print("t.right(90)", file=self.playback)
            elif action == 'turn_left':
                print("t.left(90)", file=self.playback)
            elif action == 'eat':
                print("t.color((0,1,0));t.dot(5);t.color((0,0,0))", file=self.playback)
            elif action == 'drink':
                print("t.color((0,0,1));t.dot(5);t.color((0,0,0))", file=self.playback)

    def getHeight(self):
        return len(self.world)

    def getWidth(self):
        return len(self.world[0])

    def currentCell(self, agent, delta=(0,0)):
        y = (agent.position[1]+delta[1]) % len(self.world)
        x = (agent.position[0]+delta[0]) % len(self.world[y])
        return self.world[y][x]

    def setCurrentCell(self, agent, v):
        y = agent.position[1] % len(self.world)
        x = agent.position[0] % len(self.world[y])
        self.world[y][x] = v

    # Updates the sensors, does not return a percept
    def percept(self, agent, delta=(0,0)):
        '''prints & return a list of things that are in our agent's location'''
        #things = self.list_things_at(agent.location)
        #return things

        y = (agent.position[1]+delta[1]) % len(self.world)
        x = (agent.position[0]+delta[0]) % len(self.world[y])
        cell = self.world[y][x]

        observation = self.config.blocks.get(cell,{})

        debug('--------------\npercept - cell:' + cell + ", observation:" + str(observation))
        agent.network.tick(observation)

        return None

    def _getReward(self, action, cell, status):
        rm = self.config.rewardMatrix
        am = rm.get(action, rm.get('*',{}))
        r = am.get(cell, am.get('*',0.0))
        reward = makeRewardDict(r, status)
        # TODO: truncate reward if need is satisfied
        return reward

    def execute_action(self, agent, action):
        '''changes the state of the environment based on what the agent does.'''
        debug("execute_action - position:", agent.position, ", action:", action)

        act, _, _ = action
        reward = self.takeAction(agent, act)
        agent.takeAction(action, reward)


    def takeAction(self, agent, action):
        cell = self.currentCell(agent)
        reward = self._getReward(action, cell, agent.needs)
        debug("takeAction - reward:", reward, ", position:", agent.position, ", action:", action, ", wss:", self.wss)

        def move_agent(agent, dx, dy):
#            print "PP MOVE", agent.position, dx, dy
            nx = agent.position[0]+dx
            ny = agent.position[1]+dy
            if self.config.is_torus:
                nx = nx%self.getWidth()
                ny = ny%self.getHeight()
            self._playback(agent, action, nx, ny)
            if nx >= 0 and nx < self.getWidth() and ny >= 0 and ny < self.getHeight():
                agent.position = (nx, ny)
                if self.wss is not None:
                    self.fieldConfig['agents'][agent.name]['pos'] = agent.position
                    self.wss.send_update_agent(agent.name, self.fieldConfig['agents'][agent.name])

#            print "PP NEW", agent.position

        if action == 'up':
            dx,dy = agentModule.ORIENTATION_MATRIX[agent.orientation%8]
            move_agent(agent, dx, dy)
        elif action == 'down':
            dx,dy = agentModule.ORIENTATION_MATRIX[(agent.orientation+4)%8]
            move_agent(agent, dx, dy)
        elif action == 'left':
            dx,dy = agentModule.ORIENTATION_MATRIX[(agent.orientation-2)%8]
            move_agent(agent, dx, dy)
        elif action == 'right':
            dx,dy = agentModule.ORIENTATION_MATRIX[(agent.orientation+2)%8]
            move_agent(agent, dx, dy)
        elif action == 'turn_right':
            agent.orientation = (agent.orientation+1)%8
            self._playback(agent, action)
        elif action == 'turn_left':
            agent.orientation = (agent.orientation-1)%8
            self._playback(agent, action)
        elif action == 'eat':
            self._playback(agent, action)
            if self.wss is not None:
                self.wss.send_print_message('Agent ' + agent.name + ' ate')
        elif action == 'drink':
            self._playback(agent, action)
            if self.wss is not None:
                self.wss.send_print_message('Agent ' + agent.name + ' drank')

        trans = self.config.transform.get(action,{}).get(cell, None)
        if trans:
            debug("takeAction - *** transform action:", action, ", cell:", cell, ", trans", trans)
            self.setCurrentCell(agent, trans)

        return reward

    def printWorld(self):
        for row in self.world:
            debug(row)
