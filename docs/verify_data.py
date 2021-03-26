# This script checks the data availability for the Île-de-France and related
# scenarios. Sometimes, the respective agencies update the data sets or replace
# them with newer versions. In these cases, we need to react as, otherwise, the
# instructions in the documentation can not be followed anymore exactly. This
# script should be run regulary as it checks whether the files are still in
# place.

tests = [
    {
        "name": "Census 2015",
        "urls": [
            "https://www.insee.fr/fr/statistiques/fichier/3625223/RP2015_INDCVIZA_dbf.zip",
            "https://www.insee.fr/fr/statistiques/fichier/3625223/RP2015_INDCVIZE_dbf.zip",
            "https://www.insee.fr/fr/statistiques/fichier/3625223/RP2015_INDCVIZD_dbf.zip"
        ]
    },
    {
        "name": "OD Matrices 2015",
        "urls": [
            "https://www.insee.fr/fr/statistiques/fichier/3566008/rp2015_mobpro_dbase.zip",
            "https://www.insee.fr/fr/statistiques/fichier/3565982/rp2015_mobsco_dbase.zip"
        ]
    },
    {
        "name": "Population totals 2015",
        "urls": [
            "https://www.insee.fr/fr/statistiques/fichier/3627376/base-ic-evol-struct-pop-2015.zip"
        ]
    },
    {
        "name": "Filosofi 2015",
        "urls": [
            "https://www.insee.fr/fr/statistiques/fichier/3560118/indic-struct-distrib-revenu-2015-COMMUNES.zip",
            "https://www.insee.fr/fr/statistiques/fichier/3560118/indic-struct-distrib-revenu-2015-SUPRA.zip"
        ]
    },
    {
        "name": "BPE 2019",
        "urls": [
            "https://www.insee.fr/fr/statistiques/fichier/3568638/bpe19_ensemble_xy_dbase.zip"
        ]
    },
    {
        "name": "ENTD 2008",
        "urls": [
            "https://www.statistiques.developpement-durable.gouv.fr/sites/default/files/2018-12/Q_tcm_menage_0.csv",
            "https://www.statistiques.developpement-durable.gouv.fr/sites/default/files/2019-01/Q_tcm_individu.csv",
            "https://www.statistiques.developpement-durable.gouv.fr/sites/default/files/2019-01/Q_menage.csv",
            "https://www.statistiques.developpement-durable.gouv.fr/sites/default/files/2019-01/Q_individu.csv",
            "https://www.statistiques.developpement-durable.gouv.fr/sites/default/files/2019-01/Q_ind_lieu_teg.csv",
            "https://www.statistiques.developpement-durable.gouv.fr/sites/default/files/2019-01/K_deploc.csv"
        ]
    },
    {
        "name": "IRIS 2017",
        "urls": [] # Temporary not checking
    },
    {
        "name": "Zoning 2017",
        "urls": [
            "https://www.insee.fr/fr/statistiques/fichier/2017499/reference_IRIS_geo2017.zip"
        ]
    },
    {
        "name": "SIRENE",
        "urls": [
            "https://www.data.gouv.fr/fr/datasets/r/3966c990-d3a0-48b4-95b9-745fa24b2589"
        ]
    },
    {
        "name": "BD-TOPO",
        "urls": [
            "ftp://BDTOPO_V3_NL_ext:Ohp3quaz2aideel4@ftp3.ign.fr/BDTOPO_3-0_2020-12-15/BDTOPO_3-0_TOUSTHEMES_SHP_LAMB93_R11_2020-12-15.7z",
            "ftp://BDTOPO_V3_NL_ext:Ohp3quaz2aideel4@ftp3.ign.fr/BDTOPO_3-0_2020-12-15/BDTOPO_3-0_TOUSTHEMES_SHP_LAMB93_R76_2020-12-15.7z",
            "ftp://BDTOPO_V3_NL_ext:Ohp3quaz2aideel4@ftp3.ign.fr/BDTOPO_3-0_2020-12-15/BDTOPO_3-0_TOUSTHEMES_SHP_LAMB93_R84_2020-12-15.7z"
        ]
    },
    {
        "name": "BD-TOPO",
        "urls": [
            "ftp://BDTOPO_V3_NL_ext:Ohp3quaz2aideel4@ftp3.ign.fr/BDTOPO_3-0_2020-12-15/BDTOPO_3-0_TOUSTHEMES_SHP_LAMB93_R11_2020-12-15.7z",
            "ftp://BDTOPO_V3_NL_ext:Ohp3quaz2aideel4@ftp3.ign.fr/BDTOPO_3-0_2020-12-15/BDTOPO_3-0_TOUSTHEMES_SHP_LAMB93_R76_2020-12-15.7z",
            "ftp://BDTOPO_V3_NL_ext:Ohp3quaz2aideel4@ftp3.ign.fr/BDTOPO_3-0_2020-12-15/BDTOPO_3-0_TOUSTHEMES_SHP_LAMB93_R84_2020-12-15.7z"
        ]
    },
    {
        "name": "OSM",
        "urls": [
            "https://download.geofabrik.de/europe/france/ile-de-france-latest.osm.pbf",
            "https://download.geofabrik.de/europe/france/rhone-alpes-latest.osm.pbf",
            "https://download.geofabrik.de/europe/france/languedoc-roussillon-latest.osm.pbf",
            "https://download.geofabrik.de/europe/france/midi-pyrenees-latest.osm.pbf"
        ]
    },
    {
        "name": "GTFS",
        "urls": [
            "https://data.iledefrance-mobilites.fr/explore/dataset/offre-horaires-tc-gtfs-idf/files/736ca2f956a1b6cc102649ed6fd56d45/download/",
            "https://data.toulouse-metropole.fr/explore/dataset/tisseo-gtfs/files/bd1298f158bc39ed9065e0c17ebb773b/download/",
            "https://data.montpellier3m.fr/dataset/offre-de-transport-tam-en-gtfs/resource/7df23272-e7bd-4512-b8f1-e72aba9dee2c",
            # Not looking for Arc-en-Ciel (Busses Occitanie)
            "https://download.data.grandlyon.com/files/rdata/tcl_sytral.tcltheorique/GTFS_TCL.ZIP",
            "https://eu.ftp.opendatasoft.com/sncf/gtfs/export-ter-gtfs-last.zip",
            "https://eu.ftp.opendatasoft.com/sncf/gtfs/export-intercites-gtfs-last.zip",
            "https://ressources.data.sncf.com/explore/dataset/horaires-des-train-voyages-tgvinouiouigo/files/538b55483fac4c1dad455022a0257014/download/"
        ]
    }
]

# Start testing process
from urllib.request import urlopen

any_errors = False

for test in tests:
    print("Testing %s ..." % test["name"])

    for url in test["urls"]:
        try:
            urlopen(url)
        except:
            print("  ERROR:", url)
            any_errors = True

print("")
print("Summary:")

if any_errors:
    print("  There have been ERRORS!")
else:
    print("  Everything is OK!")

if any_errors:
    raise RuntimeError("There have been errors!")
