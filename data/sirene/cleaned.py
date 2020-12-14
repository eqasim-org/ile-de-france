import pandas as pd
import data.spatial.code_changes as cc

"""
Clean the SIRENE enterprise census.
"""

def configure(context):
    context.stage("data.sirene.raw", ephemeral = True)
    context.stage("data.spatial.codes")

def execute(context):
    df_sirene = context.stage("data.sirene.raw")

    # Remove inactive enterprises
    df_sirene = df_sirene[
        df_sirene["etatAdministratifEtablissement"] == "A"
    ]

    # Define work place weights by person under salary ....
    df_sirene["employees"] = 0.0

    df_sirene.loc[df_sirene["trancheEffectifsEtablissement"] == "01", "employees"] = 2
    df_sirene.loc[df_sirene["trancheEffectifsEtablissement"] == "02", "employees"] = 5
    df_sirene.loc[df_sirene["trancheEffectifsEtablissement"] == "03", "employees"] = 9
    df_sirene.loc[df_sirene["trancheEffectifsEtablissement"] == "11", "employees"] = 19
    df_sirene.loc[df_sirene["trancheEffectifsEtablissement"] == "12", "employees"] = 49
    df_sirene.loc[df_sirene["trancheEffectifsEtablissement"] == "21", "employees"] = 99
    df_sirene.loc[df_sirene["trancheEffectifsEtablissement"] == "22", "employees"] = 199
    df_sirene.loc[df_sirene["trancheEffectifsEtablissement"] == "31", "employees"] = 249
    df_sirene.loc[df_sirene["trancheEffectifsEtablissement"] == "32", "employees"] = 499
    df_sirene.loc[df_sirene["trancheEffectifsEtablissement"] == "41", "employees"] = 999
    df_sirene.loc[df_sirene["trancheEffectifsEtablissement"] == "42", "employees"] = 1999
    df_sirene.loc[df_sirene["trancheEffectifsEtablissement"] == "51", "employees"] = 4999
    df_sirene.loc[df_sirene["trancheEffectifsEtablissement"] == "52", "employees"] = 9999
    df_sirene.loc[df_sirene["trancheEffectifsEtablissement"] == "53", "employees"] = 10000

    # ... and filter thme if nobody is working
    df_sirene = df_sirene[df_sirene["employees"] > 0].copy()

    # Add activity classification
    df_sirene["ape"] = df_sirene["activitePrincipaleEtablissement"]

    # Check communes
    df_sirene["commune_id"] = df_sirene["codeCommuneEtablissement"].astype("category")

    df_codes = context.stage("data.spatial.codes")
    requested_communes = set(df_codes["commune_id"].unique())
    excess_communes = set(df_sirene["commune_id"].unique()) - requested_communes

    if len(excess_communes) > 0:
        print(excess_communes)
        raise RuntimeError("Found excess municipalities in SIRENE data")

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

    df_sirene = df_sirene[["commune_id", "employees", "street", "number", "ape", "siret"]]

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

    return df_sirene
