import pandas as pd
import data.spatial.code_changes as cc
import numpy as np

"""
Clean the SIRENE enterprise census.
"""

def configure(context):
    context.stage("data.sirene.raw_siren", ephemeral = True)
    context.stage("data.sirene.raw_siret", ephemeral = True)
    context.stage("data.spatial.codes")

def execute(context):
    df_sirene_establishments = context.stage("data.sirene.raw_siret")
    df_sirene_headquarters = context.stage("data.sirene.raw_siren")

    # Filter out establishments without a corresponding headquarter
    df_sirene = df_sirene_establishments[df_sirene_establishments["siren"].isin(df_sirene_headquarters["siren"])].copy()

    # Remove inactive enterprises
    df_sirene = df_sirene[
        df_sirene["etatAdministratifEtablissement"] == "A"
    ].copy()

    # Define work place weights by person under salary ....
    df_sirene["minimum_employees"] = 1 # Includes "NN", "00", and NaN
    df_sirene["maximum_employees"] = 1 # Includes "NN", "00", and NaN

    df_sirene.loc[df_sirene["trancheEffectifsEtablissement"] == "01", "minimum_employees"] = 1
    df_sirene.loc[df_sirene["trancheEffectifsEtablissement"] == "01", "maximum_employees"] = 2
    df_sirene.loc[df_sirene["trancheEffectifsEtablissement"] == "02", "minimum_employees"] = 3
    df_sirene.loc[df_sirene["trancheEffectifsEtablissement"] == "02", "maximum_employees"] = 5
    df_sirene.loc[df_sirene["trancheEffectifsEtablissement"] == "03", "minimum_employees"] = 6
    df_sirene.loc[df_sirene["trancheEffectifsEtablissement"] == "03", "maximum_employees"] = 9
    df_sirene.loc[df_sirene["trancheEffectifsEtablissement"] == "11", "minimum_employees"] = 10
    df_sirene.loc[df_sirene["trancheEffectifsEtablissement"] == "11", "maximum_employees"] = 19
    df_sirene.loc[df_sirene["trancheEffectifsEtablissement"] == "12", "minimum_employees"] = 20
    df_sirene.loc[df_sirene["trancheEffectifsEtablissement"] == "12", "maximum_employees"] = 49
    df_sirene.loc[df_sirene["trancheEffectifsEtablissement"] == "21", "minimum_employees"] = 50
    df_sirene.loc[df_sirene["trancheEffectifsEtablissement"] == "21", "maximum_employees"] = 99
    df_sirene.loc[df_sirene["trancheEffectifsEtablissement"] == "22", "minimum_employees"] = 100
    df_sirene.loc[df_sirene["trancheEffectifsEtablissement"] == "22", "maximum_employees"] = 199
    df_sirene.loc[df_sirene["trancheEffectifsEtablissement"] == "31", "minimum_employees"] = 200
    df_sirene.loc[df_sirene["trancheEffectifsEtablissement"] == "31", "maximum_employees"] = 249
    df_sirene.loc[df_sirene["trancheEffectifsEtablissement"] == "32", "minimum_employees"] = 250
    df_sirene.loc[df_sirene["trancheEffectifsEtablissement"] == "32", "maximum_employees"] = 499
    df_sirene.loc[df_sirene["trancheEffectifsEtablissement"] == "41", "minimum_employees"] = 500
    df_sirene.loc[df_sirene["trancheEffectifsEtablissement"] == "41", "maximum_employees"] = 999
    df_sirene.loc[df_sirene["trancheEffectifsEtablissement"] == "42", "minimum_employees"] = 1000
    df_sirene.loc[df_sirene["trancheEffectifsEtablissement"] == "42", "maximum_employees"] = 1999
    df_sirene.loc[df_sirene["trancheEffectifsEtablissement"] == "51", "minimum_employees"] = 2000
    df_sirene.loc[df_sirene["trancheEffectifsEtablissement"] == "51", "maximum_employees"] = 4999
    df_sirene.loc[df_sirene["trancheEffectifsEtablissement"] == "52", "minimum_employees"] = 5000
    df_sirene.loc[df_sirene["trancheEffectifsEtablissement"] == "52", "maximum_employees"] = 9999
    df_sirene.loc[df_sirene["trancheEffectifsEtablissement"] == "53", "minimum_employees"] = 10000
    df_sirene.loc[df_sirene["trancheEffectifsEtablissement"] == "53", "maximum_employees"] = np.inf

    # Add activity classification
    df_sirene["ape"] = df_sirene["activitePrincipaleEtablissement"]

    # Check communes
    df_sirene["commune_id"] = df_sirene["codeCommuneEtablissement"].astype("category")

    df_codes = context.stage("data.spatial.codes")
    requested_communes = set(df_codes["commune_id"].unique())
    excess_communes = set(df_sirene["commune_id"].unique()) - requested_communes

    if len(excess_communes) > 0:
        print("Found excess municipalities in SIRENE data: ", excess_communes)

    if len(excess_communes) > 5:
        raise RuntimeError("Found more than 5 excess municipalities in SIRENE data")

    # Clean up street information
    df_sirene["street_type"] = df_sirene["typeVoieEtablissement"]
    df_sirene["street_type"] = df_sirene["street_type"].str.replace("RUE", "R")
    df_sirene["street_type"] = df_sirene["street_type"].str.replace("QUAI", "QU")
    df_sirene["street_type"] = df_sirene["street_type"].str.replace("PLACE", "PL")

    df_sirene["street"] = df_sirene["libelleVoieEtablissement"]
    df_sirene["street"] = df_sirene["street"].str.replace("'", " ")
    df_sirene["street"] = df_sirene["street"].str.replace("-", " ")
    df_sirene["street"] = df_sirene["street"].str.replace("2 ", "DEUX ")
    df_sirene["street"] = df_sirene["street"].str.replace("4 ", "QUATRE ")
    df_sirene["street"] = df_sirene["street"].str.replace("3 ", "TROIS ")
    df_sirene["street"] = df_sirene["street"].str.replace(" ST ", " SAINT ")
    df_sirene["street"] = df_sirene["street"].str.replace(r"^ST ", "SAINT ")
    df_sirene["street"] = df_sirene["street"].str.replace(" STE ", " SAINTE ")
    df_sirene["street"] = df_sirene["street"].str.replace(r"^STE ", "SAINTE ")
    df_sirene["street"] = df_sirene["street"].str.replace(" PTE ", " PORTE ")
    df_sirene["street"] = df_sirene["street"].str.replace(r"^PLACE ", "PL ")

    df_sirene["street"] = df_sirene["street_type"] + " " + df_sirene["street"]

    df_sirene["number"] = pd.to_numeric(df_sirene["numeroVoieEtablissement"], errors = "coerce")

    df_sirene = df_sirene[["siren", "commune_id", "minimum_employees", "maximum_employees", "street", "number", "ape", "siret"]]

    # Filter out if the information of invalid
    initial_count = len(df_sirene)

    df_sirene = df_sirene.dropna()

    final_count = len(df_sirene)
    print("Filtered out %d/%d (%.2f%%) of enterprises because address is invalid" % (
        initial_count - final_count, initial_count,
        100 * (initial_count - final_count) / initial_count
    ))

    df_sirene["number"] = df_sirene["number"].astype(int)
    df_sirene["street"] = df_sirene["street"].astype(str)

    # Add law status
    initial_count = len(df_sirene)

    df_sirene = pd.merge(df_sirene, df_sirene_headquarters, on = "siren")

    df_sirene["law_status"] = df_sirene["categorieJuridiqueUniteLegale"]
    df_sirene = df_sirene.drop(columns =  ["categorieJuridiqueUniteLegale", "siren"])

    final_count = len(df_sirene)
    assert initial_count == final_count

    return df_sirene
