import pandas as pd
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
    df_census = df_census.rename(columns = { "weight": "base_weight" })

    df_scenario = pd.read_excel(
        "%s/%s" % (context.config("data_path"), context.config("personas.scenarios_path")),
        sheet_name="Weights")
    
    df_scenario = df_scenario[["Persona", scenario]]
    df_scenario = df_scenario.rename(columns = { 
        "Persona": "persona",
        scenario: "scenario_share" 
    })
    assert len(df_scenario) > 0

    # Establish inflation / deflation factor per persona dependent on scenario
    df_shares = df_census.groupby("persona")["base_weight"].sum().reset_index()
    df_shares["base_share"] = df_shares["base_weight"] / df_shares["base_weight"].sum()
    df_shares = pd.merge(df_shares, df_scenario, on = "persona")

    df_shares["scenario_factor"] = df_shares["scenario_share"] / df_shares["base_share"]

    # Modify the population weights
    df_census = pd.merge(df_census, df_shares[["persona", "scenario_factor"]], on = "persona")
    df_census["weight"] = df_census["base_weight"] * df_census["scenario_factor"]

    # Cleanup
    df_census = df_census.drop(columns = ["base_weight", "scenario_factor"])
    return df_census

def validate(context):
    if not os.path.exists("%s/%s" % (context.config("data_path"), context.config("personas.scenarios_path"))):
        raise RuntimeError("Persona scenario data is not available")

    return os.path.getsize("%s/%s" % (context.config("data_path"), context.config("personas.scenarios_path")))
