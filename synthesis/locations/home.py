import pandas as pd
import Levenshtein
import tqdm
import numpy as np
import geopandas as gpd

"""
This stage provides a list of home places that serve as potential locations for
home activities. They are derived from the BDTOPO address database.

As home locations are assigned by IRIS, we re-assign the IRIS code here for
each address coordinate. Additionally, we create fake locations in IRIS that
are requested by the population, but which have no actual address. TODO: The
reason for that may be that the BDTOPO data and the used zoning system are not
in line with each other (i.e. communes have been merged, IRIS have been re-arranged
, etc.)
"""

def configure(context):
    context.stage("data.bdtopo.cleaned")
    context.stage("synthesis.population.sampled")

def execute(context):
    df_population = context.stage("synthesis.population.sampled")

    required_iris = set(df_population["iris_id"].unique())
    required_communes = set([i[:5] for i in required_iris])

    df_home = context.stage("data.bdtopo.cleaned")[[
        "commune_id", "geometry"
    ]]

    df_home = df_home[df_home["commune_id"].isin(required_communes)].copy()

    # Find missing communes
    missing_communes = required_communes - set(df_home["commune_id"].unique())

    if len(missing_communes) > 0:
        print(missing_communes)
        raise RuntimeError("Some communes are required by the population, but they are not present in address data (BDTOPO)")

    # Assign location IDs

    df_home["location_id"] = np.arange(len(df_home))
    df_home["location_id"] = "home_" + df_home["location_id"].astype(str)

    return df_home
