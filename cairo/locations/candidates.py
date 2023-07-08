import geopandas as gpd
import numpy as np

def configure(context):
    context.config("data_path")
    context.config("cairo.locations_path")
    context.config("crs")

def execute(context):
    df = gpd.read_file("{}/{}".format(
        context.config("data_path"), context.config("cairo.locations_path"))).to_crs(context.config("crs"))
        
    df = df.rename(columns = { "activity_t": "location_type" })
    df = df.dropna()
    
    df["location_id"] = np.arange(len(df))    
    df = df[["location_id", "location_type", "geometry"]]
    
    return df

