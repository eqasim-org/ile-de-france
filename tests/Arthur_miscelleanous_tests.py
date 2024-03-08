# -*- coding: utf-8 -*-
"""
Created on Mon Mar  4 13:33:57 2024

@author: arthur.burianne
"""
import pandas as pd
import numpy as np

tmp_path = ("C:/Users/arthur.burianne/Documents/dev_simulations/emc2_tmp/")
df_households, df_persons, df_trips = pd.read_pickle(tmp_path + "data.hts.emc2.filtered__a9bda47117f0467dc52ff42b6e3d4daf.p")


print("Validating trip times...")
any_errors = False
df_next = df_trips.shift(-1)

f = df_trips["departure_time"] < 0.0
print("  Trips with negative departure time:", np.count_nonzero(f))
any_errors |= np.count_nonzero(f) > 0

f = df_trips["arrival_time"] < 0.0
print("  Trips with negative arrival time:", np.count_nonzero(f))
any_errors |= np.count_nonzero(f) > 0

f = df_trips["departure_time"] > df_trips["arrival_time"]
print("  Trips with negative duration:", np.count_nonzero(f))
any_errors |= np.count_nonzero(f) > 0

f = ~df_trips["is_last_trip"]
f &= df_trips["arrival_time"] > df_next["departure_time"]

x = df_trips.loc[f]

print("  Trips that arrive after next departure:", np.count_nonzero(f))
any_errors |= np.count_nonzero(f) > 0

f = ~df_trips["is_last_trip"]
f &= df_trips["departure_time"] < df_next["departure_time"]
f &= df_trips["arrival_time"] > df_next["departure_time"]
f &= df_trips["arrival_time"] < df_next["arrival_time"]
print("  Trips that 'enter' following trip:", np.count_nonzero(f))
any_errors |= np.count_nonzero(f) > 0

f = ~df_trips["is_last_trip"]
f &= df_trips["departure_time"] > df_next["departure_time"]
f &= df_trips["arrival_time"] > df_next["arrival_time"]
f &= df_trips["departure_time"] < df_next["arrival_time"]
print("  Trips that 'exits' following trip", np.count_nonzero(f))
any_errors |= np.count_nonzero(f) > 0

f = ~df_trips["is_last_trip"]
f &= df_trips["departure_time"] > df_next["departure_time"]
f &= df_trips["arrival_time"] > df_next["departure_time"]
f &= df_trips["departure_time"] < df_next["arrival_time"]
f &= df_trips["arrival_time"] < df_next["arrival_time"]
print("  Trips that 'are included in' following trip:", np.count_nonzero(f))
any_errors |= np.count_nonzero(f) > 0

f = ~df_trips["is_last_trip"]
f &= df_trips["departure_time"] < df_next["departure_time"]
f &= df_trips["arrival_time"] > df_next["arrival_time"]
print("  Trips that 'cover' following trip:", np.count_nonzero(f))
any_errors |= np.count_nonzero(f) > 0

f = ~df_trips["is_last_trip"]
f &= df_trips["departure_time"] > df_next["arrival_time"]
f &= df_trips["arrival_time"] > df_next["arrival_time"]
print("  Trips that 'are after' following trip:", np.count_nonzero(f))
any_errors |= np.count_nonzero(f) > 0

f = df_trips["departure_time"].isna()
f |= df_trips["arrival_time"].isna()
f |= df_trips["trip_duration"].isna()
print("  Trips that have NaN times:", np.count_nonzero(f))
any_errors |= np.count_nonzero(f) > 0

if any_errors:
    print("  !!! Errors while validating trip times")
else:
    print("  => All trip times are consistent!")
