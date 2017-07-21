# Copyright (C) 2017  Jonas Colmsjö, Claes Strannegård
#
# [Using Google Style Guide](https://google.github.io/styleguide/pyguide.html)

import os
import datetime
import argparse

import animats.main

parser = argparse.ArgumentParser()
parser.add_argument("config", help="animat configuration")
args = parser.parse_args()

(outputPath, outputDir) = animats.main.getOutputPath()
animats.main.run(args.config, outputPath, outputDir)
