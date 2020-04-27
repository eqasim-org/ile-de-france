import shutil

def configure(context):
    context.stage("matsim.simulation.run")
    context.stage("matsim.simulation.prepare")
    context.stage("matsim.runtime.eqasim")

    context.config("output_path")

def execute(context):
    config_path = "%s/%s" % (
        context.path("matsim.simulation.prepare"),
        context.stage("matsim.simulation.prepare")
    )

    for name in [
        "ile_de_france_households.xml.gz",
        "ile_de_france_population.xml.gz",
        "ile_de_france_facilities.xml.gz",
        "ile_de_france_network.xml.gz",
        "ile_de_france_transit_schedule.xml.gz",
        "ile_de_france_transit_vehicles.xml.gz",
        "ile_de_france_config.xml"
    ]:
        shutil.copy(
            "%s/%s" % (context.path("matsim.simulation.prepare"), name),
            "%s/%s" % (context.config("output_path"), name)
        )

    shutil.copy(
        "%s/%s" % (context.path("matsim.runtime.eqasim"), context.stage("matsim.runtime.eqasim")),
        context.config("output_path")
    )
