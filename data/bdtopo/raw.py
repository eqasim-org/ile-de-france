import fiona
import pandas as pd
import os
import shapely.geometry as geo
import geopandas as gpd
import py7zr
import re
import glob
import numpy as np

"""
This stage loads the raw data from the French building registry (BD-TOPO).
"""
 
def configure(context):
    context.config("data_path")
    context.config("bdtopo_path", "bdtopo22")
    context.config("bdtopo_date", "2022-03-15")

    context.stage("data.spatial.departments")

def get_department_string(department_id):
    department_id = str(department_id)

    if len(department_id) == 2:
        return "0{}".format(department_id)
    elif len(department_id) == 3:
        return department_id
    else:
        raise RuntimeError("Department identifier should have at least two characters")

def execute(context):
    df_departments = context.stage("data.spatial.departments")
    print("Expecting data for {} departments".format(len(df_departments)))
    
    candidate_paths = find_bdtopo("{}/{}".format(context.config("data_path"), context.config("bdtopo_path")))
    department_paths = {}

    date = context.config("bdtopo_date")

    for department_id in df_departments["departement_id"].values:
        for path in candidate_paths:
            if path.endswith("BDTOPO_3-0_TOUSTHEMES_GPKG_LAMB93_D{}_{}.7z".format(
                get_department_string(department_id), date)):
                department_paths[department_id] = path
                break
    
    for department_id in df_departments["departement_id"].values:
        if department_id not in department_paths:        
            raise RuntimeError("No BDTOPO data found for department {}".format(department_id))

    df_bdtopo = []
    known_ids = set()

    for department_id, department_path in department_paths.items():
        print("Loading department {}".format(department_id))

        with py7zr.SevenZipFile(department_path) as archive:
            # Find the path inside the archive
            geometry_path = [path for path in archive.getnames() if path.endswith(".gpkg")]
            
            if len(geometry_path) != 1:
                raise RuntimeError("Cannot find unambiguous geometry source in: {}".format(department_path))

            print("  Extracting ...")
            archive.extract(context.path(), geometry_path[0])

            geometry_path = "{}/{}".format(context.path(), geometry_path[0])

        with context.progress(label = "Reading ...") as progress:
            data = { "cleabs": [], "nombre_de_logements": [], "geometry": [] }
            with fiona.open(geometry_path, layer = "batiment") as package:
                for item in package:
                    data["cleabs"].append(item["properties"]["cleabs"])
                    data["nombre_de_logements"].append(item["properties"]["nombre_de_logements"])
                    data["geometry"].append(geo.shape(item["geometry"]))
                    progress.update()

            df_buildings = pd.DataFrame(data)
            df_buildings = gpd.GeoDataFrame(df_buildings, crs = "EPSG:2154")
        
        df_buildings["building_id"] = df_buildings["cleabs"].apply(lambda x: int(x[8:]))
        df_buildings["housing"] = df_buildings["nombre_de_logements"].fillna(0).astype(int)

        df_buildings["centroid"] = df_buildings["geometry"].centroid
        df_buildings = df_buildings.set_geometry("centroid")

        print("  Filtering ...")

        initial_count = len(df_buildings)
        df_buildings = df_buildings[df_buildings["housing"] > 0]
        final_count = len(df_buildings)
        print("    {}/{} filtered by dwellings".format(initial_count - final_count, initial_count))

        initial_count = len(df_buildings)
        df_buildings = df_buildings[~df_buildings["building_id"].isin(known_ids)]
        final_count = len(df_buildings)
        print("    {}/{} filtered duplicates".format(initial_count - final_count, initial_count))

        initial_count = len(df_buildings)
        df_buildings = gpd.sjoin(df_buildings, df_departments[
            df_departments["departement_id"] == department_id
        ], predicate = "within")
        final_count = len(df_buildings)
        print("    {}/{} filtered spatially".format(initial_count - final_count, initial_count))

        df_buildings["department_id"] = department_id
        df_buildings = df_buildings.set_geometry("geometry")

        df_bdtopo.append(df_buildings[["building_id", "housing", "department_id", "geometry"]])
        known_ids |= set(df_buildings["building_id"].unique())

        os.remove(geometry_path)

    df_bdtopo = pd.concat(df_bdtopo)

    for department_id in df_departments["departement_id"].values:
        assert np.count_nonzero(df_bdtopo["department_id"] == department_id) > 0

    return df_bdtopo[["building_id", "housing", "geometry"]]

def find_bdtopo(path):
    candidates = list(glob.glob("{}/*.7z".format(path)))

    if len(candidates) == 0:
        raise RuntimeError("BD TOPO data is not available in {}".format(path))
    
    return candidates

def validate(context):
    paths = find_bdtopo("{}/{}".format(context.config("data_path"), context.config("bdtopo_path")))
    return sum([os.path.getsize(path) for path in paths])
