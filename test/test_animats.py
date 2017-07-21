# pylint: disable=missing-docstring, global-statement
#
# Copyright (C) 2017  Jonas Colmsjö, Claes Strannegård
#
# [Using Google Style Guide](https://google.github.io/styleguide/pyguide.html)


# Imports
# ======

import os
import filecmp
import difflib
import datetime
import unittest
import animats.main


# Setup logging
# =============

DEBUG_MODE = False

def debug(*args):
    if DEBUG_MODE: print('DEBUG:test_animats:', *args)

def log(*args):
    print('LOG:test_animats:', *args)

def error(*args):
    print('ERROR:test_animats:', *args)

def warn(*args):
    print('WARNING:test_animats:', *args)


# Unit tests
# ==========

def createDir(path):
    try:
        os.makedirs(path)
    except OSError as exception:
        if exception.errno != errno.EEXIST:
            raise

class TestAnimats(unittest.TestCase):

    def setUp(self):
        log('Testing animats...')

    def run_test(self, name):
        log('test_animats:'+name)

        currentDir = os.path.dirname(os.path.abspath(__file__))
        intputPath =  currentDir + '/' + name + '.json'
        outputDir = currentDir + os.path.join('/output', datetime.datetime.now().isoformat())
        createDir(outputDir)
        outputPath = os.path.join(outputDir, "wellbeeing.csv")

        animats.main.run(intputPath, outputPath)
        log('Used input:', intputPath, 'and wrote output to:', outputPath)
        self.assertTrue(filecmp.cmp(currentDir + '/' + name + '-wellbeing.csv', outputPath))


    def test_animats_examples(self):
        log('test_animats_examples')

#        self.run_test('example-1-copepod')
#        self.run_test('example-2-sheep')
#        self.run_test('example-3-swamp')
        self.run_test('example-4-seq')

    def tearDown(self):
        log('...done with test.')


# Main
# ====

if __name__ == '__main__':
    unittest.main()
