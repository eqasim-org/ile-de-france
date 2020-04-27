import simpledbf
from tqdm import tqdm
import pandas as pd
import os

"""
This stage loads the raw data of the French HTS (ENTD).
"""

Q_MENAGE_COLUMNS = [
    "DEP", "idENT_MEN", "PONDV1", "RG", #"V1_JNBVEH",
    "V1_JNBVELOADT", "V1_JNBVELOENF",
    "V1_LOGANIMOESP_A", "V1_LOGANIMOESP_B",
    "V1_JNBVEH", "V1_JNBMOTO", "V1_JNBCYCLO", "V1_JNBAUTVEH", "V1_JNBCCVUL"
]

Q_TCM_MENAGE_COLUMNS = [
    "NPERS", "PONDV1", "TrancheRevenuMensuel",
    "DEP", "idENT_MEN", "RG",
    "TYPMEN5", "TYPMEN15", "numcom_AUCat", "numcom_AU2010",
    "numcom_UU2010", "numcom_UUCat", "numcom_zhu"
]

Q_INDIVIDU_COLUMNS = [
    "AGE", "CS24", "DEP", "DIP14", "IDENT_IND", "idENT_MEN",
    "MOB_ETUDES", "MOB_TRAVAIL", "RG",
    "SEXE", "SITUA", "V1_GPERMIS", "V1_ICARTABON",
    "V1_TYPMREG", "V1_GPERMIS2R"
]

for i in range(1, 5):
    Q_INDIVIDU_COLUMNS += ["V1_ITYP%dCART" % i]
    for j in ["A", "B", "C", "D", "E", "F", "G"]:
        Q_INDIVIDU_COLUMNS += ["V1_ITYP%dRES_%s" % (i, j)]

Q_TCM_INDIVIDU_COLUMNS = [
    "AGE", "COUPLE", "CS24", "DEP", "DIP14", "ENFANT",
    "ETUDES", "IDENT_IND", "IDENT_MEN", "INATIO",
    "PONDV1", "SEXE", "SITUA", "rg", "ETAMATRI"
]

K_DEPLOC_COLUMNS = [
    "IDENT_IND", "V2_MMOTIFDES", "V2_MMOTIFORI", "V2_MMOY1S", "V2_MORIDOM",
    "V2_TYPJOUR", "V2_MORIHDEP", "V2_MDESHARR", "V2_MDISTTOT",
    "IDENT_JOUR", "v2_moricom_AU2010", "v2_mdescom_AU2010", "idENT_DEP", "V2_MTP",
    "V2_DVO_LOC", "V2_MDESDEP", "V2_MORIDEP", "NDEP", "V2_MOBILREF",
    "PONDKI", "DEP", "RG", "V2_DLOCAL", "POIDS_JOUR", "V2_DUREE"
]

Q_IND_LIEU_TEG_COLUMNS = [
    "IDENT_IND", "V1_BTRAVDIST", "V1_BTRAVTEMPSA", "V1_BTRAVTEMPSR",
    "V1_BTRAVMTP", "IDENT_MEN", "idENT_LIEU", "TYPLIEU", "dvo_teg"
]

def configure(context):
    context.config("data_path")

def execute(context):
    df_individu = pd.read_csv(
        "%s/entd_2008/Q_individu.csv" % context.config("data_path"),
        sep = ";", encoding = "latin1", usecols = Q_INDIVIDU_COLUMNS,
        dtype = { "DEP": str }
    )

    df_tcm_individu = pd.read_csv(
        "%s/entd_2008/Q_tcm_individu.csv" % context.config("data_path"),
        sep = ";", encoding = "latin1", usecols = Q_TCM_INDIVIDU_COLUMNS,
        dtype = { "DEP": str }
    )

    df_menage = pd.read_csv(
        "%s/entd_2008/Q_menage.csv" % context.config("data_path"),
        sep = ";", encoding = "latin1", usecols = Q_MENAGE_COLUMNS,
        dtype = { "DEP": str }
    )

    df_tcm_menage = pd.read_csv(
        "%s/entd_2008/Q_tcm_menage_0.csv" % context.config("data_path"),
        sep = ";", encoding = "latin1", usecols = Q_TCM_MENAGE_COLUMNS,
        dtype = { "DEP": str }
    )

    df_deploc = pd.read_csv(
        "%s/entd_2008/K_deploc.csv" % context.config("data_path"),
        sep = ";", encoding = "latin1", usecols = K_DEPLOC_COLUMNS,
        dtype = { "DEP": str }
    )

    df_ind_lieu_teg = pd.read_csv(
        "%s/entd_2008/Q_ind_lieu_teg.csv" % context.config("data_path"),
        sep = ";", encoding = "latin1", usecols = Q_IND_LIEU_TEG_COLUMNS,
        dtype = { "V1_BTRAVMTP": str }
    )

    return df_individu, df_tcm_individu, df_menage, df_tcm_menage, df_deploc, df_ind_lieu_teg

def validate(context):
    for name in ("Q_individu.csv", "Q_tcm_individu.csv", "Q_menage.csv", "Q_tcm_menage_0.csv", "K_deploc.csv", "Q_ind_lieu_teg.csv"):
        if not os.path.exists("%s/entd_2008/%s" % (context.config("data_path"), name)):
            raise RuntimeError("File missing from ENTD: %s" % name)

    return [
        os.path.getsize("%s/entd_2008/Q_individu.csv" % context.config("data_path")),
        os.path.getsize("%s/entd_2008/Q_tcm_individu.csv" % context.config("data_path")),
        os.path.getsize("%s/entd_2008/Q_menage.csv" % context.config("data_path")),
        os.path.getsize("%s/entd_2008/Q_tcm_menage_0.csv" % context.config("data_path")),
        os.path.getsize("%s/entd_2008/K_deploc.csv" % context.config("data_path")),
        os.path.getsize("%s/entd_2008/Q_ind_lieu_teg.csv" % context.config("data_path"))
    ]
