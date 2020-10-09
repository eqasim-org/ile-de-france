import fiona
import pandas as pd

"""
Clean up address data.
"""

def configure(context):
    context.stage("data.bdtopo.raw", ephemeral = True)
    context.stage("data.spatial.codes")

def execute(context):
    df_bdtopo = context.stage("data.bdtopo.raw")

    df_bdtopo["commune_id"] = df_bdtopo["commune_id"].astype("category")

    df_codes = context.stage("data.spatial.codes")
    requested_communes = set(df_codes["commune_id"].unique())

    excess_communes = set(df_bdtopo["commune_id"].unique()) - requested_communes
    if len(excess_communes) > 0:
        raise RuntimeError("Excess municipalities in BDTOPO")

    # Clean up street information
    df_bdtopo["street"] = df_bdtopo["raw_street"]
    df_bdtopo["street"] = df_bdtopo["street"].str.replace("2 ", "DEUX ")
    df_bdtopo["street"] = df_bdtopo["street"].str.replace("4 ", "QUATRE ")
    df_bdtopo["street"] = df_bdtopo["street"].str.replace("3 ", "TROIS ")
    df_bdtopo["street"] = df_bdtopo["street"].str.replace("-", " ")
    df_bdtopo["street"] = df_bdtopo["street"].str.replace("'", " ")
    df_bdtopo["street"] = df_bdtopo["street"].str.replace(" ST ", " SAINT ")
    df_bdtopo["street"] = df_bdtopo["street"].str.replace(r"^ST ", "SAINT ")
    df_bdtopo["street"] = df_bdtopo["street"].str.replace(" STE ", " SAINTE ")
    df_bdtopo["street"] = df_bdtopo["street"].str.replace(r"^STE ", "SAINTE ")
    df_bdtopo["street"] = df_bdtopo["street"].str.replace(r"^PLACE ", "PL ")

    df_bdtopo["number"] = pd.to_numeric(df_bdtopo["raw_number"], errors = "coerce")
    df_bdtopo = df_bdtopo[["commune_id", "street", "number", "geometry"]]

    # Filter NaN
    initial_count = len(df_bdtopo)
    df_bdtopo = df_bdtopo.dropna()
    df_bdtopo = df_bdtopo.drop_duplicates(["commune_id", "street", "number"])
    final_count = len(df_bdtopo)

    print("Dropping %.2f%% of addresses because of NaN values or duplicates" % (
        100 * (initial_count - final_count) / initial_count
    ))

    context.set_info("initial_count", initial_count)
    context.set_info("final_count", final_count)

    return df_bdtopo
