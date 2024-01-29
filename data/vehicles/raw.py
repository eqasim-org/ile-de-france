import numpy as np
import pandas as pd
import mock
from openpyxl.reader import excel

"""
This stage loads the raw data of the specified vehicle fleet data
https://www.statistiques.developpement-durable.gouv.fr/donnees-sur-le-parc-automobile-francais-au-1er-janvier-2021
"""

def configure(context):
    context.config("data_path")
    context.config("vehicles_data_year", 2015)
    context.stage("data.spatial.codes")

def execute(context):

    year = context.config("vehicles_data_year")

    df_codes = context.stage("data.spatial.codes")

    # the downloaded excel files meta-data are actually have a badly formatted ISO datetime
    # https://foss.heptapod.net/openpyxl/openpyxl/-/issues/1659 
    with mock.patch.object(excel.ExcelReader, 'read_properties', lambda self: None):
        df_vehicle_com_counts = pd.read_excel(
            "%s/vehicles_%s/Parc_VP_Communes_%s.xlsx" % (context.config("data_path"), year, year)
        )
        df_vehicle_reg_counts = pd.read_excel(
            "%s/vehicles_%s/Parc_VP_Regions_%s.xlsx" % (context.config("data_path"), year, year)
        )
    
    df_vehicle_com_counts["region_id"] = df_vehicle_com_counts["Code région"].astype("category")
    df_vehicle_com_counts["departement_id"] = df_vehicle_com_counts["Code départment"].astype("category")
    df_vehicle_com_counts["commune_id"] = df_vehicle_com_counts["Code commune"].astype("category")

    df_vehicle_reg_counts["region_id"] = df_vehicle_reg_counts["Code région"].astype("category")

    requested_departements = set(df_codes["departement_id"].unique())
    requested_regions = set(df_codes["region_id"].astype(str).unique())

    if len(requested_departements) > 0:
        df_vehicle_com_counts = df_vehicle_com_counts[df_vehicle_com_counts["departement_id"].isin(requested_departements)]

    if len(requested_regions) > 0:
        df_vehicle_reg_counts = df_vehicle_reg_counts[df_vehicle_reg_counts["region_id"].isin(requested_regions)]

    df_vehicle_com_counts["region_id"] = df_vehicle_com_counts["region_id"].cat.remove_unused_categories()
    df_vehicle_com_counts["departement_id"] = df_vehicle_com_counts["departement_id"].cat.remove_unused_categories()
    df_vehicle_com_counts["commune_id"] = df_vehicle_com_counts["commune_id"].cat.remove_unused_categories()

    df_vehicle_reg_counts["region_id"] = df_vehicle_reg_counts["region_id"].cat.remove_unused_categories()

    df_vehicle_com_counts["critair"] = df_vehicle_com_counts["Vignette Crit'air"]
    df_vehicle_com_counts["technology"] = df_vehicle_com_counts["Energie"]

    df_vehicle_reg_counts["critair"] = df_vehicle_reg_counts["Vignette crit'air"]
    df_vehicle_reg_counts["technology"] = df_vehicle_reg_counts["Energie"]

    count_column_name = "Parc au 01/01/%s" % context.config("vehicles_data_year")
    age_column_name = "Age au 01/01/%s" % context.config("vehicles_data_year")

    df_vehicle_com_counts["fleet"] = df_vehicle_com_counts[count_column_name]
    df_vehicle_reg_counts["fleet"] = df_vehicle_reg_counts[count_column_name]
    df_vehicle_reg_counts["age"] = df_vehicle_reg_counts[age_column_name]

    df_vehicle_fleet_counts = df_vehicle_com_counts.groupby(["region_id", "commune_id", "critair","technology"])["fleet"].sum().reset_index().dropna()
    df_vehicle_age_counts = df_vehicle_reg_counts.groupby(["region_id", "critair", "technology", "age"])["fleet"].sum().reset_index().dropna()

    return df_vehicle_fleet_counts, df_vehicle_age_counts