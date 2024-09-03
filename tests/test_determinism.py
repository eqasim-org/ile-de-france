import synpp
import os
import hashlib, gzip
from . import testdata
import sqlite3

def hash_sqlite_db(path):
    """
    Hash SQLite database file from its dump.

    As binary files of SQLite can be a different between OS (maybe due to a
    difference between the implementations of the driver) and only content
    matter, hashing the dump of the database is more relevant.
    """
    con = sqlite3.connect(path)
    hash = hashlib.md5()
    for line in con.iterdump():
        encoded = (line + "\n").encode()
        hash.update(encoded)
    con.close()
    return hash.hexdigest()


def hash_file(file):
    hash = hashlib.md5()

    # Gzip saves time stamps, so the gzipped files are NOT the same!
    opener = lambda: open(file, "rb")

    if file.endswith(".gz"):
        opener = lambda: gzip.open(file)

    with opener() as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash.update(chunk)

    f.close()
    return hash.hexdigest()

def test_determinism(tmpdir):
    data_path = str(tmpdir.mkdir("data"))
    testdata.create(data_path)

    for index in range(2):
        _test_determinism(index, data_path, tmpdir)

def _test_determinism(index, data_path, tmpdir):
    print("Running index %d" % index)

    cache_path = str(tmpdir.mkdir("cache_%d" % index))
    output_path = str(tmpdir.mkdir("output_%d" % index))
    config = dict(
        data_path = data_path, output_path = output_path,
        regions = [10, 11], sampling_rate = 1.0, hts = "entd",
        random_seed = 1000, processes = 1,
        secloc_maximum_iterations = 10,
        maven_skip_tests = True,
        matching_attributes = [
            "sex", "any_cars", "age_class", "socioprofessional_class",
            "income_class", "departement_id"
        ]
    )

    stages = [
        dict(descriptor = "synthesis.output"),
    ]

    synpp.run(stages, config, working_directory = cache_path)

    REFERENCE_CSV_HASHES = {
        "ile_de_france_activities.csv":     "53c44fb4026d2037729ee8ff1c8fb93f",
        "ile_de_france_households.csv":     "ca2a29ef13467326f937638f1ff8be1a",
        "ile_de_france_persons.csv":        "ddbe9b418c915b14e888b54efbdf9b1e",
        "ile_de_france_trips.csv":          "6c5f3427e41e683da768eeb53796a806",
    }

    REFERENCE_GPKG_HASHES = {
        "ile_de_france_activities.gpkg":    "50c11d1be6ef2f29a718c574da7fd8a3",
        "ile_de_france_commutes.gpkg":      "4a62b544376981d689c1b5fe88865398",
        "ile_de_france_homes.gpkg":         "cda4719021b02726164f8ace43ab20f4",
        "ile_de_france_trips.gpkg":         "d7581bd60a4ad1ad2c473170455f744f",
    }

    generated_csv_hashes = {
        file: hash_file("%s/%s" % (output_path, file)) for file in REFERENCE_CSV_HASHES.keys()
    }

    generated_gpkg_hashes = {
        file: hash_sqlite_db("%s/%s" % (output_path, file)) for file in REFERENCE_GPKG_HASHES.keys()
    }

    print("Generated CSV hashes: ", generated_csv_hashes)
    print("Generated GPKG hashes: ", generated_gpkg_hashes)

    for file in REFERENCE_CSV_HASHES.keys():
        assert REFERENCE_CSV_HASHES[file] == generated_csv_hashes[file]

    for file in REFERENCE_GPKG_HASHES.keys():
        assert REFERENCE_GPKG_HASHES[file] == generated_gpkg_hashes[file]

def test_determinism_matsim(tmpdir):
    data_path = str(tmpdir.mkdir("data"))
    testdata.create(data_path)

    for index in range(2):
        _test_determinism_matsim(index, data_path, tmpdir)

def _test_determinism_matsim(index, data_path, tmpdir):
    print("Running index %d" % index)

    cache_path = str(tmpdir.mkdir("cache_%d" % index))
    output_path = str(tmpdir.mkdir("output_%d" % index))
    config = dict(
        data_path = data_path, output_path = output_path,
        regions = [10, 11], sampling_rate = 1.0, hts = "entd",
        random_seed = 1000, processes = 1,
        secloc_maximum_iterations = 10,
        maven_skip_tests = True,
        matching_attributes = [
            "sex", "any_cars", "age_class", "socioprofessional_class",
            "income_class", "departement_id"
        ]
    )

    stages = [
        dict(descriptor = "matsim.output"),
    ]

    synpp.run(stages, config, working_directory = cache_path)

    REFERENCE_HASHES = {
        #"ile_de_france_population.xml.gz":  "e1407f918cb92166ebf46ad769d8d085",
        #"ile_de_france_network.xml.gz":     "5f10ec295b49d2bb768451c812955794",
        "ile_de_france_households.xml.gz":  "64a0c9fab72aad51bc6adb926a1c9d44",
        #"ile_de_france_facilities.xml.gz":  "5ad41afff9ae5c470082510b943e6778",
        "ile_de_france_config.xml":         "481fac5fb3e7b90810caa38ff460c00a"
    }

    # activities.gpkg, trips.gpkg, meta.json,
    # ile_de_france_transit_schedule.xml.gz, ile_de_france_transit_vehicles.xml.gz

    # TODO: Output of the Java part is not deterministic, probably because of
    # the ordering of persons / facilities. Fix that! Same is true for GPKG. A
    # detailed inspection of meta.json would make sense!

    generated_hashes = {
        file: hash_file("%s/%s" % (output_path, file)) for file in REFERENCE_HASHES.keys()
    }

    print("Generated hashes: ", generated_hashes)

    for file in REFERENCE_HASHES.keys():
        assert REFERENCE_HASHES[file] == generated_hashes[file]
