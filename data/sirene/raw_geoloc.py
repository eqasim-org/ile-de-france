import os
import pandas as pd

"""
This stage loads the raw data from the French enterprise registry.
"""

def configure(context):
    context.config("data_path")
    context.config("siret_geo_path", "sirene/GeolocalisationEtablissement_Sirene_pour_etudes_statistiques_utf8.csv")
    
    context.stage("data.spatial.codes")


def execute(context):
    
    # lecture du fichier géolocalisé de l'INSEE pour la base SIRET
    COLUMNS_DTYPES = {
        "siret":"int64", 
        "x":"float", 
        "y":"float",
    }

    df_siret_geoloc = pd.DataFrame(columns=["siret","x","y"])
    
    with context.progress(label = "Reading geolocaized SIRET by INSEE(RIL matched) ...") as progress:
         csv = pd.read_csv("%s/%s" % (context.config("data_path"), context.config("siret_geo_path")), 
                          usecols = COLUMNS_DTYPES.keys(), sep=";",dtype = COLUMNS_DTYPES,chunksize = 10240)
    
         for df_chunk in csv:
            progress.update(len(df_chunk))
            pd.concat([df_siret_geoloc, df_chunk])

    return df_siret_geoloc

 

def validate(context):
    if not os.path.exists("%s/%s" % (context.config("data_path"), context.config("siret_geo_path"))):
        raise RuntimeError("SIRENE: geolocaized SIRET data is not available")

    return os.path.getsize("%s/%s" % (context.config("data_path"), context.config("siret_geo_path")))
