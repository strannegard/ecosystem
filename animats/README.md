CHANGES:

1. Using random.seed(1) in network.py to make the result predictable (and testable). Should be moved to the config file.
1. Ran `2to3` on all files to make them compatible with Python 3
1. Skipping episodes

-----

# Animats

Reference code for:

A General Model for Learning and Decision-Making in Artificial Animals
Claes Strannegård, Nils Svangård, David Lindström, Joscha Bach, Bas Steunebrink
Submitted to IJCAI-17 AGA workshop, Melbourne, Australia

This repository is work-in-progress and while functional, not a finished open-source project.

Developed in Python 2.7 for compatibility with the Malmö Project.

## Installation

No fancy requirements if you disable the 'plotter'.

requirements.txt is coming.

## Usage

Just run main.py from the command line. It will execute the configuration file
specified in the code and write output to output/<iso-timestamp>

In the examples/ directory live the configuration files for different animat missions.
