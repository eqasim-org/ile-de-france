import numpy as np
import pandas as pd
import os

"""
Loads aggregate population data for Île-de-France.
"""

def configure(context):
    context.config("data_path")

def execute(context):
    df_population = pd.read_excel(
        "%s/rp_2015/base-ic-evol-struct-pop-2015.xls" % context.config("data_path"),
        skiprows = 5, sheet_name = "IRIS"
    )[["REG", "DEP", "COM", "IRIS", "P15_POP"]]

    df_population.columns = ["region_id", "departement_id", "commune_id", "iris_id", "population"]
    df_population = df_population[df_population["region_id"] == 11]

    return df_population

def validate(context):
    if not os.path.exists("%s/rp_2015/base-ic-evol-struct-pop-2015.xls" % context.config("data_path")):
        raise RuntimeError("Aggregated census data is not available")

    return os.path.getsize("%s/rp_2015/base-ic-evol-struct-pop-2015.xls" % context.config("data_path"))
