import pandas as pd
import numpy as np

def configure(context):
    context.stage("cairo.raw.population")
    context.config("sampling_rate")

def execute(context):
    df_persons = context.stage("cairo.raw.population")
    df_persons = df_persons.drop_duplicates("person_id")
    
    # Sampling
    sampling_rate = context.config("sampling_rate")
    df_persons = df_persons.sample(frac = sampling_rate)

    # Manage IDs
    df_persons["census_person_id"] = df_persons["person_id"].values
    df_persons["person_id"] = np.arange(len(df_persons))

    df_persons["census_household_id"] = df_persons["census_person_id"]
    df_persons["household_id"] = df_persons["person_id"]

    df_persons["hts_id"] = df_persons["census_person_id"]

    # Placeholder for household demographics
    df_persons["car_availability"] = df_persons["car_availability"].apply(
        lambda x: "all" if x == 1 else "none")
    
    df_persons["bike_availability"] = "none"
    df_persons["number_of_vehicles"] = (df_persons["car_availability"] == "all").astype(int)
    df_persons["number_of_bikes"] = 0
    df_persons["household_income"] = 0.0

    # Placeholder for person-level sociodemographics
    df_persons["age"] = 99
    df_persons["sex"] = "male"
    df_persons["socioprofessional_class"] = 0
    df_persons["employed"] = False
    df_persons["has_license"] = df_persons["car_availability"] == "all"
    df_persons["has_pt_subscription"] = False

    return df_persons[[
        "household_id", "census_household_id",
        "person_id", "census_person_id", "hts_id",

        "car_availability", "bike_availability",
        "number_of_vehicles", "number_of_bikes",
        "household_income",

        "age", "sex", "socioprofessional_class",
        "employed", "has_license", "has_pt_subscription"
    ]]
 
