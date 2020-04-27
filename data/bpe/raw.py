import simpledbf
from tqdm import tqdm
import pandas as pd
import os

"""
This stage loads the raw data from the French enterprise census.
"""

def configure(context):
    context.config("data_path")

COLUMNS = [
    "DCIRIS", "LAMBERT_X", "LAMBERT_Y",
    "REG", "TYPEQU", "DEPCOM"
]

def execute(context):
    table = simpledbf.Dbf5("%s/bpe_2018/bpe18_ensemble_xy.dbf" % context.config("data_path"), codec = "latin1")
    df_records = []

    with context.progress(total = 2504782, label = "Reading enterprise census ...") as progress:
        for df_chunk in table.to_dataframe(chunksize = 10240):
            progress.update(len(df_chunk))
            df_chunk = df_chunk[df_chunk["REG"] == "11"]
            df_chunk = df_chunk[COLUMNS]

            if len(df_chunk) > 0:
                df_records.append(df_chunk)


    df_records = pd.concat(df_records)
    return df_records

def validate(context):
    if not os.path.exists("%s/bpe_2018/bpe18_ensemble_xy.dbf" % context.config("data_path")):
        raise RuntimeError("BPE 2018 data is not available")

    return os.path.getsize("%s/bpe_2018/bpe18_ensemble_xy.dbf" % context.config("data_path"))
