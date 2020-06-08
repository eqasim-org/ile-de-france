import synpp
import os
import hashlib, gzip
from . import testdata

def test_determinism(tmpdir):
    data_path = str(tmpdir.mkdir("data"))
    testdata.create(data_path)

    md5sums = []

    for index in range(2):
        cache_path = str(tmpdir.mkdir("cache_%d" % index))
        output_path = str(tmpdir.mkdir("output_%d" % index))
        config = dict(
            data_path = data_path, output_path = output_path,
            regions = [10, 11], sampling_rate = 1.0, hts = "entd",
            random_seed = 1000, processes = 1
        )

        stages = [
            dict(descriptor = "synthesis.output"),
            dict(descriptor = "matsim.output"),
        ]

        synpp.run(stages, config, working_directory = cache_path)

        files = [
            "%s/activities.csv" % output_path,
            "%s/persons.csv" % output_path,
            "%s/households.csv" % output_path,
            #"%s/activities.gpkg" % output_path,
            #"%s/trips.gpkg" % output_path,
            #"%s/meta.json" % output_path
            "%s/ile_de_france_population.xml.gz" % output_path,
            "%s/ile_de_france_network.xml.gz" % output_path,
            #"%s/ile_de_france_transit_schedule.xml.gz" % output_path,
            #"%s/ile_de_france_transit_vehicles.xml.gz" % output_path,
            "%s/ile_de_france_households.xml.gz" % output_path,
            "%s/ile_de_france_facilities.xml.gz" % output_path,
            "%s/ile_de_france_config.xml" % output_path
        ]

        hash = hashlib.md5()

        for file in files:
            # Gzip saves time stamps, so the gzipped files are NOT the same!
            opener = lambda: open(file, "rb")

            if file.endswith(".gz"):
                opener = lambda: gzip.open(file)

            with opener() as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash.update(chunk)

            f.close()

        md5sums.append(hash.hexdigest())

    for index in range(1, len(md5sums)):
        assert md5sums[0] == md5sums[1]
