import pandas as pd
import Levenshtein
import tqdm
import numpy as np
import geopandas as gpd

"""
Often, we need localized SIRENE data in losely related projects. This stage
makes it easy to extract the data set from the pipeline.
"""

def configure(context):
    context.stage("data.sirene.localized")

    context.config("output_path")
    context.config("output_prefix", "ile_de_france_")

def execute(context):
    df_sirene = context.stage("data.sirene.localized")
    df_sirene["commune"] = df_sirene["commune"].astype(str)

    df_sirene.to_file("%s/%ssirene.gpkg" % (
        context.config("output_path"), context.config("output_prefix")), driver = "GPKG")
