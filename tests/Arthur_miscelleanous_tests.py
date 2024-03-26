# -*- coding: utf-8 -*-
"""
Created on Mon Mar  4 13:33:57 2024

@author: arthur.burianne
"""
# %%
import pandas as pd
import numpy as np

tmp_path = ("C:/Users/arthur.burianne/Documents/dev_simulations/emc2_tmp/")
# df_households, df_persons, df_trips = pd.read_pickle(tmp_path + "data.hts.emc2.raw__e8bdbdd69c761097faafa823c639aced.p")
# df_households, df_persons, df_trips = pd.read_pickle(tmp_path + "data.hts.emc2.filtered__a9bda47117f0467dc52ff42b6e3d4daf.p")
df_households, df_persons, df_trips = pd.read_pickle(tmp_path + "data.hts.emc2.reweighted__a9bda47117f0467dc52ff42b6e3d4daf.p")

df_trips["trip_weight"].sum()


# %%

# unique constant length ID = PP2*100000000+ECH*1000+PER*100+NDEP

# Merge departement into households
df_households["departement_id"] = "33"
# Transform original IDs to integer (they are hierarchichal)

df_households["edgt_household_id"] = df_households["MP2"].astype("int64")*100000000 + df_households["ECH"].astype(int)*1000


df_persons["edgt_household_id"] =  df_persons["PP2"].astype("int64")*100000000 + df_persons["ECH"].astype(int)*1000
df_persons["edgt_person_id"] = df_persons["PP2"].astype("int64")*100000000 + df_persons["ECH"].astype(int)*1000 + df_persons["PER"].astype(int)*100


df_trips["edgt_household_id"] = df_trips["DP2"].astype("int64")*100000000 + df_trips["ECH"].astype(int)*1000
df_trips["edgt_person_id"] =  df_trips["DP2"].astype("int64")*100000000 + df_trips["ECH"].astype(int)*1000 + df_trips["PER"].astype(int)*100
df_trips["edgt_trip_id"] = df_trips["DP2"].astype("int64")*100000000 + df_trips["ECH"].astype(int)*1000 + df_trips["PER"].astype(int)*100 + df_trips["NDEP"].astype(int)


# Construct new IDs for households, persons and trips (which are unique globally)
df_households["household_id"] = np.arange(len(df_households))

df_persons = pd.merge(
    df_persons, df_households[["edgt_household_id", "household_id", "departement_id"]],
    on = ["edgt_household_id"]
).sort_values(by = ["household_id", "edgt_person_id"])
df_persons["person_id"] = np.arange(len(df_persons))

df_trips = pd.merge(
    df_trips, df_persons[["edgt_person_id", "edgt_household_id", "person_id", "household_id"]],
    on = ["edgt_person_id", "edgt_household_id"]
).sort_values(by = ["household_id", "person_id", "edgt_trip_id"])
df_trips["trip_id"] = np.arange(len(df_trips))


# Weight
df_persons["person_weight"] = df_persons["COEP"].astype(float)
df_households["household_weight"] = df_households["COEM"].astype(float)


# Add weight to trips
df_trips = pd.merge(
    df_trips, df_persons[["person_id", "COEQ"]], on = "person_id", how = "left"
).rename(columns = { "COEQ": "trip_weight" })
df_persons["trip_weight"] = df_persons["COEQ"]

df_trips["trip_weight"].sum()

# %%
