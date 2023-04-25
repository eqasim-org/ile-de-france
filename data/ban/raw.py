import os
import pandas as pd
import geopandas as gpd
import gzip


# """
# This stage loads the raw data from the new French address registry (BAN).
# """

def configure(context):
    context.config("data_path")
    context.config("ban_path", "/ban/")
    context.stage("data.spatial.codes")

def execute(context):
    df_codes = context.stage("data.spatial.codes")
    requested_departements = set(df_codes["departement_id"].unique())
    requested_communes = set(df_codes["commune_id"].unique())

    df_ban = pd.DataFrame()


    COLUMNS_DTYPES = {
        "code_insee":"str",
        "x":"float", 
        "y":"float"
    }
     
    for dep in requested_departements:
        
        with context.progress(label = "Loading BAN address registry for département : " + str(dep) + " ...") as progress:
            
            # gzip archive for department BAN name
            source_path = context.config("data_path") + context.config("ban_path") + "adresses-" + str(dep) + ".csv.gz"

            # # gzip open and csv to pandas DataFrame
            df_ban_tmp = pd.read_csv(source_path, compression='gzip', sep=";",usecols = COLUMNS_DTYPES.keys(), dtype = COLUMNS_DTYPES)

            # communes filter
            df_ban_tmp = df_ban_tmp[df_ban_tmp['code_insee'].isin(requested_communes)].copy()

            # concat   
            df_ban = pd.concat([df_ban,df_ban_tmp])

            progress.update()
            
                 
    #convert to geo dataframe
    df_ban = gpd.GeoDataFrame(df_ban, geometry=gpd.points_from_xy(df_ban.x, df_ban.y),crs="EPSG:2154")
    df_ban.rename(columns={"code_insee":"commune_id"},inplace=True)

    return df_ban
 

def validate(context):
    if not os.path.exists("%s/%s" % (context.config("data_path"), context.config("ban_path"))):
        raise RuntimeError("BAN data is not available")

    return os.path.getsize("%s/%s" % (context.config("data_path"), context.config("ban_path")))
