import pandas as pd
import os
import numpy as np

"""
This stage loads the raw data from the French enterprise registry.
"""

def configure(context):
    context.config("data_path")
    context.config("siret_path", "sirene/StockEtablissement_utf8.zip")

    context.stage("data.spatial.codes")

def execute(context):
    df_siret = pd.read_csv("%s/%s" % (context.config("data_path"), context.config("siret_path")), usecols = [
            "siren", "siret", "codeCommuneEtablissement", "activitePrincipaleEtablissement",
            "trancheEffectifsEtablissement", "libelleVoieEtablissement", "numeroVoieEtablissement",
            "typeVoieEtablissement", "etatAdministratifEtablissement"
        ],
        dtype = dict(siren = int, siret = int, codeCommuneEtablissement = str, trancheEffectifsEtablissement = str, typeVoieEtablissement = str)
    )

    # Filter by departement
    df_codes = context.stage("data.spatial.codes")
    requested_departements = set(df_codes["departement_id"].unique())

    f = df_siret["codeCommuneEtablissement"].isna() # Just to get a mask

    for departement in requested_departements:
        print("Finding municipalities for departement %s" % departement)
        f |= df_siret["codeCommuneEtablissement"].str.startswith(departement)

    f &= ~df_siret["codeCommuneEtablissement"].isna()
    df_siret = df_siret[f]

    return df_siret

def validate(context):
    if not os.path.exists("%s/%s" % (context.config("data_path"), context.config("siret_path"))):
        raise RuntimeError("SIRENE: SIRET data is not available")

    return os.path.getsize("%s/%s" % (context.config("data_path"), context.config("siret_path")))
