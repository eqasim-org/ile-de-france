import shapely.geometry as geo
import numpy as np
import pandas as pd
import geopandas as gpd

def configure(context):
    context.stage("data.bpe.cleaned")
    context.stage("data.spatial.municipalities")

def execute(context):
    # Load destinations
    df_destinations = context.stage("data.bpe.cleaned")[[
        "enterprise_id", "activity_type", "commune_id", "geometry"
    ]].copy()
    df_destinations["destination_id"] = np.arange(len(df_destinations))

    # Attach attributes for activity types
    df_destinations["offers_work"] = True
    df_destinations["offers_other"] = True

    df_destinations["offers_leisure"] = df_destinations["activity_type"] == "leisure"
    df_destinations["offers_shop"] = df_destinations["activity_type"] == "shop"
    df_destinations["offers_education"] = df_destinations["activity_type"] == "education"

    df_destinations["imputed"] = False

    # Add work and education destinations to the centroid of zones that have no other destinations
    df_zones = context.stage("data.spatial.municipalities")

    all_communes = set(df_zones["commune_id"].unique())
    work_communes = set(df_destinations[df_destinations["offers_work"]]["commune_id"].unique())
    education_communes = set(df_destinations[df_destinations["offers_education"]]["commune_id"].unique())

    df_imputed = []

    for commune_id in all_communes - work_communes:
        centroid = df_zones[df_zones["commune_id"] == commune_id]["geometry"].centroid.iloc[0]

        df_imputed.append({
            "commune_id": commune_id, "geometry": centroid,
            "offers_work": True, "offers_education": False
        })

    for commune_id in all_communes - education_communes:
        centroid = df_zones[df_zones["commune_id"] == commune_id]["geometry"].centroid.iloc[0]

        df_imputed.append({
            "commune_id": commune_id, "geometry": centroid,
            "offers_work": False, "offers_education": True
        })

    df_imputed = pd.DataFrame.from_records(df_imputed)
    df_imputed["imputed"] = True
    df_imputed["offers_leisure"] = False
    df_imputed["offers_shop"] = False
    df_imputed["offers_other"] = True
    df_imputed["destination_id"] = df_destinations["destination_id"].max() + np.arange(len(df_imputed)) + 1
    df_imputed["enterprise_id"] = -1

    # Merge both frames togehter
    columns = [
        "destination_id", "enterprise_id", "commune_id", "geometry", "imputed",
        "offers_work", "offers_education", "offers_shop", "offers_leisure", "offers_other"
    ]

    df_destinations = df_destinations[columns]
    df_imputed = df_imputed[columns]

    return pd.concat([df_destinations, df_imputed])
