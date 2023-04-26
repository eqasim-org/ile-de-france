import data.spatial.utils as spatial_utils
import numpy as np
import pandas as pd
import geopandas as gpd

def configure(context):
    context.stage("synthesis.population.spatial.home.zones")
    context.stage("synthesis.locations.home")
    context.stage("data.spatial.codes")
    context.config("random_seed")

def _sample_locations(context, args):

    iris_id, random_seed = args
    df_locations = context.data("df_locations")
    df_homes = context.data("df_homes")

    df_homes = df_homes[df_homes["iris_id"] == iris_id].copy()
    df_locations = df_locations[df_locations["iris_id"] == iris_id].copy()

    home_count = len(df_homes)
    location_count = len(df_locations)

    assert location_count > 0
    assert home_count > 0
    
    # random = np.random.RandomState(random_seed)

    #cdf = np.cumsmum(df_locations["weight"])
    #cdf /= cdf[-1]

    #indices = [
    #       np.count_nonzero(cdf < u) 
    #       for u in random.random(0, 1, size = home_count)]

    # normalize IRIS residences weights
    residences_weights  = df_locations["weight"]/df_locations["weight"].sum()
    residences_weights = residences_weights.to_numpy()
    
    # weighted draw
    indices = np.random.default_rng(random_seed).choice(np.arange(len(df_locations)), size=home_count,p=residences_weights)

    # uniform draw
    # random = np.random.RandomState(random_seed)
    # indices = random.randint(location_count, size = home_count)

    # apply selection
    df_homes["geometry"] = df_locations.iloc[indices]["geometry"].values
    df_homes["building_id"] = df_locations.iloc[indices]["building_id"].values
    
    context.progress.update()
    return df_homes

def execute(context):
    
    df_codes = context.stage("data.spatial.codes")

    random = np.random.RandomState(context.config("random_seed"))

    df_homes = context.stage("synthesis.population.spatial.home.zones")
    df_locations = context.stage("synthesis.locations.home")
                   
    # Sample locations for home
    unique_iris_ids = sorted(set(df_homes["iris_id"].unique()))

    with context.progress(label = "Sampling home locations ...", total = len(unique_iris_ids)) as progress:
        with context.parallel(dict(
            df_locations = df_locations, df_homes = df_homes
        )) as parallel:
            seeds = random.randint(10000, size = len(unique_iris_ids))
            df_homes = pd.concat(parallel.map(_sample_locations, zip(unique_iris_ids, seeds)))

    df_homes = gpd.GeoDataFrame(df_homes, crs = "EPSG:2154")
    return df_homes[["household_id", "commune_id", "geometry", "building_id"]]
