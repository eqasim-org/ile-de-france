import simpledbf
from tqdm import tqdm
import pandas as pd
import os

"""
This stage loads the raw data from the French population census.
"""

def configure(context):
    context.config("data_path")

COLUMNS = [
    "CANTVILLE", "NUMMI", "AGED",
    "APAF", "ARM", "COUPLE", "CS1",
    "DEPT", "DIPL_15", "ETUD", "ILETUD",
    "ILT", "INATC", "INPER", "INPERF",
    "IPONDI", "IRIS", "LIENF", "MOCO",
    "MODV", "REGION", "SEXE", "SFM",
    "STAT_CONJ", "TACT", "TRANS", "TRIRIS",
    "TYPFC", "TYPMC", "TYPMR", "VOIT", "DEROU"
]

def execute(context):
    table = simpledbf.Dbf5("%s/rp_2015/FD_INDCVIZA_2015.dbf" % context.config("data_path"))
    records = []

    with context.progress(total = 4320619, label = "Reading census ...") as progress:
        for df_chunk in table.to_dataframe(chunksize = 10240):
            progress.update(len(df_chunk))
            df_chunk = df_chunk[df_chunk["REGION"] == "11"]
            df_chunk = df_chunk[COLUMNS]

            if len(df_chunk) > 0:
                records.append(df_chunk)

    pd.concat(records).to_hdf("%s/census.hdf" % context.path(), "census")

def validate(context):
    if not os.path.exists("%s/rp_2015/FD_INDCVIZA_2015.dbf" % context.config("data_path")):
        raise RuntimeError("RP 2015 data is not available")

    return os.path.getsize("%s/rp_2015/FD_INDCVIZA_2015.dbf" % context.config("data_path"))
