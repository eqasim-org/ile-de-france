import pandas as pd
import geopandas as gpd
import shapely

def configure(context):
    context.config("data_path")
    context.config("cairo.population_path")
    context.config("crs")
    
COLUMNS = {
    "person_id": "person_id",
    "home_loc": "home_location",
    "activities": "number_of_activities",
    "act_no": "activity_index",
    "activity": "purpose",
    "distance": "preceding_distance",
    "start": "activity_start_time",
    "end": "activity_end_time",
    "car": "car_availability"
}

def execute(context):
    df = []
    
    with context.progress(label = "Loading population ...", total = 52961280) as progress:
        for df_partial in pd.read_csv("{}/{}".format(
            context.config("data_path"), context.config("cairo.population_path")), usecols = list(COLUMNS.keys()), chunksize = 10240):
            df_partial = df_partial.rename(columns = COLUMNS)
            df.append(df_partial)
            progress.update(len(df_partial))
    
    # Merge together
    df = pd.concat(df)
    
    # Convert geographic data
    df["home_location"] = df["home_location"].apply(shapely.from_wkt)
    df = gpd.GeoDataFrame(df, crs = "EPSG:4326", geometry = "home_location").to_crs(context.config("crs"))
    
    return df[[
        "person_id", "home_location", 
        "number_of_activities", "activity_index",
        "purpose", "activity_start_time", "activity_end_time",
        "preceding_distance", "car_availability"
    ]]
