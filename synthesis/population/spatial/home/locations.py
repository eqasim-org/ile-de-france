import data.spatial.utils as spatial_utils
import numpy as np

def configure(context):
    context.stage("synthesis.population.spatial.home.zones")
    context.stage("data.spatial.iris")

    context.config("random_seed")

def execute(context):
    random = np.random.RandomState(context.config("random_seed"))

    df_homes = context.stage("synthesis.population.spatial.home.zones")
    df_iris = context.stage("data.spatial.iris")

    # Sample destinations for home

    df_homes[["x", "y"]] = spatial_utils.sample_from_zones(
        context, df_iris, df_homes, "iris_id", random, label = "Imputing IRIS coordinates ...")

    assert not df_homes["x"].isna().any()
    assert not df_homes["y"].isna().any()

    df_homes = spatial_utils.to_gpd(context, df_homes)
    return df_homes[["household_id", "commune_id", "geometry"]]
