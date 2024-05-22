import pandas as pd
import numpy as np
import os

"""
This stage updates the census weights to correspond to persona-based scenarios
"""

def configure(context):
    context.stage("data.census.personas")

    context.config("personas.scenarios_path")
    context.config("personas.scenario", "none")

def execute(context):
    df_census = context.stage("data.census.personas")

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

    # Prepare indexing
    df_households = df_census[["household_id", "household_size", "weight"]].drop_duplicates("household_id")
    df_households["household_index"] = np.arange(len(df_households))
    df_census = pd.merge(df_census, df_households[["household_id", "household_index"]])

    # Obtain weights and sizes as arrays
    household_weights = df_households["weight"].values
    household_sizes = df_households["household_size"].values

    # Obtain the attribute levels and membership of attributes for all households
    attribute_membership = []
    attribute_counts = []
    attribute_targets = []

    # Process personas
    for persona, target_share in zip(df_scenario["persona"], df_scenario["scenario_share"]):
        f = df_census["persona"] == persona

        df_counts = df_census.loc[f, "household_index"].value_counts()
        
        attribute_targets.append(target_share * df_census["weight"].sum())
        attribute_membership.append(df_counts.index.values)
        attribute_counts.append(df_counts.values)
    
    # Process total
    attribute_targets.append(df_census["weight"].sum())
    attribute_membership.append(np.arange(len(household_sizes))) # all
    attribute_counts.append(household_sizes)

    # Perform IPU to obtain update weights
    update = np.ones((len(df_households),))

    minimum_factors = []
    maximum_factors = []

    print(df_census["persona"].value_counts().sort_index())

    for iteration in range(100):
        factors = []    
        for k in np.arange(len(attribute_targets)):
            selection = attribute_membership[k]
        
            target = attribute_targets[k]
            current = np.sum(update[selection] * household_weights[selection] * attribute_counts[k])
        
            factor = target / current
            factors.append(factor)
                
            update[selection] *= factor

        minimum_factors.append(np.min(factors))
        maximum_factors.append(np.max(factors))

        print(
            "IPU", "it={}".format(iteration), 
            "min={}".format(np.min(factors)),
            "max={}".format(np.max(factors))
        )

        if np.max(factors) - np.min(factors) < 1e-3:
            break

    # Update the weights
    df_households["weight"] *= update
    
    # Re-apply weights
    df_census = df_census.drop(columns = "weight")
    df_census = pd.merge(df_census, df_households[[
         "household_id", "weight"]].drop_duplicates("household_id"), on = "household_id")

    return df_census

def validate(context):
    if not os.path.exists("%s/%s" % (context.config("data_path"), context.config("personas.scenarios_path"))):
        raise RuntimeError("Persona scenario data is not available")

    return os.path.getsize("%s/%s" % (context.config("data_path"), context.config("personas.scenarios_path")))
