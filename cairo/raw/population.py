import pandas as pd

def configure(context):
    context.config("cairo.population_path")
    context.config("sampling_rate")

def execute(context):
    df = pd.read_csv("{}/{}".format(
        context.config("data_path"), context.config("cairo.population_path")))
    
    sampling_rate = context.config("sampling_rate")
    df = df.sample(sampling_rate)

    # Cleaning columns
    df = df.rename(columns = {
        "home_loc": "home_location",
        "activities": "number_of_activities",
        "act_no": "activity_index",
        "activity_type": "purpose",
        "distance": "preceding_distance",
        "start": "activity_start_time",
        "end": "activity_end_time",
        "car": "car_availability"
    })
    
    return df[[
        "person_id", "home_location", 
        "number_of_activities", "activity_index",
        "purpose", "activity_start_time", "activity_end_time",
        "preceding_distance", "car_availability"
    ]]
