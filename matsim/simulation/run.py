import shutil
import os.path

import matsim.runtime.eqasim as eqasim

def configure(context):
    context.stage("matsim.simulation.prepare")

    context.stage("matsim.runtime.java")
    context.stage("matsim.runtime.eqasim")

    context.config("iterations", 40)

def execute(context):
    config_path = "%s/%s" % (
        context.path("matsim.simulation.prepare"),
        context.stage("matsim.simulation.prepare")
    )

    iterations = context.config("iterations")

    # Run routing
    eqasim.run(context, "org.eqasim.ile_de_france.RunSimulation", [
        "--config-path", config_path,
        "--config:controler.lastIteration", str(iterations),
        "--config:controler.writeEventsInterval", str(iterations),
        "--config:controler.writePlansInterval", str(iterations),
        "--config:eqasim.tripAnalysisInterval", str(iterations)
    ])
    assert os.path.exists("%s/simulation_output/output_events.xml.gz" % context.path())
