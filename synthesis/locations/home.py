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
    context.stage("data.spatial.iris")

def execute(context):
    # Find required IRIS
    df_iris = context.stage("data.spatial.iris")
    required_iris = set(df_iris["iris_id"].unique())

    # Load all addresses and add IRIS information
    df_addresses = context.stage("data.bdtopo.cleaned")[["geometry"]]

    print("Imputing IRIS into addresses ...")
    df_addresses = gpd.sjoin(df_addresses,
        df_iris[["iris_id", "commune_id", "geometry"]], op = "within")
    del df_addresses["index_right"]

    df_addresses.loc[df_addresses["iris_id"].isna(), "iris_id"] = "unknown"
    df_addresses["iris_id"] = df_addresses["iris_id"].astype("category")

    # Add fake homes for IRIS without addresses
    missing_iris = required_iris - set(df_addresses["iris_id"].unique())

    print("Adding homes at the centroid of %d/%d IRIS without BD-TOPO observations" % (
        len(missing_iris), len(required_iris)))

    df_added = []

    for iris_id in missing_iris:
        centroid = df_iris[df_iris["iris_id"] == iris_id]["geometry"].centroid.iloc[0]

        df_added.append({
            "iris_id": iris_id, "geometry": centroid,
            "commune_id": iris_id[:5]
        })

    df_added = pd.DataFrame.from_records(df_added)

    # Merge together
    df_addresses["fake"] = False
    df_added["fake"] = True

    df_addresses = pd.concat([df_addresses, df_added])

    # Add work identifier
    df_addresses["location_id"] = np.arange(len(df_addresses))
    df_addresses["location_id"] = "home_" + df_addresses["location_id"].astype(str)

    return df_addresses[["location_id", "iris_id", "commune_id", "fake", "geometry"]]
