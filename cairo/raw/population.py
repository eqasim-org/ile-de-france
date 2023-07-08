import pandas as pd
import geopandas as gpd
import shapely
import numpy as np

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
    
    # Some filtering
    remove_na_time = set(df[
        ((df["activity_index"] > 0) & df["activity_start_time"].isna()) | 
        ((df["activity_index"] < df["number_of_activities"] - 1) & df["activity_end_time"].isna())
    ]["person_id"].unique())

    remove_negative_time = set(df[
        ((df["activity_start_time"] < 0) & np.isfinite(df["activity_start_time"])) | 
        ((df["activity_end_time"] < 0) & np.isfinite(df["activity_end_time"]))
    ]["person_id"].unique())

    print("Dropping {} persons with NaN start times".format(len(remove_na_time)))
    print("Dropping {} persons with negative times".format(len(remove_negative_time)))

    df = df[~df["person_id"].isin(remove_na_time | remove_negative_time)].copy()

    return df[[
        "person_id", "home_location", 
        "number_of_activities", "activity_index",
        "purpose", "activity_start_time", "activity_end_time",
        "preceding_distance", "car_availability"
    ]]
