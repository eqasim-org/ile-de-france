import pandas as pd
import os
import zipfile
import numpy as np
"""
Loads the "unités urbaines" national file
"""

def configure(context):
    context.stage("data.spatial.municipalities")

    context.config("data_path")
    context.config("uu_path", "uu/UU2020_au_01-01-2023.zip")
    context.config("uu_xlsx", "UU2020_au_01-01-2023.xlsx")

def execute(context):
    with zipfile.ZipFile("{}/{}".format(
        context.config("data_path"), context.config("uu_path"))) as archive:
        with archive.open(context.config("uu_xlsx")) as f:
            df = pd.read_excel(f, sheet_name = "Composition_communale", skiprows = 5)
            
    df = df[["CODGEO","STATUT_2017"]].copy()
    df = df.set_axis(["commune_id","type_uu"],axis='columns')
    
    # Clean unités urbaines    
    df["type_uu"] = df["type_uu"].replace({"B":"suburb","C":"central_city","I":"isolated_city","H":"rural"})
    assert np.all(~df["type_uu"].isna())
    df["type_uu"] = df["type_uu"].astype("category")

    df_municipalities = context.stage("data.spatial.municipalities")
    requested_communes = set(df_municipalities["commune_id"].unique())
    df = df[df["commune_id"].isin(requested_communes)]
    
    return df

