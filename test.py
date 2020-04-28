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