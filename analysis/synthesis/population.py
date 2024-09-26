import itertools
import numba

import numpy as np
import pandas as pd
from  analysis.marginals import NUMBER_OF_VEHICLES_LABELS

AGE_CLASS = [0, 10, 14, 17, 25, 50, 65, np.inf]
NUMBER_OF_VEHICLES= [0,1,2,3,np.inf]
def configure(context):

    context.config("output_path")
    context.config("output_prefix", "ile_de_france_")
    context.stage("synthesis.population.trips")
    context.stage("synthesis.population.enriched")

    context.stage("data.census.filtered", alias = "census")
    context.stage("data.hts.selected", alias = "hts")

def execute(context):
    path = context.config("output_path")
    prefix = context.config("output_prefix")

    df_person_eq = context.stage("synthesis.population.enriched")
    df_trip_eq = context.stage("synthesis.population.trips")

    df_census = context.stage("census")
    _, df_hts_person, df_hts_trip = context.stage("hts")
    # get age class
    df_person_eq["age_class"] = pd.cut(df_person_eq["age"],AGE_CLASS,include_lowest=True)
    df_census["age_class"] = pd.cut(df_census["age"],AGE_CLASS,include_lowest=True)
    df_hts_person["age_class"] = pd.cut(df_hts_person["age"],AGE_CLASS,include_lowest=True)

    # get vehicule class 
    df_person_eq["vehicles_class"] = pd.cut(df_person_eq["number_of_vehicles"],NUMBER_OF_VEHICLES,right=True,labels=NUMBER_OF_VEHICLES_LABELS)
    df_census["vehicles_class"] = pd.cut(df_census["number_of_vehicles"],NUMBER_OF_VEHICLES,right=True,labels=NUMBER_OF_VEHICLES_LABELS)


    df_eq_depl = pd.merge(df_trip_eq,df_person_eq[["person_id","age_class"]],on=["person_id"])
    df_hts_depl = pd.merge(df_hts_trip,df_hts_person[["person_id","age_class"]],on=["person_id"])
    # Age purpose analysis
    analysis_age_purpose = pd.pivot_table(df_eq_depl,"person_id",index="age_class",columns="following_purpose",aggfunc="count")
    analysis_age_purpose.to_csv(f"{path}/{prefix}age_purpose.csv")

    # Compare age volume
    analysis_age_class = pd.concat([df_census.groupby("age_class")["person_id"].count(),df_person_eq.groupby("age_class")["person_id"].count()],axis=1).reset_index()
    analysis_age_class.columns = ["Age class","INSEE","EQASIM"]
    analysis_age_class.to_csv(f"{path}/{prefix}age.csv")

    # Compare vehicule volume
    analysis_vehicles_class = pd.concat([df_census.groupby("vehicles_class")["household_id"].nunique(),df_person_eq.groupby("vehicles_class")["household_id"].nunique()],axis=1).reset_index()
    analysis_vehicles_class.columns = ["Number of vehicles class","INSEE","EQASIM"]
    analysis_vehicles_class.to_csv(f"{path}/{prefix}vehicle.csv")
    
    # Compare license volume 
    analysis_license_class = pd.concat([df_hts_person.groupby("has_license")["person_id"].count(),df_person_eq.groupby("has_license")["person_id"].count()],axis=1).reset_index()
    analysis_vehicles_class.columns = ["Possession of license","HTS","EQASIM"]
    analysis_vehicles_class["Possession of license"] = analysis_vehicles_class["Possession of license"] == 1
    analysis_license_class.to_csv(f"{path}/{prefix}license.csv")

    # Compare depl volume
    analysis_depl = pd.concat([df_hts_depl.groupby("age_class")["person_id"].count(),df_eq_depl.groupby("age_class")["person_id"].count()],axis=1).reset_index()
    analysis_depl.columns = ["Age class","HTS","EQASIM"]
    analysis_depl.to_csv(f"{path}/{prefix}deplacement.csv")

    # Compare dist
    df_hts_trip["routed_distance"] = df_hts_trip["routed_distance"]/1000
    df_hts_trip["distance_class"] = pd.cut(df_hts_trip["routed_distance"],list(np.arange(50))+[np.inf])
    analysis_dist = df_hts_trip.groupby("distance_class")["person_id"].count()
    return analysis_dist









