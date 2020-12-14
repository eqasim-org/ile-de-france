def create(output_path):
    """
    This script creates test fixtures for the Île-de-France / France pipeline.

    For that, we generate a couple of artificial data sets that have the same
    structure as the initial French data. We deliberately do *not* base this script
    on the actual data sets (e.g., to filter and reduce them), but generate them
    from scratch. This way, we can extend and improve these artificial files step
    by step to test specific features of the pipeline.

    In this artificial France, we have two regions: 10 and 20.

        +---------+---------+
        |         |         |
        |   10    |   20    | 50km
        |         |         |
        +---------+---------+
           50km       50km

    Both regions are divided in four departments 1A, 1B, 1C, 1D and 2A, 2B, 2C, 2D:

        +----+----+              +----+----+
        | 1A | 1B | 25km         | 2A | 2B | 25km
        +----+----+              +----+----+
        | 1C | 1D | 25km         | 2C | 2D | 25km
        +----+----+              +----+----+
         25km 25km                25km 25km

    Each department is divided in 25 municipalities, e.g. 1A001 to 1A025, which are boxes
    of 5km x 5km:

        001 002 003 004 005
        006 007 008 009 010
        011 012 013 014 015
        016 017 018 019 020
        021 022 023 024 025

    The municipalities are furthermore divided into IRIS of size 500m x 500m. This
    gives 10x10 = 100 IRIS per municipality, e.g. 1A00250001 to 1A00250100. Only
    few municipalities are covered by IRIS:
    - 1B013, 1B014, 1B018, 1B019
    - 2D007, 2D008, 2D012, 2D013
    """

    BPE_OBSERVATIONS = 500
    HTS_HOUSEHOLDS = 300
    HTS_HOUSEHOLD_MEMBERS = 3

    CENSUS_HOUSEHOLDS = 300
    CENSUS_HOUSEHOLD_MEMBERS = 3

    COMMUTE_FLOW_OBSERVATIONS = 500
    ADDRESS_OBSERVATIONS = 2000
    SIRENE_OBSERVATIONS = 2000

    import geopandas as gpd
    import pandas as pd
    import shapely.geometry as geo
    import numpy as np
    import os

    random = np.random.RandomState(0)

    REGION_LENGTH = 50 * 1e3
    DEPARTMENT_LENGTH = 25 * 1e3
    MUNICIPALITY_LENGTH = 5 * 1e3
    IRIS_LENGTH = 500

    anchor_x = 638589
    anchor_y = 6861081

    # Define internal zoing system
    print("Creating zoning system ...")
    df = []

    WITH_IRIS = set([
        "1B013", "1B014", "1B018", "1B019",
        "2D007", "2D008", "2D012", "2D013"
    ])

    for region_column in np.arange(2):
        region_prefix = region_column + 1
        region_number = region_prefix * 10

        region_x = anchor_x + region_column * REGION_LENGTH
        region_y = anchor_y + 0

        for department_row in np.arange(2):
            for department_column in np.arange(2):
                department_letter = { (0, 0): "A", (0, 1): "B", (1, 0): "C", (1, 1): "D" }[(
                    department_row, department_column
                )]

                department_name = "%d%s" % (region_prefix, department_letter)

                department_x = region_x + department_column * DEPARTMENT_LENGTH
                department_y = region_y - department_row * DEPARTMENT_LENGTH

                for municipality_index in np.arange(25):
                    municipality_name = "%s%03d" % (department_name, municipality_index + 1)

                    municipality_row = municipality_index // 5
                    municipality_column = municipality_index % 5

                    municipality_x = department_x + municipality_column * MUNICIPALITY_LENGTH
                    municipality_y = department_y - municipality_row * MUNICIPALITY_LENGTH

                    if municipality_name in WITH_IRIS:
                        for iris_index in np.arange(100):
                            iris_name = "%s%04d" % (municipality_name, iris_index + 1)

                            iris_row = iris_index // 10
                            iris_column = iris_index % 10

                            iris_x = municipality_x + iris_column * IRIS_LENGTH
                            iris_y = municipality_y - iris_row * IRIS_LENGTH

                            iris_polygon = geo.Polygon([
                                (iris_x, iris_y), (iris_x + IRIS_LENGTH, iris_y),
                                (iris_x + IRIS_LENGTH, iris_y - IRIS_LENGTH),
                                (iris_x, iris_y - IRIS_LENGTH)
                            ])

                            df.append(dict(
                                region = region_number,
                                department = department_name,
                                municipality = municipality_name,
                                iris = iris_name,
                                geometry = iris_polygon
                            ))

                    else:
                        municipality_polygon = geo.Polygon([
                            (municipality_x, municipality_y), (municipality_x + MUNICIPALITY_LENGTH, municipality_y),
                            (municipality_x + MUNICIPALITY_LENGTH, municipality_y - MUNICIPALITY_LENGTH),
                            (municipality_x, municipality_y - MUNICIPALITY_LENGTH)
                        ])

                        iris_name = "%s0000" % municipality_name

                        df.append(dict(
                            region = region_number,
                            department = department_name,
                            municipality = municipality_name,
                            iris = iris_name,
                            geometry = municipality_polygon
                        ))

    df = pd.DataFrame.from_records(df)
    df = gpd.GeoDataFrame(df, crs = "EPSG:2154")

    # Dataset: IRIS zones
    # Required attributes: CODE_IRIS, INSEE_COM, geometry
    print("Creating IRIS zones ...")

    df_iris = df.copy()
    df_iris = df_iris[["iris", "municipality", "geometry"]].rename(columns = dict(
        iris = "CODE_IRIS", municipality = "INSEE_COM"
    ))

    os.mkdir("%s/iris_2017" % output_path)
    df_iris.to_file("%s/iris_2017/CONTOURS-IRIS.shp" % output_path)

    # Dataset: Codes
    # Required attributes: CODE_IRIS, DEPCOM, DEP, REG
    print("Creating codes ...")

    df_codes = df.copy()
    df_codes = df_codes[["iris", "municipality", "department", "region"]].rename(columns = dict(
        iris = "CODE_IRIS", municipality = "DEPCOM", department = "DEP", region = "REG"
    ))

    os.mkdir("%s/codes_2017" % output_path)
    df_codes.to_excel(
        "%s/codes_2017/reference_IRIS_geo2017.xls" % output_path,
        sheet_name = "Emboitements_IRIS",
        startrow = 5, index = False
    )

    # Dataset: Aggregate census
    # Required attributes: IRIS, COM, DEP, REG, P15_POP
    print("Creating aggregate census ...")

    df_population = df.copy()
    df_population = df_population[["iris", "municipality", "department", "region"]].rename(columns = dict(
        iris = "IRIS", municipality = "COM", department = "DEP", region = "REG"
    ))

    # Set all population to fixed number
    df_population["P15_POP"] = 120.0

    os.mkdir("%s/rp_2015" % output_path)
    df_population.to_excel(
        "%s/rp_2015/base-ic-evol-struct-pop-2015.xls" % output_path,
        sheet_name = "IRIS", startrow = 5, index = False
    )

    # Dataset: BPE
    # Required attributes: DCIRIS, LAMBERT_X, LAMBERT_Y, TYPEQU, DEPCOM, DEP
    print("Creating BPE ...")

    # We put enterprises at the centroid of the shapes
    observations = BPE_OBSERVATIONS
    categories = np.array(["A", "B", "C", "D", "E", "F", "G"])

    df_selection = df.iloc[random.randint(0, len(df), size = observations)].copy()
    df_selection["DCIRIS"] = df_selection["iris"]
    df_selection["DEPCOM"] = df_selection["municipality"]
    df_selection["DEP"] = df_selection["department"]
    df_selection["LAMBERT_X"] = df_selection["geometry"].centroid.x
    df_selection["LAMBERT_Y"] = df_selection["geometry"].centroid.y
    df_selection["TYPEQU"] = categories[random.randint(0, len(categories), size = len(df_selection))]

    # Deliberately set coordinates for some to NaN
    df_selection["LAMBERT_X"].iloc[-10:] = np.nan
    df_selection["LAMBERT_Y"].iloc[-10:] = np.nan

    import pysal

    types = [("C", 10, 0), ("C", 12, 0), ("C", 12, 0), ("C", 4, 0), ("C", 5, 0), ("C", 3, 0)]
    columns = ["DCIRIS", "LAMBERT_X", "LAMBERT_Y", "TYPEQU", "DEPCOM", "DEP"]

    os.mkdir("%s/bpe_2018" % output_path)
    db = pysal.open("%s/bpe_2018/bpe18_ensemble_xy.dbf" % output_path, "w")

    db.header = columns
    db.field_spec = types

    for index, row in df_selection[columns].iterrows():
        db.write(row)

    db.close()

    # Dataset: Tax data
    # Required attributes: CODGEO, D115, ..., D915
    print("Creating FILOSOFI ...")

    df_income = df.drop_duplicates("municipality")[["municipality"]].rename(columns = dict(municipality = "CODGEO"))
    df_income["D115"] = 9122.0
    df_income["D215"] = 11874.0
    df_income["D315"] = 14430.0
    df_income["D415"] = 16907.0
    df_income["Q215"] = 22240.0
    df_income["D615"] = 22827.0
    df_income["D715"] = 25699.0
    df_income["D815"] = 30094.0
    df_income["D915"] = 32303.0

    # Deliberately remove some of them
    df_income = df_income[~df_income["CODGEO"].isin([
        "1A015", "1A016"
    ])]

    # Deliberately only provide median for some
    f = df_income["CODGEO"].isin(["1D002", "1D005"])
    df_income.loc[f, "D215"] = np.nan

    os.mkdir("%s/filosofi_2015" % output_path)
    df_income.to_excel(
        "%s/filosofi_2015/FILO_DISP_COM.xls" % output_path,
        sheet_name = "ENSEMBLE", startrow = 5, index = False
    )

    # Data set: ENTD
    print("Creating ENTD ...")

    data = dict(
        Q_MENAGE = [],
        Q_TCM_MENAGE = [],
        Q_INDIVIDU = [],
        Q_TCM_INDIVIDU = [],
        K_DEPLOC = [],
    )

    for household_index in range(HTS_HOUSEHOLDS):
        household_id = household_index

        region = random.choice([10, 20])
        department = "%d%s" % (region // 10, random.choice(["A", "B", "C", "D"]))

        data["Q_MENAGE"].append(dict(
            DEP = department, idENT_MEN = household_id, PONDV1 = 1.0,
            RG = region, V1_JNBVELOADT = random.randint(4),
            V1_JNBVEH = random.randint(3), V1_JNBMOTO = random.randint(2),
            V1_JNBCYCLO = 0
        ))

        data["Q_TCM_MENAGE"].append(dict(
            NPERS = 3, PONDV1 = 1.0, DEP = department,
            idENT_MEN = household_id, RG = region,
            TrancheRevenuMensuel = random.choice([
                "Moins de 400", "De 400", "De 600", "De 800",
                "De 1 000", "De 1 200", "De 1 500", "De 1800",
                "De 2 000", "De 2 500", "De 3 000", "De 4 000",
                "De 6 000", "10 000"
            ])
        ))

        for person_index in range(HTS_HOUSEHOLD_MEMBERS):
            person_id = household_id * 1000 + person_index
            studies = random.random_sample() < 0.3

            data["Q_INDIVIDU"].append(dict(
                IDENT_IND = person_id, idENT_MEN = household_id,
                RG = region,
                V1_GPERMIS = random.choice([1, 2]), V1_GPERMIS2R = random.choice([1, 2]),
                V1_ICARTABON = random.choice([1, 2]),
            ))

            data["Q_TCM_INDIVIDU"].append(dict(
                AGE = random.randint(90), SEXE = random.choice([1, 2]),
                CS24 = random.randint(8) * 10, DEP = department,
                ETUDES = 1 if studies else 2, IDENT_IND = person_id,
                IDENT_MEN = household_id, PONDV1 = 1.0,
                SITUA = random.choice([1, 2])
            ))

            if person_index == 0: # Only one person per household has activity chain
                home_department = department
                work_department = random.choice(df["department"].unique())

                purpose = "1.11" if studies else "9"
                mode = random.choice(["1", "2", "2.20", "2.23", "4"])

                data["K_DEPLOC"].append(dict(
                    IDENT_IND = person_id, V2_MMOTIFDES = purpose, V2_MMOTIFORI = 1,
                    V2_TYPJOUR = 1, V2_MORIHDEP = "08:00:00", V2_MDESHARR = "09:00:00",
                    V2_MDISTTOT = 3, # km
                    IDENT_JOUR = 1, V2_MTP = mode,
                    V2_MDESDEP = work_department,
                    V2_MORIDEP = home_department,
                    NDEP = 4, V2_MOBILREF = 1, PONDKI = 3.0
                ))

                data["K_DEPLOC"].append(dict(
                    IDENT_IND = person_id, V2_MMOTIFDES = 2, V2_MMOTIFORI = purpose,
                    V2_TYPJOUR = 1, V2_MORIHDEP = "17:00:00", V2_MDESHARR = "17:30:00",
                    V2_MDISTTOT = 3, # km
                    IDENT_JOUR = 1, V2_MTP = mode,
                    V2_MDESDEP = home_department,
                    V2_MORIDEP = work_department,
                    NDEP = 4, V2_MOBILREF = 1, PONDKI = 3.0
                ))

                data["K_DEPLOC"].append(dict(
                    IDENT_IND = person_id, V2_MMOTIFDES = 1, V2_MMOTIFORI = 2,
                    V2_TYPJOUR = 1, V2_MORIHDEP = "18:00:00", V2_MDESHARR = "19:00:00",
                    V2_MDISTTOT = 3, # km
                    IDENT_JOUR = 1, V2_MTP = mode,
                    V2_MDESDEP = home_department,
                    V2_MORIDEP = home_department,
                    NDEP = 4, V2_MOBILREF = 1, PONDKI = 3.0
                ))

                # Add a tail
                data["K_DEPLOC"].append(dict(
                    IDENT_IND = person_id, V2_MMOTIFDES = 2, V2_MMOTIFORI = 1,
                    V2_TYPJOUR = 1, V2_MORIHDEP = "21:00:00", V2_MDESHARR = "22:00:00",
                    V2_MDISTTOT = 3, # km
                    IDENT_JOUR = 1, V2_MTP = mode,
                    V2_MDESDEP = home_department,
                    V2_MORIDEP = home_department,
                    NDEP = 4, V2_MOBILREF = 1, PONDKI = 3.0
                ))

    os.mkdir("%s/entd_2008" % output_path)
    pd.DataFrame.from_records(data["Q_MENAGE"]).to_csv("%s/entd_2008/Q_menage.csv" % output_path, index = False, sep = ";")
    pd.DataFrame.from_records(data["Q_TCM_MENAGE"]).to_csv("%s/entd_2008/Q_tcm_menage_0.csv" % output_path, index = False, sep = ";")
    pd.DataFrame.from_records(data["Q_INDIVIDU"]).to_csv("%s/entd_2008/Q_individu.csv" % output_path, index = False, sep = ";")
    pd.DataFrame.from_records(data["Q_TCM_INDIVIDU"]).to_csv("%s/entd_2008/Q_tcm_individu.csv" % output_path, index = False, sep = ";")
    pd.DataFrame.from_records(data["K_DEPLOC"]).to_csv("%s/entd_2008/K_deploc.csv" % output_path, index = False, sep = ";")


    # Data set: EGT
    print("Creating EGT ...")

    data = dict(
        households = [],
        persons = [],
        trips = []
    )

    for household_index in range(HTS_HOUSEHOLDS):
        household_id = household_index

        municipality = random.choice(df["municipality"].unique())
        region = df[df["municipality"] == municipality]["region"].values[0]
        department = df[df["municipality"] == municipality]["department"].values[0]

        data["households"].append(dict(
            RESDEP = department, NQUEST = household_id, POIDSM = 1.0,
            NB_VELO = random.randint(3), NB_VD = random.randint(2),
            RESCOMM = municipality, NB_2RM = 0,
            MNP = 3, REVENU = random.randint(12)
        ))

        for person_index in range(HTS_HOUSEHOLD_MEMBERS):
            person_id = household_id * 1000 + person_index
            studies = random.random_sample() < 0.3

            data["persons"].append(dict(
                RESDEP = department, NP = person_id, POIDSP = 1.0,
                NQUEST = household_id, SEXE = random.choice([1, 2]),
                AGE = random.randint(90), PERMVP = random.choice([1, 2]),
                ABONTC = random.choice([1, 2]), OCCP = 3 if studies else 2,
                PERM2RM = random.choice([1, 2]), NBDEPL = 2, CS8 = random.randint(9)
            ))

            home_department = department
            home_municipality = municipality

            work_municipality = random.choice(df["municipality"].unique())
            work_region = df[df["municipality"] == work_municipality]["region"].values[0]
            work_department = df[df["municipality"] == work_municipality]["department"].values[0]

            purpose = 21 if studies else 11
            mode = random.choice([1, 2, 3, 5, 7])

            data["trips"].append(dict(
                NQUEST = household_id, NP = person_id,
                ND = 1, ORDEP = home_department, DESTDEP = work_department,
                ORH = 8, ORM = 0, DESTH = 9, DESTM = 0, ORCOMM = home_municipality,
                DESTCOMM = work_municipality, DPORTEE = 3, MODP_H7 = 2,
                DESTMOT_H9 = purpose, ORMOT_H9 = 1
            ))

            data["trips"].append(dict(
                NQUEST = household_id, NP = person_id,
                ND = 1, ORDEP = work_department, DESTDEP = home_department,
                ORH = 8, ORM = 0, DESTH = 9, DESTM = 0, ORCOMM = work_municipality,
                DESTCOMM = home_municipality, DPORTEE = 3, MODP_H7 = 2,
                DESTMOT_H9 = 31, ORMOT_H9 = purpose
            ))

            data["trips"].append(dict(
                NQUEST = household_id, NP = person_id,
                ND = 2, ORDEP = home_department, DESTDEP = home_department,
                ORH = 17, ORM = 0, DESTH = 18, DESTM = 0, ORCOMM = home_municipality,
                DESTCOMM = home_municipality, DPORTEE = 3, MODP_H7 = 2,
                DESTMOT_H9 = 1, ORMOT_H9 = 31
            ))

    os.mkdir("%s/egt_2010" % output_path)
    pd.DataFrame.from_records(data["households"]).to_csv("%s/egt_2010/Menages_semaine.csv" % output_path, index = False, sep = ",")
    pd.DataFrame.from_records(data["persons"]).to_csv("%s/egt_2010/Personnes_semaine.csv" % output_path, index = False, sep = ",")
    pd.DataFrame.from_records(data["trips"]).to_csv("%s/egt_2010/Deplacements_semaine.csv" % output_path, index = False, sep = ",")

    # Data set: Census
    print("Creating census ...")

    persons = []

    for household_index in range(CENSUS_HOUSEHOLDS):
        household_id = household_index

        iris = df["iris"].iloc[random.randint(len(df))]
        department = iris[:2]
        if iris.endswith("0000"): iris = iris[:-4] + "XXXX"

        if random.random_sample() < 0.1: # For some, commune is not known
            iris = "ZZZZZZZZZ"

        destination_municipality = random.choice(df["municipality"].unique())
        destination_region = df[df["municipality"] == destination_municipality]["region"].values[0]
        destination_department = df[df["municipality"] == destination_municipality]["department"].values[0]

        for person_index in range(CENSUS_HOUSEHOLD_MEMBERS):
            persons.append(dict(
                CANTVILLE = "ABCE", NUMMI = household_id,
                AGED = "%03d" % random.randint(90), COUPLE = random.choice([1, 2]),
                CS1 = random.randint(9),
                DEPT = department, IRIS = iris, REGION = region, ETUD = random.choice([1, 2]),
                ILETUD = 4 if department != destination_department else 0,
                ILT = 4 if department != destination_department else 0,
                IPONDI = float(1.0),
                SEXE = random.choice([1, 2]),
                TACT = random.choice([1, 2]),
                TRANS = 4, VOIT = random.randint(3), DEROU = random.randint(2)
            ))

    columns = [
        "CANTVILLE", "NUMMI", "AGED", "COUPLE", "CS1", "DEPT", "IRIS", "REGION",
        "ETUD", "ILETUD", "ILT", "IPONDI",
        "SEXE", "TACT", "TRANS", "VOIT", "DEROU"
    ]

    types = [
        ("C", 5, 0),
        ("C", 7, 0),
        ("C", 3, 0),
        ("C", 1, 0),
        ("C", 1, 0), # CS 1
        ("C", 3, 0),
        ("C", 9, 0),
        ("C", 2, 0),
        ("C", 1, 0),
        ("C", 1, 0),
        ("C", 1, 0),
        ("N", 10, 7), # IPONDI
        ("C", 1, 0),
        ("C", 2, 0),
        ("C", 1, 0),
        ("C", 1, 0),
        ("C", 1, 0),
    ]

    df_persons = pd.DataFrame.from_records(persons)[columns]

    db = pysal.open("%s/rp_2015/FD_INDCVIZA_2015.dbf" % output_path, "w")
    db.header = columns
    db.field_spec = types
    for index, row in df_persons.iterrows():
        db.write(row)
    db.close()

    # Data set: commute flows
    print("Creating commute flows ...")

    municipalities = df["municipality"].unique()
    observations = COMMUTE_FLOW_OBSERVATIONS

    # ... work
    df_work = pd.DataFrame(dict(
        COMMUNE = municipalities[random.randint(0, len(municipalities), observations)],
        DCLT = municipalities[random.randint(0, len(municipalities), observations)],
        TRANS = random.randint(1, 6, size = (observations,))
    ))

    df_work["ARM"] = "Z"
    df_work["IPONDI"] = 1.0

    columns = ["COMMUNE", "DCLT", "TRANS", "ARM", "IPONDI"]
    types = [("C", 5, 0), ("C", 5, 0), ("C", 1, 0), ("C", 5, 0), ("N", 10, 7)]
    db = pysal.open("%s/rp_2015/FD_MOBPRO_2015.dbf" % output_path, "w")
    db.header = columns
    db.field_spec = types
    for index, row in df_work[columns].iterrows():
        db.write(row)
    db.close()

    # ... education
    df_education = pd.DataFrame(dict(
        COMMUNE = municipalities[random.randint(0, len(municipalities), observations)],
        DCETUF = municipalities[random.randint(0, len(municipalities), observations)]
    ))
    df_education["ARM"] = "Z"
    df_education["IPONDI"] = 1.0

    columns = ["COMMUNE", "DCETUF", "ARM", "IPONDI"]
    types = [("C", 5, 0), ("C", 5, 0), ("C", 5, 0), ("N", 10, 7)]
    db = pysal.open("%s/rp_2015/FD_MOBSCO_2015.dbf" % output_path, "w")
    db.header = columns
    db.field_spec = types
    for index, row in df_education[columns].iterrows():
        db.write(row)
    db.close()

    # Data set: BD-TOPO
    print("Creating BD-TOPO ...")

    observations = ADDRESS_OBSERVATIONS

    streets = np.array([
        "A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M",
        "N", "O", "P", "Q", "R", "S", "T", "U", "V", "W", "X", "Y", "Z"
    ])[random.randint(0, 26, observations)]

    numbers = random.randint(0, 20, observations)

    x = random.random_sample(size = (observations,)) * 100
    y = random.random_sample(size = (observations,)) * 50

    df_bdtopo = gpd.GeoDataFrame({
        "CODE_INSEE": municipalities[random.randint(0, len(municipalities), observations)],
        "NUMERO": numbers,
        "NOM_1": streets,
        "geometry": [
            geo.Point(x, y) for x, y in zip(x, y)
        ]
    }, crs = "EPSG:2154")

    df_bdtopo["NOM_1"] = "R " + df_bdtopo["NOM_1"]

    os.mkdir("%s/bdtopo" % output_path)
    df_bdtopo.to_file("%s/bdtopo/ADRESSE.shp" % output_path)

    # Data set: SIRENE
    print("Creating SIRENE ...")

    observations = SIRENE_OBSERVATIONS

    streets = np.array([
        "A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M",
        "N", "O", "P", "Q", "R", "S", "T", "U", "V", "W", "X", "Y", "Z"
    ])[random.randint(0, 26, observations)]

    numbers = random.randint(0, 20, observations)

    df_sirene = pd.DataFrame({
        "siret": random.randint(0, 99999999, observations),
        "libelleVoieEtablissement": streets,
        "numeroVoieEtablissement": numbers,
        "codeCommuneEtablissement": municipalities[random.randint(0, len(municipalities), observations)],
        "etatAdministratifEtablissement": "A"
    })

    df_sirene["activitePrincipaleEtablissement"] = "52.1"
    df_sirene["trancheEffectifsEtablissement"] = "03"
    df_sirene["typeVoieEtablissement"] = "RUE"

    os.mkdir("%s/sirene" % output_path)
    df_sirene.to_csv("%s/sirene/StockEtablissement_utf8.csv" % output_path, index = False)

    # Data set: OSM
    # We add add a road grid of 500m
    print("Creating OSM ...")
    import itertools

    osm = []
    osm.append('<?xml version="1.0" encoding="UTF-8"?>')
    osm.append('<osm version="0.6">')

    df_nodes = []
    links = []

    node_index = 1

    lengthx = 200
    lengthy = 100

    for i in range(lengthx):
        for j in range(lengthy):
            df_nodes.append(dict(
                id = node_index,
                geometry = geo.Point(anchor_x + 500 * i + 250, anchor_y - 500 * j - 250)
            ))

            if j < lengthy - 1:
                links.append([node_index, node_index + 1])

            if i < lengthx - 1:
                links.append([node_index, node_index + lengthx])

            node_index += 1

    df_nodes = gpd.GeoDataFrame(df_nodes, crs = "EPSG:2154")
    df_nodes = df_nodes.to_crs("EPSG:4326")

    for row in df_nodes.itertuples():
        osm.append('<node id="%d" lat="%f" lon="%f" version="3" timestamp="2010-12-05T17:00:00" />' % (
            row[1], row[2].y, row[2].x
        ))

    for index, link in enumerate(links):
        osm.append('<way id="%d" version="3" timestamp="2010-12-05T17:00:00">' % (index + 1))
        osm.append('<nd ref="%d" />' % link[0])
        osm.append('<nd ref="%d" />' % link[1])
        osm.append('<tag k="highway" v="primary" />')
        osm.append('</way>')

    osm.append('</osm>')

    import gzip
    os.mkdir("%s/osm" % output_path)
    with gzip.open("%s/osm/ile-de-france-latest.osm.gz" % output_path, "wb+") as f:
        f.write(bytes("\n".join(osm), "utf-8"))

    import subprocess
    subprocess.check_call([
        "osmosis", "--read-xml", "%s/osm/ile-de-france-latest.osm.gz" % output_path,
        "--write-pbf", "%s/osm/ile-de-france-latest.osm.pbf" % output_path
    ])

    # Data set: GTFS
    print("Creating GTFS ...")

    feed = {}

    feed["agency"] = pd.DataFrame.from_records([dict(
        agency_id = 1, agency_name = "eqasim", agency_timezone = "Europe/Paris",
        agency_url = "https://eqasim.org"
    )])

    feed["calendar"] = pd.DataFrame.from_records([dict(
        service_id = 1, monday = 1, tuesday = 1, wednesday = 1,
        thursday = 1, friday = 1, saturday = 1, sunday = 1, start_date = "20100101",
        end_date = "20500101"
    )])

    feed["routes"] = pd.DataFrame.from_records([dict(
        route_id = 1, agency_id = 1, route_short_name = "EQ",
        route_long_name = "The eqasim train", route_desc = "",
        route_type = 2
    )])

    stops = []

    df_stops = df[df["municipality"].isin(["1B019", "2D007"])].copy()
    df_stops = df_stops.to_crs("EPSG:4326")

    feed["stops"] = pd.DataFrame.from_records([dict(
        stop_id = "A", stop_code = "A", stop_name = "A",
        stop_desc = "",
        stop_lat = df_stops["geometry"].iloc[0].centroid.y,
        stop_lon = df_stops["geometry"].iloc[0].centroid.x,
        location_type = 1, parent_station = None
    ), dict(
        stop_id = "B", stop_code = "B", stop_name = "B",
        stop_desc = "",
        stop_lat = df_stops["geometry"].iloc[1].centroid.y,
        stop_lon = df_stops["geometry"].iloc[1].centroid.x,
        location_type = 1, parent_station = None
    )])

    trips = []
    times = []

    trip_id = 1

    for origin, destination in [("A", "B"), ("B", "A")]:
        for hour in np.arange(1, 24):
            trips.append(dict(
                route_id = 1, service_id = 1, trip_id = trip_id
            ))

            times.append(dict(
                trip_id = trip_id, arrival_time = "%02d:00:00" % hour,
                departure_time = "%02d:00:00" % hour, stop_id = origin, stop_sequence = 1
            ))

            times.append(dict(
                trip_id = trip_id, arrival_time = "%02d:00:00" % (hour + 1),
                departure_time = "%02d:00:00" % (hour + 1), stop_id = destination, stop_sequence = 2
            ))

            trip_id += 1

    feed["trips"] = pd.DataFrame.from_records(trips)
    feed["stop_times"] = pd.DataFrame.from_records(times)

    # Transfers
    feed["transfers"] = pd.DataFrame(dict(
        from_stop_id = [], to_stop_id = [], transfer_type = []
    ))

    os.mkdir("%s/gtfs" % output_path)

    import data.gtfs.utils
    data.gtfs.utils.write_feed(feed, "%s/gtfs/IDFM_gtfs.zip" % output_path)

if __name__ == "__main__":
    import sys
    create(sys.argv[1])
