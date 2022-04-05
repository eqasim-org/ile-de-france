import pandas as pd
import Levenshtein
import tqdm
import numpy as np
import geopandas as gpd

def configure(context):
    context.config("lead_path")
    context.config("lead_year")

def execute(context):
    df_additional = pd.DataFrame({ "geometry": [] })

    if context.config("lead_year") == 2030:
        df_additional = gpd.read_file("%s/new_addresses.gpkg" % context.config("lead_path"))
        df_additional = df_additional[["geometry"]]

    return df_additional
