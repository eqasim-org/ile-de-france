import data.spatial.utils as spatial_utils
import numpy as np
import pandas as pd
import geopandas as gpd

def configure(context):
    context.stage("synthesis.population.spatial.home.zones")
    context.stage("synthesis.locations.home")

    context.config("random_seed")

def _sample_locations(context, args):
    iris_id, random_seed = args
    df_locations = context.data("df_locations")
    df_homes = context.data("df_homes")

    random = np.random.RandomState(random_seed)

    df_homes = df_homes[df_homes["iris_id"] == iris_id].copy()
    df_locations = df_locations[df_locations["iris_id"] == iris_id].copy()

    home_count = len(df_homes)
    location_count = len(df_locations)

    assert location_count > 0
    assert home_count > 0

    indices = random.randint(location_count, size = home_count)
    df_homes["geometry"] = df_locations.iloc[indices]["geometry"].values

    context.progress.update()
    return df_homes

def execute(context):
    random = np.random.RandomState(context.config("random_seed"))

    df_homes = context.stage("synthesis.population.spatial.home.zones")
    df_locations = context.stage("synthesis.locations.home")

    # Sample locations for home

    unique_iris_ids = set(df_homes["iris_id"].unique())

    with context.progress(label = "Sampling home locations ...", total = len(unique_iris_ids)) as progress:
        with context.parallel(dict(
            df_locations = df_locations, df_homes = df_homes
        )) as parallel:
            seeds = random.randint(10000, size = len(unique_iris_ids))
            df_homes = pd.concat(parallel.map(_sample_locations, zip(unique_iris_ids, seeds)))

    df_homes = gpd.GeoDataFrame(df_homes, crs = "EPSG:2154")
    return df_homes[["household_id", "commune_id", "geometry"]]
