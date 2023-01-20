import pandas as pd
import numpy as np
import os

"""
This stage updates the census weights to correspond to persona-based scenarios
"""

def configure(context):
    context.stage("data.census.filtered")

    context.config("personas.scenarios_path")
    context.config("personas.scenario", "none")

def execute(context):
    df_census = context.stage("data.census.filtered").sort_values(by = "household_id").copy()
    
    scenario = context.config("personas.scenario")

    if scenario == "none":
        return df_census

    # Load scenario data
    df_scenario = pd.read_excel(
        "%s/%s" % (context.config("data_path"), context.config("personas.scenarios_path")),
        sheet_name="Weights")
    
    df_scenario = df_scenario[["Persona", scenario]]
    df_scenario = df_scenario.rename(columns = { 
        "Persona": "persona",
        scenario: "scenario_share" 
    })
    assert len(df_scenario) > 0

    # Perform weighting
    df_households = df_census.groupby(["household_id", "persona"]).size().reset_index(name = "members")
    df_households = pd.merge(df_households, df_census[["household_id", "weight"]].drop_duplicates(
        "household_id", keep = "first"), on = "household_id")

    threshold = 1e-6
    print("Weighting households for personas ...")

    for iteration in range(0, 100):
        differences = []

        for __, row in df_scenario.iterrows():
            f_persona = df_households["persona"] == row["persona"]
            df_selection = df_households[f_persona]

            total_count = np.sum(df_households["members"] * df_households["weight"])
            persona_count = np.sum(df_selection["members"] * df_selection["weight"])

            current_weight = persona_count / total_count
            target_weight = row["scenario_share"]
            differences.append(current_weight - target_weight)

            f_household = df_households["household_id"].isin(df_selection["household_id"])
            df_households.loc[f_household, "weight"] *= target_weight / current_weight

        mismatch = np.sum(np.abs(differences))
        print("  Mismatch after iteration {}:".format(iteration), mismatch)

        if mismatch < threshold:
            break

    # Re-apply weights
    df_census = df_census.drop(columns = "weight")
    df_census = pd.merge(df_census, df_households[[
         "household_id", "weight"]].drop_duplicates("household_id"), on = "household_id")

    return df_census

def validate(context):
    if not os.path.exists("%s/%s" % (context.config("data_path"), context.config("personas.scenarios_path"))):
        raise RuntimeError("Persona scenario data is not available")

    return os.path.getsize("%s/%s" % (context.config("data_path"), context.config("personas.scenarios_path")))
