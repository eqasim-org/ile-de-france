import shutil

def configure(context):
    context.stage("matsim.simulation.run")
    context.stage("matsim.simulation.prepare")
    context.stage("matsim.runtime.eqasim")

    context.config("output_path")
    context.config("output_prefix", "ile_de_france_")
    context.config("write_jar", True)
    context.config("generate_vehicles_file", False)
    need_osm = context.config("export_detailed_network", False)
    if need_osm:
        context.stage("matsim.scenario.supply.osm")
    

    context.stage("documentation.meta_output")

def execute(context):
    config_path = "%s/%s" % (
        context.path("matsim.simulation.prepare"),
        context.stage("matsim.simulation.prepare")
    )

    file_names = [
        "%shouseholds.xml.gz" % context.config("output_prefix"),
        "%spopulation.xml.gz" % context.config("output_prefix"),
        "%sfacilities.xml.gz" % context.config("output_prefix"),
        "%snetwork.xml.gz" % context.config("output_prefix"),
        "%stransit_schedule.xml.gz" % context.config("output_prefix"),
        "%stransit_vehicles.xml.gz" % context.config("output_prefix"),
        "%sconfig.xml" % context.config("output_prefix")
    ]

    if context.config("generate_vehicles_file"):
        vehicle_file = "%svehicles.xml.gz" % context.config("output_prefix")

        # it would make more sense to modify this in the eqasim-java part (in org.eqasim.core.scenario.config)
        # but it's not obvious how to preserve backward compatibility hence the following method :
        config_file = "%sconfig.xml" % context.config("output_prefix")
        with open( "%s/%s" % (context.path("matsim.simulation.prepare"), config_file)) as f_read:
            content = f_read.read()
            content = content.replace(
                '<param name="vehiclesFile" value="null" />',
                '<param name="vehiclesFile" value="%s" />' % vehicle_file
            )
            content = content.replace(
                '<param name="vehiclesSource" value="defaultVehicle" />',
                '<param name="vehiclesSource" value="fromVehiclesData" />'
            )
            with open("%s/%s" % (context.config("output_path"), config_file), "w+") as f_write:
                f_write.write(content)
        
        file_names.append(vehicle_file)
        # since we did a copy & modify, no need to copy it again
        file_names.remove(config_file)

    for name in file_names:
        shutil.copy(
            "%s/%s" % (context.path("matsim.simulation.prepare"), name),
            "%s/%s" % (context.config("output_path"), name)
        )

    if context.config("export_detailed_network"):
        shutil.copy(
            "%s/%s" % (context.path("matsim.scenario.supply.osm"), "detailed_network.csv"),
            "%s/%s" % (context.config("output_path"), "%sdetailed_network.csv" % context.config("output_prefix"))
        )
    
    if context.config("write_jar"):
        shutil.copy(
            "%s/%s" % (context.path("matsim.runtime.eqasim"), context.stage("matsim.runtime.eqasim")),
            "%s/%srun.jar" % (context.config("output_path"), context.config("output_prefix"))
        )
