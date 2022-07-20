import simpledbf
from tqdm import tqdm
import pandas as pd
import os

"""
This stage loads the raw data from the French service registry.
"""

def configure(context):
    context.config("data_path")
    context.config("bpe_path", "bpe_2019/bpe19_ensemble_xy.csv")

    context.stage("data.spatial.codes")

COLUMNS = [
    "DCIRIS", "LAMBERT_X", "LAMBERT_Y",
    "TYPEQU", "DEPCOM"
]

def execute(context):
    df_codes = context.stage("data.spatial.codes")
    requested_departements = df_codes["departement_id"].unique()

    #table = simpledbf.Dbf5("%s/%s" % (context.config("data_path"), context.config("bpe_path")), codec = "latin1")
    csv_file = "%s/%s" % (context.config("data_path"), context.config("bpe_path"))

    df_records = []

    with context.progress(label = "Reading enterprise census ...") as progress:
        for df_chunk in pd.read_csv(csv_file, encoding = "latin1", chunksize = 10240, sep=';'):
            progress.update(len(df_chunk))

            df_chunk = df_chunk[df_chunk["DEP"].isin(requested_departements)]
            df_chunk = df_chunk[COLUMNS]

            if len(df_chunk) > 0:
                df_records.append(df_chunk)

    return pd.concat(df_records)

def validate(context):
    if not os.path.exists("%s/%s" % (context.config("data_path"), context.config("bpe_path"))):
        raise RuntimeError("BPE 2019 data is not available")

    return os.path.getsize("%s/%s" % (context.config("data_path"), context.config("bpe_path")))
