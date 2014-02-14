#!/bin/bash

db=crk_2014_01

python performance.py $db dc cr 0 0 10 0.05 > dc_cr.dat &
python performance.py $db po cr 0 0 10 0.05 > po_cr.dat &
python performance.py $db many cr 0 0 10 0.05 > many_cr.dat &
python performance.py $db dc cs 0 -10 10 0.05 > dc_cs.dat &
python performance.py $db po cs 0 -10 10 0.05 > po_cs.dat &
python performance.py $db many cs 0 -10 10 0.05 > many_cs.dat &

