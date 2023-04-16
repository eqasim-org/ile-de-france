import pandas as pd
import os

"""
This stage loads the raw data from the French population census.
"""

def configure(context):
    context.stage("data.spatial.codes")

    context.config("data_path")
    context.config("census_path", "rp_2019/FD_INDCVIZA_2019.csv")


COLUMNS_DTYPES = {
    "CANTVILLE":"str", 
    "NUMMI":"str", 
    "AGED":"str",
    "COUPLE":"str", 
    "CS1":"str",
    "DEPT":"str", 
    "ETUD":"str", 
    "ILETUD":"str",
    "ILT":"str", 
    "IPONDI":"str", 
    "IRIS":"str",
    "REGION":"str", 
    "SEXE":"str",
    "TACT":"str", 
    "TRANS":"str",
    "VOIT":"str", 
    "DEROU":"str"
}


def execute(context):
    
    df_records = []
    df_codes = context.stage("data.spatial.codes")
    requested_departements = df_codes["departement_id"].unique()


    with context.progress(label = "Reading census ...") as progress:
        
        csv = pd.read_csv("%s/%s" % (context.config("data_path"),
                context.config("census_path")), usecols = COLUMNS_DTYPES.keys(), sep = ";",
                dtype = COLUMNS_DTYPES,
                chunksize = 10240)
    
    for df_chunk in csv:
        progress.update(len(df_chunk))

        df_chunk = df_chunk[df_chunk["DEPT"].isin(requested_departements)]

        if len(df_chunk) > 0:
            df_records.append(df_chunk)

    return pd.concat(df_records)


def validate(context):
    if not os.path.exists("%s/%s" % (context.config("data_path"), context.config("census_path"))):
        raise RuntimeError("RP 2019 data is not available")

    return os.path.getsize("%s/%s" % (context.config("data_path"), context.config("census_path")))
