from pandas.core.frame import DataFrame
import numpy as np
import pandas as pd
import geopandas as gpd
import os

"""
This stage loads the raw data of the specified HTS (EMC2 Gironde).

Adapted from the first implementation by Valentin Le Besond (IFSTTAR Nantes)
and second implementation by Sebastian Hoërl
"""

def configure(context):
    context.config("data_path")

from .format import HOUSEHOLD_FORMAT, PERSON_FORMAT, TRIP_FORMAT

HOUSEHOLD_COLUMNS = {
    "MP2": str, "ECH": str, "COEM": float,
    "M14": int, "M20": int, "M5": int
}
# Loire Atlantique EDGT => EMC2 Gironde
# MTIR+MP2  =>   MP2 (MP2 +  MTIR + 000)  # zone de tirage et zone de résidence
# M7    =>   M20 # nombre de vélos à disposition du ménage
# M6    =>   M14 # nombre de 2RM (+3RM) à disposition du ménage


PERSON_COLUMNS = {
    "ECH": str, "PER": int, "PP2": str, "PENQ": int,
    "P3": int, "P2": int, "P4": int,
    "P7": str, "P10": str, "P12": str,
    "P9": str, "P5": str,
    "COEP": float, "COEQ": float
}
# Loire Atlantique EDGT => EMC2 Gironde
# PTIR+PP2  =>   PP2 (PTIR +  PP2 + 000)  # zone de tirage et zone de résidence
# P1 => ?
# P12 formatté étrangemen( oui, non, nan?)
# P10 abo TC

TRIP_COLUMNS = {
    "ECH": str, "PER": int, "NDEP": int, "DP2": str,
    "D2A": int, "D5A": int, "D3": str, "D4": str,
    "D7": str, "D8": str,
    "D8C": int, "MODP": int, "DOIB": int, "DIST": int
}
# Loire Atlantique EDGT => EMC2 Gironde
# DTIR+DP2  =>  DP2 (DTIR +  DP2 + 000)  # zone de tirage et zone de résidence
# D4A+D4B   =>  D4 (1630 = 16h30) heure de départ
# D8A+D8B   =>  D8 (1630 = 16h30) heure d'arrivée



def execute(context):
    # Load households
    df_households = pd.read_csv(
        "%s/emc2/08a_EMC2_Gironde_2022_Men_Fusion_men2021_MQPV_23052023.csv"
        % context.config("data_path"),
        usecols = list(HOUSEHOLD_COLUMNS.keys()), dtype = HOUSEHOLD_COLUMNS,sep=";"
    )

    # Load persons
    df_persons = pd.read_csv(
        "%s/emc2/07b_EMC2_Gironde_2022_Pers_Fusion_men2021_P19A_13022023.csv"
     % context.config("data_path"),
     usecols = list(PERSON_COLUMNS.keys()), dtype = PERSON_COLUMNS,sep=";"
 )

    # Load trips
    df_trips = pd.read_csv(
        "%s/emc2/07c_EMC2_Gironde_2022_Depl_Fusion_men2021_D11_03022023.csv"
        % context.config("data_path"),
        usecols = list(TRIP_COLUMNS.keys()), dtype = TRIP_COLUMNS,sep=";"
    )


    return df_households, df_persons, df_trips

FILES = [
    "08a_EMC2_Gironde_2022_Men_Fusion_men2021_MQPV_23052023.csv",
    "07b_EMC2_Gironde_2022_Pers_Fusion_men2021_P19A_13022023.csv",
    "07c_EMC2_Gironde_2022_Depl_Fusion_men2021_D11_03022023.csv",
]

def validate(context):
    for name in FILES:
        if not os.path.exists("%s/emc2/%s" % (context.config("data_path"), name)):
            raise RuntimeError("File missing from EDGT: %s" % name)

    return [
        os.path.getsize("%s/emc2/%s" % (context.config("data_path"), name))
        for name in FILES
    ]
