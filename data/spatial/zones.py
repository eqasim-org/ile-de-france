import numpy as np
import pandas as pd
import geopandas as gpd
from sklearn.neighbors import KDTree
from tqdm import tqdm
import shapely.geometry as geo
import multiprocessing as mp

"""
Combined municiaplities, IRIS and departement information into one consistent
data set. Also attaches population size to each of the zones. Provides various
functions to ease the work with zoning data.
"""

def configure(context):
    context.stage("data.spatial.population")
    context.stage("data.spatial.iris")

def translate_zone_ids(df_zones, df, identifier):
    assert "has_iris" in df
    assert "iris_id" in df
    assert "commune_id" in df
    assert not "zone_id" in df

    return pd.concat([
        pd.merge(
            df[~df["has_iris"]],
            df_zones[df_zones["zone_level"] == "commune"][["zone_id", "commune_id"]],
            on = "commune_id", how = "inner"
        )[[identifier, "zone_id"]],
        pd.merge(
            df[df["has_iris"]],
            df_zones[df_zones["zone_level"] == "iris"][["zone_id", "iris_id"]],
            on = "iris_id", how = "inner"
        )[[identifier, "zone_id"]]
    ])

def sample_coordinate_from_shape(shape, count, random, sample_size = None):
    points = []

    if sample_size is None:
        sample_size = int(1.3 * count)

    while len(points) < count:
        minx, miny, maxx, maxy = shape.bounds
        candidates = random.random_sample(size = (sample_size, 2))
        candidates[:,0] = minx + candidates[:,0] * (maxx - minx)
        candidates[:,1] = miny + candidates[:,1] * (maxy - miny)
        candidates = [geo.Point(*point) for point in candidates]
        candidates = [point for point in candidates if shape.contains(point)]
        points += candidates

    return np.array([(point.x, point.y) for point in points[:count]])

def _sample_coordinates(context, args):
    zone_id, random_seed = args

    df_zones = context.data("zones")
    zone_ids = context.data("zone_ids")

    random = np.random.RandomState(random_seed)

    zone = df_zones[df_zones["zone_id"] == zone_id]["geometry"].values[0]
    f = zone_ids == zone_id
    coordinates = sample_coordinate_from_shape(zone, np.count_nonzero(f), random)

    return f, coordinates

def sample_coordinates(context, df_zones, df, random, label = "Sampling coordinates ..."):
    assert "zone_id" in df

    zone_ids = df["zone_id"].values
    unique_zone_ids = np.unique(zone_ids)
    random_seeds = random.randint(0, int(1e6), len(zone_ids))

    with context.parallel(dict(zones = df_zones, zone_ids = zone_ids)) as parallel:
        for f, coordinates in context.progress(parallel.imap(_sample_coordinates, zip(unique_zone_ids, random_seeds)), label = label, total = len(unique_zone_ids)):
            df.loc[f, "x"] = coordinates[:, 0]
            df.loc[f, "y"] = coordinates[:, 1]

    return df

def execute(context):
    df_population = context.stage("data.spatial.population")
    df_iris = context.stage("data.spatial.iris")
    assert(len(df_population) == len(df_iris))

    # Join population count and region into IRIS
    df_iris = pd.merge(df_iris, df_population[["iris_id", "population", "region_id"]])

    # Create geometries for communes
    df_communes = df_iris[[
        "commune_id", "geometry", "population"
    ]].dissolve(by = "commune_id", aggfunc = "sum").reset_index()
    df_communes["iris_id"] = df_communes["commune_id"] + "0000"

    # Join departement and region into communes
    df_join = df_iris[["commune_id", "departement_id", "region_id"]].groupby("commune_id").first().reset_index()
    df_communes = pd.merge(df_communes, df_join)

    # Reorder things
    df_iris = df_iris[["region_id", "departement_id", "commune_id", "iris_id", "geometry", "population"]]
    df_communes = df_communes[["region_id", "departement_id", "commune_id", "iris_id", "geometry", "population"]]

    # Count IRIS in communes
    commune_ids_without_iris = df_iris[df_iris["iris_id"].str.endswith("0000")]["commune_id"]
    df_communes["has_iris"] = ~df_communes["commune_id"].isin(commune_ids_without_iris)
    df_communes["zone_level"] = "commune"

    # Remove artificial IRIS
    df_iris = df_iris[~df_iris["iris_id"].str.endswith("0000")]
    df_iris["has_iris"] = True
    df_iris["zone_level"] = "iris"

    # Construct zones
    df_zones = pd.concat([df_communes, df_iris])
    df_zones["zone_level"] = df_zones["zone_level"].astype("category")
    df_zones["zone_id"] = np.arange(len(df_zones))

    # Data types
    df_zones["region_id"] = df_zones["region_id"].astype(np.int)
    df_zones["departement_id"] = df_zones["departement_id"].astype(np.int)
    df_zones["commune_id"] = df_zones["commune_id"].astype(np.int)
    df_zones["iris_id"] = df_zones["iris_id"].astype(np.int)

    return df_zones[[
        "zone_id", "zone_level",
        "region_id", "departement_id", "commune_id", "iris_id", "geometry",
        "population", "has_iris"
    ]]
