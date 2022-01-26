import pandas as pd
import os
import numpy as np

"""
This stage loads the raw data from the French enterprise registry.
"""

def configure(context):
    context.config("data_path")
    context.config("siren_path", "sirene/StockUniteLegale_utf8.zip")

    context.stage("data.sirene.raw_siret")

def execute(context):
    relevant_siren = context.stage("data.sirene.raw_siret")["siren"].unique()

    df_siren = pd.read_csv("%s/%s" % (context.config("data_path"), context.config("siren_path")), usecols = [
            "siren", "categorieJuridiqueUniteLegale"
        ],
        dtype = dict(siren = int, categorieJuridiqueUniteLegale = int)
    )

    df_siren = df_siren[
        df_siren["siren"].isin(relevant_siren)
    ]

    return df_siren

def validate(context):
    if not os.path.exists("%s/%s" % (context.config("data_path"), context.config("siren_path"))):
        raise RuntimeError("SIRENE: SIREN data is not available")

    return os.path.getsize("%s/%s" % (context.config("data_path"), context.config("siren_path")))
