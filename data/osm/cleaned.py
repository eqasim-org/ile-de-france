import data.osm.osmosis
import os, os.path, gzip

"""
This file reads the OSM data in PBF format specified by the "osm_path"
and "data_path" configuration options. The data is read from
"data_path/osm_path". Note that you can define a list of input files separated
by ";" in the "osm_path" option. These OSM files will be merged, for instance,
if you want to merge the old Languedoc and Midi-Pyrénées regional snapshots
from Geofabrik to create a continuous file for the new Occitanie region.

This stage furthermore filters the file such that only highway elmenets and
railway elements of the OSM data remain. This makes it easier for the downstream
MATSim converter to work with the data.
"""

def configure(context):
    context.config("data_path")
    context.config("osm_path", "osm/ile-de-france-latest.osm.pbf")

    context.stage("data.osm.osmosis")

def execute(context):
    input_files = context.config("osm_path").split(";")

    # Filter input files for quicker processing
    for index, path in enumerate(input_files):
        print("Filtering %s ..." % path)

        mode = "pbf" if path.endswith("pbf") else "xml"

        data.osm.osmosis.run(context, [
            "--read-%s" % mode, "%s/%s" % (context.config("data_path"), path),
            "--tag-filter", "accept-ways", "highway=*", "railway=*",
            "--write-pbf", "filtered_%d.osm.pbf" % index
        ])

    # Merge filtered files if there are multiple ones
    print("Merging and compressing OSM data...")

    command = []
    for index in range(len(input_files)):
        command += ["--read-pbf", "filtered_%d.osm.pbf" % index]

    for index in range(len(input_files) - 1):
        command += ["--merge"]

    command += ["--write-xml", "compressionMethod=gzip", "output.osm.gz"]

    data.osm.osmosis.run(context, command)

    # Pipe output to file and write using gzip
    #with gzip.open("%s/output.osm.gz" % context.path(), "wb+") as f:
    #    data.osm.osmosis.run(context, command, f = f)

    # Remove temporary files
    for index, path in enumerate(input_files):
        print("Removing temporary file for %s ..." % path)
        os.remove("%s/filtered_%d.osm.pbf" % (context.path(), index))

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
