import data.spatial.zones
import data.spatial.utils
import numpy as np

def configure(context):
    context.stage("synthesis.population.spatial.home.zones")
    context.stage("data.spatial.zones")

    context.config("random_seed")

def execute(context):
    random = np.random.RandomState(context.config("random_seed"))

    df_homes = context.stage("synthesis.population.spatial.home.zones")
    df_zones = context.stage("data.spatial.zones")

    # Sample destinations for home
    data.spatial.zones.sample_coordinates(context, df_zones, df_homes, random, label = "Sampling coordinates ...")
    df_homes = data.spatial.utils.to_gpd(context, df_homes)

    return df_homes[["household_id", "commune_id", "geometry"]]
