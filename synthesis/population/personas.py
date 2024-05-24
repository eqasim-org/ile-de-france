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
    
    # Prepare indexing
    df_households = df_census[["household_id", "household_size", "weight"]].drop_duplicates("household_id")
    df_households["household_index"] = np.arange(len(df_households))
    df_census = pd.merge(df_census, df_households[["household_id", "household_index"]])

    # Obtain weights and sizes as arrays
    household_weights = df_households["weight"].values
    household_sizes = df_households["household_size"].values

    # Obtain the attribute levels and membership of attributes for all households
    attributes = []

    attribute_membership = []
    attribute_counts = []
    attribute_targets = []

    ### PROJECTION PART
    # Actually, we don't perform a weighting here (already in previous step)
    # But we keep the values constant

    # Proccesing age ...
    df_marginal = df_census.groupby("age")["weight"].sum().reset_index(name = "projection")
    for index, row in context.progress(df_marginal.iterrows(), label = "Processing attribute: age", total = len(df_marginal)):
        f = df_census["age"] == row["age"]

        if np.count_nonzero(f) == 0:
            print("Did not find age:", row["age"])

        else:
            df_counts = df_census.loc[f, "household_index"].value_counts()
        
            attribute_targets.append(row["projection"])
            attribute_membership.append(df_counts.index.values)
            attribute_counts.append(df_counts.values)
            attributes.append("age={}".format(row["age"]))
    
    # Processing sex ...
    df_marginal = df_census.groupby("sex")["weight"].sum().reset_index(name = "projection")
    for index, row in context.progress(df_marginal.iterrows(), label = "Processing attribute: sex", total = len(df_marginal)):
        f = df_census["sex"] == row["sex"]
        
        if np.count_nonzero(f) == 0:
            print("Did not find sex:", row["sex"])

        else:
            df_counts = df_census.loc[f, "household_index"].value_counts()
        
            attribute_targets.append(row["projection"])
            attribute_membership.append(df_counts.index.values)
            attribute_counts.append(df_counts.values)
            attributes.append("sex={}".format(row["sex"]))

    # Processing age x sex ...
    df_marginal = df_census.groupby(["age", "sex"])["weight"].sum().reset_index(name = "projection")
    for index, row in context.progress(df_marginal.iterrows(), label = "Processing attributes: sex x age", total = len(df_marginal)):
        f = (df_census["sex"] == row["sex"]) & (df_census["age"] == row["age"])

        if row["age"] == 0:
            continue
        
        if np.count_nonzero(f) == 0:
            print("Did not find values:", row["sex"], row["age"])

        else:
            df_counts = df_census.loc[f, "household_index"].value_counts()
        
            attribute_targets.append(row["projection"])
            attribute_membership.append(df_counts.index.values)
            attribute_counts.append(df_counts.values)
            attributes.append("sex={},age={}".format(row["sex"], row["age"]))

    # Processing total ...
    projection_total = df_marginal = df_census["weight"].sum()
    attribute_targets.append(projection_total)
    attribute_membership.append(np.arange(len(household_sizes)))
    attribute_counts.append(household_sizes)
    attributes.append("total")

    ### PERSONA PART
    if scenario != "Projection":
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

        # The persons contain personas 0-15, here we get 1-16, so we need to adjust
        df_scenario["persona"] -= 1

        # Process personas
        for persona, target_share in zip(df_scenario["persona"], df_scenario["scenario_share"]):
            f = df_census["persona"] == persona

            df_counts = df_census.loc[f, "household_index"].value_counts()
            
            attribute_targets.append(target_share * projection_total)
            attribute_membership.append(df_counts.index.values)
            attribute_counts.append(df_counts.values)
            attributes.append("persona:{}".format(persona))

        df_scenario = pd.read_excel(
            "%s/%s" % (context.config("data_path"), context.config("personas.scenarios_path")),
            sheet_name="Results")
        
        df_scenario = df_scenario[df_scenario["Scenario"] == scenario].copy()
        
        # Process location type attribute
        df_values = df_scenario[df_scenario["Attribute"] == "Location"][["Value", "Target"]].copy()
        df_values["Value"] = df_values["Value"].replace({ "nA": "-1"}).astype(int)
        # TODO: Rather fix this in the input!
        df_values["Target"] = df_values["Target"] / df_values["Target"].sum()

        for value, target_share in zip(df_values["Value"], df_values["Target"]):
            f = df_census["location_type"] == value

            df_counts = df_census.loc[f, "household_index"].value_counts()

            print("location_type=", value, "target=", target_share, "initial=", df_census.loc[f, "weight"].sum() / df_census["weight"].sum())

            attribute_targets.append(target_share * projection_total)
            attribute_membership.append(df_counts.index.values)
            attribute_counts.append(df_counts.values)
            attributes.append("location_type:{}".format(value))

    # Perform IPU to obtain update weights
    update = np.ones((len(df_households),))

    minimum_factors = []
    maximum_factors = []

    print("running IPU with", len(attributes), "attributes")
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
