import pandas as pd
import os

"""
Loads raw OD data from French census data.
"""

def configure(context):
    context.stage("data.spatial.codes")
    context.config("data_path")
    context.config("od_pro_path", "rp_2019/FD_MOBPRO_2019.csv")
    context.config("od_sco_path", "rp_2019/FD_MOBSCO_2019.csv")

def execute(context):
    df_codes = context.stage("data.spatial.codes")
    requested_communes = df_codes["commune_id"].unique()

    # First, load work
    with context.progress(label = "Reading work flows ...") as progress:
        
        df_records = []

        COLUMNS_DTYPES = {
            "COMMUNE":"str", 
            "ARM":"str", 
            "TRANS":"int",
            "IPONDI":"float", 
            "DCLT":"str"
        }


        csv = pd.read_csv("%s/%s" % (context.config("data_path"), context.config("od_pro_path")), 
                          usecols = COLUMNS_DTYPES.keys(), dtype = COLUMNS_DTYPES, sep = ";",chunksize = 10240)
        
        for df_chunk in csv:
            progress.update(len(df_chunk))
        
            f = df_chunk["COMMUNE"].isin(requested_communes)
            f |= df_chunk["ARM"].isin(requested_communes)
            f &= df_chunk["DCLT"].isin(requested_communes)
    
            df_chunk = df_chunk[f]
            
            if len(df_chunk) > 0:
                df_records.append(df_chunk)
        
        work = pd.concat(df_records)


    # Second, load education
    with context.progress(label = "Reading education flows ...") as progress:
        
        df_records = []

        COLUMNS_DTYPES = {
            "COMMUNE":"str", 
            "ARM":"str", 
            "IPONDI":"float",
            "DCETUF":"str"
        }
        
        csv = pd.read_csv("%s/%s" % (context.config("data_path"), context.config("od_sco_path")), 
                          usecols = COLUMNS_DTYPES.keys(), dtype = COLUMNS_DTYPES, sep = ";",chunksize = 10240)
        
        for df_chunk in csv:
            progress.update(len(df_chunk))
        
            f = df_chunk["COMMUNE"].isin(requested_communes)
            f |= df_chunk["ARM"].isin(requested_communes)
            f &= df_chunk["DCETUF"].isin(requested_communes)
    
            df_chunk = df_chunk[f]
            
            if len(df_chunk) > 0:
                df_records.append(df_chunk)
        
        education = pd.concat(df_records)

    return work, education


def validate(context):
    if not os.path.exists("%s/%s" % (context.config("data_path"), context.config("od_pro_path"))):
        raise RuntimeError("RP MOBPRO data is not available")

    if not os.path.exists("%s/%s" % (context.config("data_path"), context.config("od_sco_path"))):
        raise RuntimeError("RP MOBSCO data is not available")

    return [
        os.path.getsize("%s/%s" % (context.config("data_path"), context.config("od_pro_path"))),
        os.path.getsize("%s/%s" % (context.config("data_path"), context.config("od_sco_path")))
    ]
