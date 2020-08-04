import data.osm.osmium
import os, os.path

def configure(context):
    context.config("data_path")
    context.config("osm_path", "osm/ile-de-france-latest.osm.bz2")

    context.stage("data.osm.osmium")

def execute(context):
    input_files = context.config("osm_path").split(";")

    # Filter input files for quicker processing
    for index, path in enumerate(input_files):
        print("Filtering %s ..." % path)

        data.osm.osmium.run(context, [
            "tags-filter", "%s/%s" % (context.config("data_path"), path),
            "w/highway", "w/railway", "-o", "filtered_%d.osm.gz" % index
        ])

    # Merge filtered files if there are multiple ones
    print("Merging OSM data ...")

    data.osm.osmium.run(context, [
        "merge", "-o", "output.osm.gz"
    ] + [
        "filtered_%d.osm.gz" % index for index in range(len(input_files))
    ])

    # Remove temporary files
    for index, path in enumerate(input_files):
        print("Removing temporary file for %s ..." % path)
        os.remove("%s/filtered_%d.osm.gz" % (context.path(), index))

    return "output.osm.gz"

def validate(context):
    input_files = context.config("osm_path").split(";")
    total_size = 0

    for path in input_files:
        if not os.path.exists("%s/%s" % (context.config("data_path"), path)):
            raise RuntimeError("OSM data is not available: %s" % path)
        else:
            total_size += os.path.getsize("%s/%s" % (context.config("data_path"), path))

    return total_size
