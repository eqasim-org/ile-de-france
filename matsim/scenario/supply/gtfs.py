import os.path

import matsim.runtime.pt2matsim as pt2matsim

def configure(context):
    context.stage("matsim.runtime.java")
    context.stage("matsim.runtime.pt2matsim")

    context.config("data_path")
    context.config("gtfs_path", "gtfs")

def execute(context):
    gtfs_path = os.path.realpath("%s/%s" % (context.config("data_path"), context.config("gtfs_path")))

    pt2matsim.run(context, "org.matsim.pt2matsim.run.Gtfs2TransitSchedule", [
        gtfs_path,
        "dayWithMostServices", "EPSG:2154", # TODO: dayWithMostServices should be made explicit and configurable!
        "%s/transit_schedule.xml.gz" % context.path(),
        "%s/transit_vehicles.xml.gz" % context.path()
    ])

    assert(os.path.exists("%s/transit_schedule.xml.gz" % context.path()))
    assert(os.path.exists("%s/transit_vehicles.xml.gz" % context.path()))

    return dict(
        schedule_path = "transit_schedule.xml.gz",
        vehicles_path = "transit_vehicles.xml.gz"
    )

def validate(context):
    if not os.path.exists("%s/%s/trips.txt" % (context.config("data_path"), context.config("gtfs_path"))):
        raise RuntimeError("GTFS data is not available")

    return os.path.getsize("%s/%s/trips.txt" % (context.config("data_path"), context.config("gtfs_path")))
