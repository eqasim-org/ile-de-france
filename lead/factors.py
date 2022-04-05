import numpy as np
import pandas as pd

def configure(context):
    context.stage("data.spatial.codes")
    context.config("lead_path")

def execute(context):
    df_codes = context.stage("data.spatial.codes")

    # Find growth factor for the requested year
    df_growth = pd.read_excel("%s/projections_scenario_central.xls" % context.config("lead_path"))
    df_growth = df_growth[df_growth["code_Departements"].isin(df_codes["departement_id"])]
    df_growth["factor_2022"] = df_growth["pop_2022"] / df_growth["pop_2015"]
    df_growth["factor_2030"] = df_growth["pop_2030"] / df_growth["pop_2022"]
    df_growth = df_growth.rename(columns = { "code_Departements": "departement_id" })
    df_growth = df_growth[["departement_id", "factor_2022", "factor_2030"]]

    print(df_growth)

    return df_growth
