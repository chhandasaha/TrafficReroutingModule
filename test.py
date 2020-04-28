#!/usr/bin/env python
# Eclipse SUMO, Simulation of Urban MObility; see https://eclipse.org/sumo
# Copyright (C) 2009-2017 German Aerospace Center (DLR) and others.
# This program and the accompanying materials
# are made available under the terms of the Eclipse Public License v2.0
# which accompanies this distribution, and is available at
# http://www.eclipse.org/legal/epl-v20.html

# @file    runner.py
# @author  Lena Kalleske
# @author  Daniel Krajzewicz
# @author  Michael Behrisch
# @author  Jakob Erdmann
# @date    2009-03-26
# @version $Id$

from __future__ import absolute_import
from __future__ import print_function

import os
import sys
import optparse
import subprocess
import random
from _hashlib import new

# we need to import python modules from the $SUMO_HOME/tools directory
try:
    sys.path.append(os.path.join(os.path.dirname(
        __file__), '..', '..', '..', '..', "tools"))  # tutorial in tests
    sys.path.append(os.path.join(os.environ.get("SUMO_HOME", os.path.join(
        os.path.dirname(__file__), "..", "..", "..")), "tools"))  # tutorial in docs
    from sumolib import checkBinary  # noqa
except ImportError:
    sys.exit(
        "please declare environment variable 'SUMO_HOME' as the root directory of your sumo installation (it should contain folders 'bin', 'tools' and 'docs')")

import traci
import traci.constants as tc
import traci._inductionloop

def generate_routefile():
    random.seed(42)  # make tests reproducible
    N = 3600  # number of time steps
    #demand per second from different directions
    pWE = 1. / 10
    pEW = 1. / 11
    pNS = 1. / 18
    pSN = 1. / 30
    with open("data/cross.rou.xml", "w") as routes:
        print("""<routes>
        <vType id="typeWE" accel="0.8" decel="4.5" sigma="0.5" length="5" minGap="2.5" maxSpeed="16.67" guiShape="passenger"/>
        <vType id="typeNS" accel="0.8" decel="4.5" sigma="0.5" length="7" minGap="3" maxSpeed="25" guiShape="bus"/>

        <route id="right" edges="51o 1i 2o 52i" />
        <route id="left" edges="52o 2i 1o 51i" />
        <route id="down" edges="54o 4i 3o 53i" />
        <route id="up" edges="53o 3i 4o 54i" />""", file=routes)
        # lastVeh = 0
        vehNr = 0
        for i in range(N):
            ss=random.uniform(0, 1)
            if ss < pWE:
                print('    <vehicle id="right_%i" type="typeWE" route="right" depart="%i" />' % (
                vehNr, i), file=routes)
                vehNr += 1
                #lastVeh = i
            ss=random.uniform(0, 1)
            if ss < pEW:
                print('    <vehicle id="left_%i" type="typeWE" route="left" depart="%i" />' % (
                vehNr, i), file=routes)
                vehNr += 1
                # lastVeh = i
            ss=random.uniform(0, 1)
            if ss< pNS:
                print('    <vehicle id="down_%i" type="typeNS" route="down" depart="%i" color="1,0,0"/>' % (
                vehNr, i), file=routes)
                vehNr += 1
                # lastVeh = i
            ss=random.uniform(0, 1)
            if ss < pSN:
                print('    <vehicle id="up_%i" type="typeNS" route="up" depart="%i" color="0,1,0"/>' % (
                vehNr, i), file=routes)
                vehNr += 1
                #lastVeh = i
        print("</routes>", file=routes)

# The program looks like this
#    <tlLogic id="0" type="static" programID="0" offset="0">
# the locations of the tls are      NESW
#        <phase duration="31" state="GrGr"/>
#        <phase duration="6"  state="yryr"/>
#        <phase duration="31" state="rGrG"/>
#        <phase duration="6"  state="ryry"/>
#    </tlLogic>


def run():
    """execute the TraCI control loop"""
    step = 0
    i=1
    prev=-1
    
    traci.trafficlight.setPhase("0", 2)
    prev=traci.trafficlight.getPhase("0")
    ppp=2
    while traci.simulation.getMinExpectedNumber() > 0:
        traci.simulationStep()
        step += 1
        edgeID = '2o'
        # COMPLETE THE FUNCTION LIST WITH OTHER traci.edge FUNCTIONs
        functionList = [ traci.edge.getCO2Emission(edgeID),  getElectricityConsumption(edgeID)]
        _f = open("result.txt", "w+")
        for f in functionList:
            _f.write(f + ', ')
        _f.close()
    traci.close()
    sys.stdout.flush()


def get_options():
    optParser = optparse.OptionParser()
    optParser.add_option("--nogui", action="store_true",
                         default=False, help="run the commandline version of sumo")
    options, args = optParser.parse_args()
    return options


# this is the main entry point of this script
if __name__ == "__main__":
    options = get_options()

    # this script has been called from the command line. It will start sumo as a
    # server, then connect and run
    if options.nogui:
        sumoBinary = checkBinary('sumo')
    else:
        sumoBinary = checkBinary('sumo-gui')

    # first, generate the route file for this simulation
#     generate_routefile()

    # this is the normal way of using traci. sumo is started as a
    # subprocess and then the python script connects and runs
    traci.start([sumoBinary, "-c", "data/cross.sumocfg",
                              "--tripinfo-output", "tripinfo.xml"])
    run()
