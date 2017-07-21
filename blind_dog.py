# pylint: disable=missing-docstring, global-statement, invalid-name
#
# A simple example showing how wsserver can be used
#
# Copyright (C) 2017  Jonas Colmsjö, Claes Strannegård
#
# [Using Google Style Guide](https://google.github.io/styleguide/pyguide.html)

import random

from agents import Agent
from agents import Thing
from agents import Environment

# Setup logging
# =============

DEBUG_MODE = False

def debug(*args):
    print('DEBUG:blind_dog:', *args)

def error(*args):
    print('ERROR:blind_dog:', *args)

def warn(*args):
    print('WARNING:blind_dog:', *args)


# Classes
# ========

class Food(Thing):
    pass

class Water(Thing):
    pass

class Dirt(Thing):
    pass

class Park(Environment):
    def __init__(self, wss):
        super().__init__()
        self.wss = wss

    def percept(self, agent):
        '''prints & return a list of things that are in our agent's location'''
        things = self.list_things_at(agent.location)
        return things

    def execute_action(self, agent, action):
        '''changes the state of the environment based on what the agent does.'''
        if action == "move down":
            msg = '{} decided to {} at location: {}'.format(str(agent)[1:-1],
                                                            action, agent.location)
            move_down()
            self.wss.send_print_message(msg)
            self.wss.send_update_agent('D', CFG['agents']['D'])
            print(msg)
            agent.movedown()

        elif action == "eat":
            items = self.list_things_at(agent.location, tclass=Food)
            if items:
                if agent.eat(items[0]): #Have the dog eat the first item
                    msg = '{} ate {} at location: {}'.format(str(agent)[1:-1], str(items[0])[1:-1], agent.location)
                    self.wss.send_print_message(msg)
                    print(msg)
                    self.delete_thing(items[0]) #Delete it from the Park after.

        elif action == "drink":
            items = self.list_things_at(agent.location, tclass=Water)
            if items:
                if agent.drink(items[0]): #Have the dog drink the first item
                    msg = '{} drank {} at location: {}'.format(str(agent)[1:-1], str(items[0])[1:-1], agent.location)
                    self.wss.send_print_message(msg)
                    print(msg)
                    self.delete_thing(items[0]) #Delete it from the Park after.

        elif action == "watch":
            items = self.list_things_at(agent.location, tclass=Thing)
            msg = '{} decided to {} {} at location: {}'.format(str(agent)[1:-1],
                                                               action, items,
                                                               agent.location)
            self.wss.send_print_message(msg)
            print(msg)


    def is_done(self):
        '''By default, we're done when we can't find a live agent,
        but to prevent killing our cute dog, we will stop before itself -
        when there is no more food or water'''
        no_edibles = not any(isinstance(thing, (Food, Water)) for thing in self.things)
        dead_agents = not any(agent.is_alive() for agent in self.agents)
        return dead_agents or no_edibles

class BlindDog(Agent):
    location = 1

    def movedown(self):
        self.location += 1

    def eat(self, thing):
        '''returns True upon success or False otherwise'''
        if isinstance(thing, Food):
            #print("Dog: Ate food at {}.".format(self.location))
            return True

        return False

    def drink(self, thing):
        ''' returns True upon success or False otherwise'''
        if isinstance(thing, Water):
            #print("Dog: Drank water at {}.".format(self.location))
            return True

        return False

    # thing
    def watch(self, _):
        ''' returns True upon success or False otherwise'''
        return True


def program(percepts):
    '''Returns an action based on it's percepts'''
    for p in percepts:
        if isinstance(p, Food):
            return 'eat'
        elif isinstance(p, Water):
            return 'drink'
        elif random.random() < 0.5:
            return 'watch'
    return 'move down'

# Main
# =====

# left: (-1,0), right: (1,0), up: (0,-1), down: (0,1)
MOVES = [(0, -1), (0, 1)]

CFG = {
    'numTilesPerSquare': (1, 1),
    'drawGrid': True,
    'randomTerrain': 0,
    'terrain': 'G\nD\nG\nG\nF\nG\nW\nG\nG\nG',
    'agents': {
        'D': {
            'name': 'D',
            'pos': (0, 0),
            'hidden': False
        }
    }
}

def add_pos(pos1, pos2):
    return (pos1[0]+ pos2[0], pos1[1] + pos2[1])

def move_down():
    CFG['agents']['D']['pos'] = add_pos(CFG['agents']['D']['pos'], (0,1))

def run(wss):
    park = Park(wss)
    dog = BlindDog(program)
    dogfood = Food()
    water = Water()
    dirt = Dirt()
    park.add_thing(dog, 1)
    park.add_thing(dirt, 2)
    park.add_thing(dogfood, 5)
    park.add_thing(water, 7)

    wss.send_init(CFG)

    park.run(20)
