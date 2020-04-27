import shapely.geometry as geo
import numpy as np
import geopandas as gpd
import pandas as pd
from sklearn.neighbors import KDTree
import multiprocessing as mp

def to_gpd(context, df, x = "x", y = "y", crs = dict(init = "epsg:2154")):
    df["geometry"] = [
        geo.Point(*coord) for coord in context.progress(
            zip(df[x], df[y]), total = len(df),
            label = "Converting coordinates"
        )]
    df = gpd.GeoDataFrame(df, crs = dict(init = "epsg:2154"))

    if not crs == dict(init = "epsg:2154"):
        df = df.to_crs(dict(init = "epsg:2154"))

    return df
