import data.spatial.utils as spatial_utils
import numpy as np
import pandas as pd
import geopandas as gpd

def configure(context):
    context.stage("synthesis.population.spatial.home.zones")
    context.stage("synthesis.locations.home.locations")

    context.config("random_seed")
    context.config("home_location_sampling", "weighted")

def _sample_locations(context, args):
    # Extract data sets
    df_locations = context.data("df_locations")
    df_homes = context.data("df_homes")
    sampling_mode = context.data("sampling_mode")

    # Extract task parameters
    iris_id, random_seed = args

    # Select home candidates and locations for the selected IRIS
    df_homes = df_homes[df_homes["iris_id"] == iris_id].copy()
    df_locations = df_locations[df_locations["iris_id"] == iris_id].copy()

    # Verify counts
    home_count = len(df_homes)
    location_count = len(df_locations)

    assert location_count > 0
    assert home_count > 0

    # Perform sampling
    random = np.random.RandomState(random_seed)

    if sampling_mode == "weighted":
        cdf = np.cumsmum(df_locations["weight"].values)
        cdf /= cdf[-1]

        indices = np.array([np.count_nonzero(cdf < u) 
            for u in random.random(0.0, 1.0, size = home_count)])
    elif sampling_mode == "uniform":
        indices = random.randint(location_count, size = home_count)
    else:
        raise RuntimeError("Unknown sampling mode")
    
    # Apply selection
    df_homes["geometry"] = df_locations.iloc[indices]["geometry"].values
    df_homes["building_id"] = df_locations.iloc[indices]["building_id"].values
    
    # Update progress
    context.progress.update()

    return gpd.GeoDataFrame(df_homes, crs = df_locations.crs)

def execute(context):
    random = np.random.RandomState(context.config("random_seed"))

    df_homes = context.stage("synthesis.population.spatial.home.zones")
    df_locations = context.stage("synthesis.locations.home.locations")
                   
    # Sample locations for home
    unique_iris_ids = sorted(set(df_homes["iris_id"].unique()))

    with context.progress(label = "Sampling home locations ...", total = len(unique_iris_ids)):
        with context.parallel(dict(
            df_locations = df_locations, df_homes = df_homes, sampling_mode = context.config("home_location_sampling")
        )) as parallel:
            seeds = random.randint(10000, size = len(unique_iris_ids))
            df_homes = pd.concat(parallel.map(_sample_locations, zip(unique_iris_ids, seeds)))

    return df_homes[["household_id", "commune_id", "building_id", "geometry"]]

def validate(context):
    assert context.config("home_location_sampling") in ("weighted", "uniform")
