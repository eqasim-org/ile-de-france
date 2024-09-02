import numpy as np
import pandas as pd
import mock, os, glob
from openpyxl.reader import excel
import zipfile

"""
This stage loads the raw data of the specified vehicle fleet data
https://www.statistiques.developpement-durable.gouv.fr/donnees-sur-le-parc-automobile-francais-au-1er-janvier-2021
"""

def configure(context):
    context.config("data_path")
    context.config("vehicles_path")
    context.config("vehicles_year", 2021)
    context.stage("data.spatial.codes")

def find_municipalities(path):
    candidates = sorted(list(glob.glob("{}/*.xlsx".format(path))))
    candidates = [c for c in candidates if "communes" in c]

    if len(candidates) == 0:
        raise RuntimeError("Municipalities vehicle data is not available in {}".format(path))
    
    if len(candidates) > 1:
        raise RuntimeError("Found multiple municipalities vehicle data sets in {}".format(path))

    return candidates

def find_regions(path):
    candidates = sorted(list(glob.glob("{}/*.zip".format(path))))
    candidates = [c for c in candidates if "regions" in c]

    if len(candidates) == 0:
        raise RuntimeError("Regions vehicle data is not available in {}".format(path))
    
    if len(candidates) > 1:
        raise RuntimeError("Found multiple regions vehicle data sets in {}".format(path))

    return candidates


def execute(context):
    df_codes = context.stage("data.spatial.codes")

    # the downloaded excel files meta-data are actually have a badly formatted ISO datetime
    # https://foss.heptapod.net/openpyxl/openpyxl/-/issues/1659 
    with mock.patch.object(excel.ExcelReader, 'read_properties', lambda self: None):
        with zipfile.ZipFile(find_municipalities("{}/{}".format(context.config("data_path"), context.config("vehicles_path")))) as archive:
            archive.extractall(context.path())

        with zipfile.ZipFile(find_municipalities("{}/{}".format(context.config("data_path"), context.config("vehicles_path")))) as archive:
            archive.extractall(context.path())

        year = str(context.config("vehicles_year"))

        municipalities_path = [path for path in glob.glob("{}/*.xlsx") if "Communes" in path and year in path]
        assert len(municipalities_path) == 1
        municipalities_path = municipalities_path[0]

        regions_path = [path for path in glob.glob("{}/*.xlsx") if "Regions" in path and year in path]
        assert len(regions_path) == 1
        regions_path = regions_path[0]
        
        df_municipalities = pd.read_excel(municipalities_path)
        df_regions = pd.read_excel(regions_path)
    
    df_municipalities["region_id"] = df_municipalities["Code région"].astype("category")
    df_municipalities["departement_id"] = df_municipalities["Code départment"].astype("category")
    df_municipalities["commune_id"] = df_municipalities["Code commune"].astype("category")

    df_regions["region_id"] = df_regions["Code région"].astype("category")

    requested_departements = set(df_codes["departement_id"].unique())
    requested_regions = set(df_codes["region_id"].astype(str).unique())

    if len(requested_departements) > 0:
        df_municipalities = df_municipalities[df_municipalities["departement_id"].isin(requested_departements)]

    if len(requested_regions) > 0:
        df_regions = df_regions[df_regions["region_id"].isin(requested_regions)]

    df_municipalities["region_id"] = df_municipalities["region_id"].cat.remove_unused_categories()
    df_municipalities["departement_id"] = df_municipalities["departement_id"].cat.remove_unused_categories()
    df_municipalities["commune_id"] = df_municipalities["commune_id"].cat.remove_unused_categories()

    df_regions["region_id"] = df_regions["region_id"].cat.remove_unused_categories()

    df_municipalities["critair"] = df_municipalities["Vignette Crit'air"]
    df_municipalities["technology"] = df_municipalities["Energie"]

    df_regions["critair"] = df_regions["Vignette crit'air"]
    df_regions["technology"] = df_regions["Energie"]

    count_column_name = "Parc au 01/01/%s" % context.config("vehicles_data_year")
    age_column_name = "Age au 01/01/%s" % context.config("vehicles_data_year")

    df_municipalities["fleet"] = df_municipalities[count_column_name]
    df_regions["fleet"] = df_regions[count_column_name]
    df_regions["age"] = df_regions[age_column_name]

    df_vehicle_fleet_counts = df_municipalities.groupby(["region_id", "commune_id", "critair","technology"])["fleet"].sum().reset_index().dropna()
    df_vehicle_age_counts = df_regions.groupby(["region_id", "critair", "technology", "age"])["fleet"].sum().reset_index().dropna()

    return df_vehicle_fleet_counts, df_vehicle_age_counts

def validate(context):
    municipalities_path = find_municipalities("{}/{}".format(context.config("data_path"), context.config("vehicles_path")))
    regions_path = find_regions("{}/{}".format(context.config("data_path"), context.config("vehicles_path")))
    
    return os.path.getsize(municipalities_path) + os.path.getsize(regions_path)
