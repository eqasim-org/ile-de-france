import pandas as pd
import numpy as np
import geopandas as gpd
import numpy as np

"""
This stage assigns adresses from BAN to residential buildings from BD TOPO.

The match is based on distance from building shape perimeter in every direction 
(buffer expressed as meters). The distance value is set to 5 meters by default 
and in most case is between 1 to 20 meters in the data.

The output is one or several rows per building depending on the match (one or 
many adresses). For every building the housing count is distributed to the matching 
adresses. For instance, the assigned addresses of a building with 10 housing units
and two addresses will have a weight of 5.

If no adresses matches a buidling, its centroid is taken as the unique address.
"""

def configure(context):
    context.stage("data.bdtopo.raw")
    context.stage("data.ban.raw")
    
    context.config("home_address_buffer", 5.0)

def execute(context):
    # Load buildings
    df_buildings = context.stage("data.bdtopo.raw")

    # Load addresses
    df_addresses = context.stage("data.ban.raw")[["geometry"]].copy()
    
    print("Number of buildings:" + str(len(df_buildings)))
    print("Number of addresses:" + str(len(df_addresses)))

    # Buffer buildings to capture adresses in their vicinity
    df_buffer = df_buildings[["building_id", "housing", "geometry"]].copy()
    df_buffer["geometry"] = df_buffer.buffer(context.config("home_address_buffer"))

    # Find close-by addresses
    df_addresses = gpd.sjoin(df_addresses, df_buffer, predicate = "within")[[
        "building_id", "housing", "geometry"]]
    
    # Create missing addresses by using centroids
    df_missing = df_buildings[~df_buildings["building_id"].isin(df_addresses["building_id"])].copy()
    df_missing["geometry"] = df_missing["geometry"].centroid
    df_missing = df_missing[["building_id", "housing", "geometry"]]

    # Put together matched and missing addresses
    df_addresses = pd.concat([df_addresses, df_missing])

    # Obtain weights for all addresses
    df_total = df_addresses.groupby("building_id")["housing"].sum().reset_index(name = "total")
    df_addresses = pd.merge(df_addresses, df_total, on = "building_id")
    df_addresses["weight"] = df_addresses["housing"] / df_addresses["total"]
    
    return df_addresses[["building_id", "weight", "geometry"]]
