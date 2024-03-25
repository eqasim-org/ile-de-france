import numpy as np
import pandas as pd
from sklearn.neighbors import KDTree
import os
from data.income.municipality import _read_filosofi_excel, _income_distributions_from_filosofi_ensemble_sheet
from bhepop2.tools import read_filosofi_attributes, filosofi_attributes

"""
Loads and prepares income distributions by municipality and by household attributes (size, type):
- For global distributions (all-all), see income/municipality
- For attribute distributions, read the adequate Filosofi sheet and get the percentiles
"""


def configure(context):
    context.config("data_path")
    context.stage("data.spatial.municipalities")
    context.config("income_year", 19)


def execute(context):
    # get income year used
    year = str(context.config("income_year"))

    # get list of requested commune ids
    df_municipalities = context.stage("data.spatial.municipalities")
    requested_communes = set(df_municipalities["commune_id"].unique())

    # build list of attributes to read from Filosofi
    # for now, we enrich eqasim population based on household size and type
    eqasim_attributes = ["size", "family_comp"]
    attributes = []
    for attr in filosofi_attributes:
        if attr["name"] in eqasim_attributes:
            attributes.append(attr)

    # build full list of sheets
    sheet_list = ["ENSEMBLE"]
    for attribute in attributes:
        sheet_list = sheet_list + [x["sheet"] for x in attribute["modalities"]]

    # read Filosofi sheets
    excel = _read_filosofi_excel(context, sheet_name=sheet_list)

    # read global income distributions with eqasim function (infer missing distributions, etc)
    df = _income_distributions_from_filosofi_ensemble_sheet(excel["ENSEMBLE"], year, df_municipalities)

    # put result in bhepop2 format
    df["attribute"] = "all"
    df["modality"] = "all"
    df.rename(
        columns={
            "q1": "D1",
            "q2": "D2",
            "q3": "D3",
            "q4": "D4",
            "q5": "D5",
            "q6": "D6",
            "q7": "D7",
            "q8": "D8",
            "q9": "D9",
        },
        inplace=True,
    )

    # read attributes
    df_with_attributes = read_filosofi_attributes(excel, year, attributes, requested_communes)

    # add eqasim columns
    df_with_attributes["is_imputed"] = False
    df_with_attributes["is_missing"] = False

    # concat and format result
    df = pd.concat([df, df_with_attributes])
    df = df[["commune_id", "D1", "D2", "D3", "D4", "D5", "D6", "D7", "D8", "D9", "attribute", "modality", "is_imputed", "is_missing", "reference_median"]]

    return df

def validate(context):
    if not os.path.exists("%s/%s" % (context.config("data_path"), context.config("income_com_path"))):
        raise RuntimeError("Filosofi data is not available")

    return os.path.getsize("%s/%s" % (context.config("data_path"), context.config("income_com_path")))
