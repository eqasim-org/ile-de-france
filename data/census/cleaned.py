from tqdm import tqdm
import pandas as pd
import numpy as np
import data.hts.hts as hts

"""
This stage cleans the French population census:
  - Assign new unique integer IDs to households and persons
  - Clean up spatial information and sociodemographic attributes
"""

def configure(context):
    context.stage("data.census.raw")

def execute(context):
    df = pd.read_hdf("%s/census.hdf" % context.path("data.census.raw"))

    # Construct household IDs for persons with NUMMI != Z
    df_household_ids = df[["CANTVILLE", "NUMMI"]]
    df_household_ids = df_household_ids[df_household_ids["NUMMI"] != "Z"]
    df_household_ids["temporary"] = df_household_ids["CANTVILLE"] + df_household_ids["NUMMI"]
    df_household_ids = df_household_ids.drop_duplicates("temporary")
    df_household_ids["household_id"] = np.arange(len(df_household_ids))
    df = pd.merge(df, df_household_ids, on = ["CANTVILLE", "NUMMI"], how = "left")

    # Fill up undefined household ids (those where NUMMI == Z)
    f = np.isnan(df["household_id"])
    df.loc[f, "household_id"] = np.arange(np.count_nonzero(f)) + df["household_id"].max()
    df["household_id"] = df["household_id"].astype(np.int)

    # Put person IDs
    df["person_id"] = np.arange(len(df))

    # Sorting
    df = df.sort_values(by = ["household_id", "person_id"])

    # Spatial information
    df["iris_id"] = pd.to_numeric(df["IRIS"], errors = "coerce").fillna(-1).astype(np.int)
    df["triris_id"] = pd.to_numeric(df["TRIRIS"], errors = "coerce").fillna(-1).astype(np.int)
    df["commune_id"] = pd.to_numeric(df["IRIS"].str[:5], errors = "coerce").fillna(-1).astype(np.int)
    df["departement_id"] = df["DEPT"].astype(np.int)

    df["has_iris"] = df["iris_id"] != -1
    df["has_commune"] = df["commune_id"] != -1

    # Age
    df["age"] = df["AGED"].apply(lambda x: "0" if x == "000" else x.lstrip("0")).astype(np.int)

    # Clean COUPLE
    df["couple"] = df["COUPLE"] == "1"

    # Clean TRANS
    df.loc[df["TRANS"] == "1", "commute_mode"] = np.nan
    df.loc[df["TRANS"] == "2", "commute_mode"] = "walk"
    df.loc[df["TRANS"] == "3", "commute_mode"] = "bike"
    df.loc[df["TRANS"] == "4", "commute_mode"] = "car"
    df.loc[df["TRANS"] == "5", "commute_mode"] = "pt"
    df.loc[df["TRANS"] == "Z", "commute_mode"] = np.nan
    df["commute_mode"] = df["commute_mode"].astype("category")

    # Weight
    df["weight"] = df["IPONDI"].astype(np.float)

    # Clean SEXE
    df.loc[df["SEXE"] == "1", "sex"] = "male"
    df.loc[df["SEXE"] == "2", "sex"] = "female"
    df["sex"] = df["sex"].astype("category")

    # Clean employment
    df["employed"] = df["TACT"] == "11"

    # Studies
    df["studies"] = df["ETUD"] == "1"

    # Number of vehicles
    df["number_of_vehicles"] = df["VOIT"].apply(
        lambda x: str(x).replace("Z", "0").replace("X", "0")
    ).astype(np.int)

    df["number_of_vehicles"] += df["DEROU"].apply(
        lambda x: str(x).replace("U", "0").replace("Z", "0").replace("X", "0")
    ).astype(np.int)

    # Household size
    df_size = df[["household_id"]].groupby("household_id").size().reset_index(name = "household_size")
    df = pd.merge(df, df_size)

    # Socioprofessional category
    df["socioprofessional_class"] = df["CS1"].astype(np.int)

    # Place of work or education
    df["work_outside_idf"] = df["ILT"].isin(("4", "5", "6"))
    df["education_outside_idf"] = df["ILETUD"].isin(("4", "5", "6"))

    # Consumption units
    df = pd.merge(df, hts.calculate_consumption_units(df), on = "household_id")

    return df[[
        "person_id", "household_id", "weight",
        "iris_id", "triris_id", "departement_id",
        "age", "sex", "couple",
        "commute_mode", "employed",
        "studies", "number_of_vehicles", "household_size",
        "commune_id", "work_outside_idf", "education_outside_idf",
        "has_commune", "has_iris", "consumption_units", "socioprofessional_class"
    ]]
