Animats
=======

Reference code for:

A General Model for Learning and Decision-Making in Artificial Animals by
Claes Strannegård, Nils Svangård, David Lindström, Joscha Bach and Bas Steunebrink

Submitted to IJCAI-17 AGA workshop, Melbourne, Australia

This repository is work-in-progress and while functional, not a finished open-source project.


Setup
=====

* First init `virtualenv` for Python3: `virtualenv -p python3 venv3` (`virutalenv` needs to be installed)
* Activate `virtualenv`: `source venv3/bin/activate`
* Install the necessary Python packages: `pip install -r requirements.txt`


Run the program
==============

* Activate `virtualenv`: `source venv3/bin/activate`
* Run the program: `python main.py`
* When using the browser client, first start the web sockets server: `python wsserver.py`


Development
===========

* In case new Python packages are installed, make sure to save the setup: `pip3 freeze > requirements.txt`
* Make sure to maintain the unit test when doing changes
* Run `./build.sh` to lint and run the unit tests


Credits
=======

Using some classes from the [AIMA book](https://github.com/aimacode/aima-python)
