import simpledbf
from tqdm import tqdm
import pandas as pd
import os

"""
This stage loads the raw data from the French population census.
"""

def configure(context):
    context.stage("data.spatial.codes")

    context.config("data_path")
    context.config("census_path", "rp_2015/FD_INDCVIZA_2015.dbf")

COLUMNS = [
    "CANTVILLE", "NUMMI", "AGED",
    "COUPLE", "CS1",
    "DEPT", "ETUD", "ILETUD",
    "ILT", "IPONDI", "IRIS",
    "REGION", "SEXE",
    "TACT", "TRANS",
    "VOIT", "DEROU"
]

def execute(context):
    df_codes = context.stage("data.spatial.codes")
    requested_departements = df_codes["departement_id"].unique()

    table = simpledbf.Dbf5("%s/%s" % (context.config("data_path"), context.config("census_path")))
    records = []

    with context.progress(total = 4320619, label = "Reading census ...") as progress:
        for df_chunk in table.to_dataframe(chunksize = 10240):
            progress.update(len(df_chunk))

            df_chunk = df_chunk[df_chunk["DEPT"].isin(requested_departements)]
            df_chunk = df_chunk[COLUMNS]

            if len(df_chunk) > 0:
                records.append(df_chunk)

    pd.concat(records).to_hdf("%s/census.hdf" % context.path(), "census")

def validate(context):
    if not os.path.exists("%s/%s" % (context.config("data_path"), context.config("census_path"))):
        raise RuntimeError("RP 2015 data is not available")

    return os.path.getsize("%s/%s" % (context.config("data_path"), context.config("census_path")))
