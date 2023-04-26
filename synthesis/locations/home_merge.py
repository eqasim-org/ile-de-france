import pandas as pd
import numpy as np
import geopandas as gpd
import numpy as np

"""
This stage matches adresses from BAN with residential buildings from BD TOPO.
The match is based on distance from building shape perimeter in every direction 
(buffer expressed as meters in french EPSG:2154 projection). Distance value is 
default set to 5 meters and in most case is measured from 1 to 20 meters).
The output is one or several row(s) per buildings depending on match (one or 
many adresses). For every row of one buiilding the residences count is distributed
to matching adresses (i.e : Building A with 10 residences comes with 2 matching
adresses (A1 and A2), each of these two adresses are separeted rows in the output 
with 5 residences declared for draw).If no adresses matches a buidling it centroid
is taken as unique adress.

"""

def configure(context):
    context.stage("data.bdtopo.raw")
    context.stage("data.ban.raw")
    context.stage("data.spatial.iris")

def execute(context):
    # Find required IRIS
    df_iris = context.stage("data.spatial.iris")
    required_iris = set(df_iris["iris_id"].unique())

    # Load all addresses and residential buildings information
    df_buildings = context.stage("data.bdtopo.raw")
    df_buildings["geometry"] = df_buildings["geometry"].centroid
    df_buildings["centroid"] = df_buildings["geometry"].centroid

    df_addresses = context.stage("data.ban.raw")
    
    print("nb bâtiments :" + str(len(df_buildings)))
    print("nb adresses :" + str(len(df_addresses)))

    # buildings buffer to captur adresses in extended perimeter
    df_buildings_buffer = df_buildings.copy()
    df_buildings_buffer["geometry"] = df_buildings_buffer.buffer(5)    

    # matches residential buildings with BAN adresses (1 or more)  
    # within buffer (expressed as meters in french coordinate system Lambert 93 EPSG:2154)
    df_buildings_adresses = df_buildings_buffer.sjoin(df_addresses, how="left",predicate="contains")
    
    # set adresses points as geometry
    df_buildings_adresses["geometry"] =  gpd.points_from_xy(df_buildings_adresses.x, df_buildings_adresses.y, crs="EPSG:2154")    

    # for non matched buldings, uses centroid as point coordinates
    df_buildings_adresses.loc[df_buildings_adresses["x"].isna(),"geometry"] = df_buildings_adresses[df_buildings_adresses["x"].isna()]["centroid"]   
    
    # residence count per buildings distribution on adresses matches (1 or many)
    # as numpy array to fasten process
    adresses_count = df_buildings_adresses["building_id"].to_numpy()

    # get buildings ids, count, and map to rebuild
    adresses_group_id,indices,adresses_group_count = np.unique(adresses_count,return_inverse=True,return_counts=True)

    # rebuild and replace buildings ids with residences count
    adresses_count = adresses_group_count[indices]
    df_buildings_adresses["adresses_count"] = adresses_count
    
    # residences distribution per buildings
    df_buildings_adresses["weight"] = df_buildings_adresses["housing"] /df_buildings_adresses["adresses_count"]
  
    return df_buildings_adresses[["geometry", "building_id", "weight"]]
