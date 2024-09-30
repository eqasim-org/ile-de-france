import itertools
import numba

import numpy as np
import pandas as pd
from  analysis.marginals import NUMBER_OF_VEHICLES_LABELS

AGE_CLASS = [0, 10, 14, 17, 25, 50, 65, np.inf]
NUMBER_OF_VEHICLES= [0,1,2,3,np.inf]
NAME_AGE_CLASS = ["0-10","11-14","15-17","18-25","26-50","51-65","65+"]
def configure(context):

    context.config("output_path")
    context.config("output_prefix", "ile_de_france_")
    context.config("sampling_rate")
    context.stage("synthesis.population.trips")
    context.stage("synthesis.population.enriched")

    context.stage("data.census.filtered", alias = "census")
    context.stage("data.hts.selected", alias = "hts")

def execute(context):
    path = context.config("output_path")
    prefix = context.config("output_prefix")
    sampling_rate = context.config("sampling_rate")
    df_person_eq = context.stage("synthesis.population.enriched")
    df_trip_eq = context.stage("synthesis.population.trips")

    df_census = context.stage("census")
    _, df_hts_person, df_hts_trip = context.stage("hts")
    df_hts_person["person_weight"] *=df_census["weight"].sum()/df_hts_person["person_weight"].sum()
    # get age class
    df_person_eq["age_class"] = pd.cut(df_person_eq["age"],AGE_CLASS,include_lowest=True,labels=NAME_AGE_CLASS)
    df_census["age_class"] = pd.cut(df_census["age"],AGE_CLASS,include_lowest=True,labels=NAME_AGE_CLASS)
    df_hts_person["age_class"] = pd.cut(df_hts_person["age"],AGE_CLASS,include_lowest=True,labels=NAME_AGE_CLASS)

    # get vehicule class 
    df_person_eq["vehicles_class"] = pd.cut(df_person_eq["number_of_vehicles"],NUMBER_OF_VEHICLES,right=True,labels=NUMBER_OF_VEHICLES_LABELS)
    df_census["vehicles_class"] = pd.cut(df_census["number_of_vehicles"],NUMBER_OF_VEHICLES,right=True,labels=NUMBER_OF_VEHICLES_LABELS)


    df_eq_depl = pd.merge(df_trip_eq,df_person_eq[["person_id","age_class"]],on=["person_id"])
    df_hts_depl = pd.merge(df_hts_trip,df_hts_person[["person_id","age_class","person_weight"]],on=["person_id"])
    # Age purpose analysis
    analysis_age_purpose = pd.pivot_table(df_eq_depl,"person_id",index="age_class",columns="following_purpose",aggfunc="count")
    analysis_age_purpose = analysis_age_purpose/sampling_rate
    analysis_age_purpose.to_csv(f"{path}/{prefix}age_purpose.csv")

    # Compare age volume
    analysis_age_class = pd.concat([df_census.groupby("age_class")["weight"].sum(),df_person_eq.groupby("age_class")["person_id"].count()],axis=1).reset_index()
    analysis_age_class.columns = ["Age class","INSEE","EQASIM"]
    analysis_age_class["Proportion_INSEE"] = analysis_age_class["INSEE"] /df_census["weight"].sum()
    analysis_age_class["Proportion_EQASIM"] = analysis_age_class["EQASIM"] /len(df_person_eq)
    analysis_age_class["EQASIM"] = analysis_age_class["EQASIM"]/sampling_rate
    analysis_age_class.to_csv(f"{path}/{prefix}age.csv")

    # Compare vehicule volume
    analysis_vehicles_class = pd.concat([df_census.groupby("vehicles_class")["household_id"].nunique(),df_person_eq.groupby("vehicles_class")["household_id"].nunique()],axis=1).reset_index()
    analysis_vehicles_class.columns = ["Number of vehicles class","INSEE","EQASIM"]
    analysis_vehicles_class["INSEE"] = analysis_vehicles_class["INSEE"] / df_census["household_id"].nunique() 
    analysis_vehicles_class["EQASIM"] = analysis_vehicles_class["EQASIM"] / df_person_eq["household_id"].nunique() 
    analysis_vehicles_class.to_csv(f"{path}/{prefix}nbr_vehicle.csv")
    
    # Compare license volume 
    analysis_license_class = pd.concat([df_hts_person.groupby("has_license")["person_weight"].sum(),df_person_eq.groupby("has_license")["person_id"].count()],axis=1).reset_index()
    analysis_license_class.columns = ["Possession of license","HTS","EQASIM"]
    analysis_license_class["Proportion_HTS"] = analysis_license_class["HTS"] /df_hts_person["person_weight"].sum()
    analysis_license_class["Proportion_EQASIM"] = analysis_license_class["EQASIM"] /len(df_person_eq)
    analysis_license_class["EQASIM"] = analysis_license_class["EQASIM"]/sampling_rate
    analysis_license_class.to_csv(f"{path}/{prefix}license.csv")

    # Compare depl volume
    analysis_depl = pd.concat([df_hts_depl.groupby("age_class")["person_weight"].sum(),df_eq_depl.groupby("age_class")["person_id"].count()],axis=1).reset_index()
    analysis_depl.columns = ["Age class","HTS","EQASIM"]
    analysis_depl["Proportion_HTS"] = analysis_depl["HTS"] /df_hts_depl["person_weight"].sum()
    analysis_depl["Proportion_EQASIM"] = analysis_depl["EQASIM"] /len(df_eq_depl)
    analysis_depl["EQASIM"] = analysis_depl["EQASIM"]/sampling_rate
    analysis_depl.to_csv(f"{path}/{prefix}deplacement.csv")

    # Compare dist
    df_hts_depl["routed_distance"] = df_hts_depl["routed_distance"]/1000
    df_hts_depl["distance_class"] = pd.cut(df_hts_depl["routed_distance"],list(np.arange(100))+[np.inf])
    analysis_dist = df_hts_depl.groupby("distance_class")["person_weight"].sum()

    return analysis_dist









