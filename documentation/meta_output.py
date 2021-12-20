import geopandas as gpd
import pandas as pd
import shapely.geometry as geo
import os, datetime, json
import matsim.runtime.git
import subprocess as sp


def configure(context):
    context.stage("matsim.runtime.git")
    context.config("output_path")
    context.config("output_prefix", "ile_de_france_")

    for option in ("sampling_rate", "hts", "random_seed"):
        context.config(option)

def get_version_path():
    directory_path = os.path.dirname(os.path.realpath(__file__))
    return os.path.realpath("%s/../VERSION" % directory_path)

def execute(context):
    commit = "unknown"

    try:
        git = context.stage("matsim.runtime.git")
        path = os.path.dirname(os.path.realpath(__file__))
        commit = matsim.runtime.git.run(context, ["rev-parse", "HEAD"], cwd = path, catch_output = True)
    except sp.CalledProcessError:
        pass # Probably code was not cloned, but downloaded as a ZIP

    with open(get_version_path()) as f:
        version = f.read().strip()

    # Write meta information
    information = dict(
        sampling_rate = context.config("sampling_rate"),
        hts = context.config("hts"),
        random_seed = context.config("random_seed"),
        created = datetime.datetime.now(datetime.timezone.utc).isoformat(),
        version = version,
        commit = commit
    )

    with open("%s/%smeta.json" % (context.config("output_path"), context.config("output_prefix")), "w+") as f:
        json.dump(information, f, indent = 4)

def validate(context):
    with open(get_version_path()) as f:
        return f.read().strip()
