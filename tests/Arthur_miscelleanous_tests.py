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

# %%
z = df_trips.groupby("mode")["trip_weight"].sum()/df_trips["trip_weight"].sum()*100
