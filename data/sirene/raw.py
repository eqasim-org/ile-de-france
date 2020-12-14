import pandas as pd
import os
import numpy as np

"""
This stage loads the raw data from the French enterprise registry.
"""

def configure(context):
    context.config("data_path")
    context.config("sirene_path", "sirene/StockEtablissement_utf8.csv")

    context.stage("data.spatial.codes")

def execute(context):
    df_sirene = pd.read_csv("%s/%s" % (context.config("data_path"), context.config("sirene_path")), usecols = [
            "siret", "codeCommuneEtablissement", "activitePrincipaleEtablissement",
            "trancheEffectifsEtablissement", "libelleVoieEtablissement", "numeroVoieEtablissement",
            "typeVoieEtablissement", "etatAdministratifEtablissement"
        ],
        dtype = dict(siret = int, codeCommuneEtablissement = str, trancheEffectifsEtablissement = str, typeVoieEtablissement = str)
    )

    # Filter by departement
    df_codes = context.stage("data.spatial.codes")
    requested_departements = set(df_codes["departement_id"].unique())

    f = df_sirene["codeCommuneEtablissement"].isna() # Just to get a mask

    for departement in requested_departements:
        print("Finding municipalities for departement %s" % departement)
        f |= df_sirene["codeCommuneEtablissement"].str.startswith(departement)

    f &= ~df_sirene["codeCommuneEtablissement"].isna()
    df_sirene = df_sirene[f]

    return df_sirene

def validate(context):
    if not os.path.exists("%s/%s" % (context.config("data_path"), context.config("sirene_path"))):
        raise RuntimeError("SIRENE data is not available")

    return os.path.getsize("%s/%s" % (context.config("data_path"), context.config("sirene_path")))
