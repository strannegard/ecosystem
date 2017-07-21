# pylint: disable=missing-docstring, global-statement, eval-used, invalid-name, len-as-condition
#
# This web sockets server makes it possible to view environments and agents
# from a we browser.
#
# Copyright (C) 2017  Jonas Colmsjö, Claes Strannegård

import sys
import json
import signal
import random

import asyncio
import websockets

import blind_dog
import animats.main


# Constants and functions
# =======================

DEBUG_MODE = False

def debug(*args):
    print('DEBUG:', *args)

def writef(string):
    sys.stdout.write(string)
    sys.stdout.flush()


# Websockets server class
# ========================

class WssServer:

    def __init__(self, message_handler):
        self.connected = False
        self.queue = []
        self.message_handler = message_handler

    # install a SIGALRM handler and  emit SIGALRM every 1 sec
    # signum, frame
    def sig_handler(self, _, _2):
        writef('.')
        if not self.connected:
            signal.setitimer(signal.ITIMER_REAL, 1)
        else:
            writef("Connected!\n")

    async def consumer_handler(self, websocket):
        while True:
            message = await websocket.recv()
            (message, param) = json.loads(message)

            self.message_handler(self, message, param)

            await asyncio.sleep(1)

    async def producer_handler(self, websocket):
        while True:
            self.connected = True
            await asyncio.sleep(1)
            if len(self.queue) > 0:
                await websocket.send(self.queue.pop(0))

    # path
    async def handler(self, websocket, _):
        consumer_task = asyncio.ensure_future(self.consumer_handler(websocket))
        producer_task = asyncio.ensure_future(self.producer_handler(websocket))

        # done
        _, pending = await asyncio.wait(
            [consumer_task, producer_task],
            return_when=asyncio.FIRST_COMPLETED,
        )

        for task in pending:
            task.cancel()

    def start_wss_server(self):

        # start printing dots while waiting for the client to connect
        signal.signal(signal.SIGALRM, self.sig_handler)
        signal.setitimer(signal.ITIMER_REAL, 1)
        writef('Waiting for client to connect')

        # start the websockets server
        start_server = websockets.serve(self.handler, '127.0.0.1', 5678)
        asyncio.get_event_loop().run_until_complete(start_server)
        asyncio.get_event_loop().run_forever()

    def send(self, msg):
        self.queue.append(msg)

    def send_init(self, cfg):
        self.send('f = new Field()')
        self.send('f.initTerrain(' + json.dumps(cfg) + ')')

    def send_print_message(self, msg):
        self.send('Field.printMessage("' + msg + '")')

    def send_update_agent(self, agent, state):
        self.send('f.updateAgent("' + agent + '",' + json.dumps(state) + ')')

# Example of how the Field JS class can be used
# ---------------------------------------------

# left: (-1,0), right: (1,0), up: (0,-1), down: (0,1)
MOVES = [(-1, 0), (1, 0), (0, -1), (0, 1)]

TERRAIN = 'GGGGGGGGGG\nDDDDDDDDDD\nWWWWWWWWWW\nGGGGGGGGGG\nGGGGGGGGGG\nGGGGGGGGGG\nGGGGGGGGGG\nGGGGGGGGGG\nGGGGGGGGGG\nGGGGGGGGGG'
TERRAIN_SIZE = (10, 10)

CFG = {
    'numTilesPerSquare': (1, 1),
    'drawGrid': True,
    'randomTerrain': 0,
    'terrain': TERRAIN,
    'agents': {
        'A': {
            'name': 'A',
            'pos': (0, 0),
            'hidden': False
        },
        'B': {
            'name': 'B',
            'pos': (1, 0),
            'hidden': False
            }
        }
    }

def update_agent_pos(cfg, agent, pos):
    cfg['agents'][agent]['pos'] = pos

def get_agent_pos(cfg, agent):
    return cfg['agents'][agent]['pos']

def add_pos(pos1, pos2):
    return (pos1[0]+ pos2[0], pos1[1] + pos2[1])

def check_pos(pos):
    return pos[0] >= 0 and pos[0] < TERRAIN_SIZE[0] and pos[1] >= 0 and pos[1] < TERRAIN_SIZE[1]

def random_move(from_pos):
    move = random.choice(MOVES)
    new_pos = add_pos(from_pos, move)

    # Make sure we are within the field
    if not check_pos(new_pos):
        new_pos = random_move(from_pos)

    return new_pos

def run_example(wss, param):
    wss.send_init(CFG)
    for _ in range(0, int(param)):
        for agent in CFG['agents']:
            update_agent_pos(CFG, agent, random_move(get_agent_pos(CFG, agent)))
            wss.send_update_agent(agent, CFG['agents'][agent])

# Main
# ====

def my_handler(wss, message, param):
    if message == 'example':
        run_example(wss, param)

    elif message == 'blind_dog':
        blind_dog.run(wss)

    elif message == 'animat':
        (outputPath, outputDir) = animats.main.getOutputPath()
        animats.main.run(param, outputPath, outputDir, wss)

    else:
        wss.send_print_message('unknown message ' + message + ' with param ' + param)


# execute only if run as a script
if __name__ == "__main__":
    wss = WssServer(my_handler)
    wss.start_wss_server()
