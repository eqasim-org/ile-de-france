import numpy as np
import pandas as pd
import os

"""
Loads aggregate population data.
"""

YEAR = 2015
SOURCE = "rp_%d/base-ic-evol-struct-pop-%d.xls" % (YEAR, YEAR)

def configure(context):
    context.config("data_path")
    context.stage("data.spatial.codes")

def execute(context):
    df_population = pd.read_excel(
        "%s/%s" % (context.config("data_path"), SOURCE),
        skiprows = 5, sheet_name = "IRIS", usecols = ["IRIS", "COM", "DEP", "REG", "P15_POP"]
    ).rename(columns = {
        "IRIS": "iris_id", "COM": "commune_id", "DEP": "departement_id", "REG": "region_id",
        "P15_POP": "population"
    })

    df_population["iris_id"] = df_population["iris_id"].astype("category")
    df_population["commune_id"] = df_population["commune_id"].astype("category")
    df_population["departement_id"] = df_population["departement_id"].astype("category")
    df_population["region_id"] = df_population["region_id"].astype(int)

    # Merge into code data and verify integrity
    df_codes = context.stage("data.spatial.codes")
    df_population = pd.merge(df_population, df_codes, on = ["iris_id", "commune_id", "departement_id", "region_id"])

    requested_iris = set(df_codes["iris_id"].unique())
    merged_iris = set(df_population["iris_id"].unique())

    if requested_iris != merged_iris:
        raise RuntimeError("Some IRIS are missing: %s" % (requested_iris - merged_iris,))

    return df_population[["region_id", "departement_id", "commune_id", "iris_id", "population"]]

def validate(context):
    if not os.path.exists("%s/%s" % (context.config("data_path"), SOURCE)):
        raise RuntimeError("Aggregated census data is not available")

    return os.path.getsize("%s/%s" % (context.config("data_path"), SOURCE))
