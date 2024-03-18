import pandas as pd
import os
import zipfile
import numpy as np

# Loads the input data for the urban type (unité urbain)

def configure(context):
    context.stage("data.spatial.municipalities")

    context.config("data_path")
    context.config("urban_type_path", "uu/UU2020_au_01-01-2023.zip")
    context.config("urban_type_file", "UU2020_au_01-01-2023.xlsx")

def execute(context):
    with zipfile.ZipFile("{}/{}".format(
        context.config("data_path"), context.config("urban_type_path"))) as archive:
        with archive.open(context.config("urban_type_file")) as f:
            df = pd.read_excel(f, sheet_name = "Composition_communale", skiprows = 5)
            
    df = df[["CODGEO", "STATUT_2017"]].copy()
    df = df.set_axis(["commune_id", "type_uu"], axis = "columns")

    # Cities that have districts are not detailed in the UU file, only the whole city is mentioned
    # However the municipalities file details the districts with their respective INSEE codes
    cities_with_districts = {"75056": [str(75101 + i) for i in (range(20))],  # Paris
                             "69123": [str(69001 + i) for i in range(9)],  # Lyon
                             "13055": [str(13201 + i) for i in range(15)]}  # Marseilles

    # Replacing each line of the UU file corresponding to a city with districts by multiple lines one for each districts
    for city_code in cities_with_districts:
        uu_type = df[df["commune_id"] == city_code].iloc[0].loc["type_uu"]
        df.drop(df[df["commune_id"] == city_code].index, inplace=True)
        new_lines = {"commune_id": [district_id for district_id in cities_with_districts[city_code]],
                     "type_uu": [uu_type for i in range(len(cities_with_districts[city_code]))]}
        df = pd.concat([df, pd.DataFrame.from_dict(new_lines)])

    # Clean unités urbaines
    df["type_uu"] = df["type_uu"].replace({"B":"suburb","C":"central_city","I":"isolated_city","H":"none"})
    assert np.all(~df["type_uu"].isna())
    df["type_uu"] = df["type_uu"].astype("category")

    df_municipalities = context.stage("data.spatial.municipalities")
    requested_communes = set(df_municipalities["commune_id"].unique())
    df = df[df["commune_id"].isin(requested_communes)]
    
    return df
