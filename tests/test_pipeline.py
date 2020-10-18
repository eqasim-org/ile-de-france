import synpp
import os
import hashlib
from . import testdata

def test_data(tmpdir):
    data_path = str(tmpdir.mkdir("data"))
    testdata.create(data_path)

    cache_path = str(tmpdir.mkdir("cache"))
    config = dict(data_path = data_path, regions = [10, 11])

    stages = [
        dict(descriptor = "data.spatial.iris"),
        dict(descriptor = "data.spatial.codes"),
        dict(descriptor = "data.spatial.population"),
        dict(descriptor = "data.bpe.cleaned"),
        dict(descriptor = "data.income.municipality"),
        dict(descriptor = "data.hts.entd.cleaned"),
        dict(descriptor = "data.hts.egt.cleaned"),
        dict(descriptor = "data.census.cleaned"),
        dict(descriptor = "data.od.cleaned")
    ]

    synpp.run(stages, config, working_directory = cache_path)

def run_population(tmpdir, hts):
    data_path = str(tmpdir.mkdir("data"))
    testdata.create(data_path)

    cache_path = str(tmpdir.mkdir("cache"))
    output_path = str(tmpdir.mkdir("output"))
    config = dict(
        data_path = data_path, output_path = output_path,
        regions = [10, 11], sampling_rate = 1.0, hts = "entd",
        random_seed = 1000, processes = 1,
        secloc_maximum_iterations = 10,
        maven_skip_tests = True
    )

    stages = [
        dict(descriptor = "synthesis.output"),
    ]

    synpp.run(stages, config, working_directory = cache_path)

    assert os.path.isfile("%s/activities.csv" % output_path)
    assert os.path.isfile("%s/persons.csv" % output_path)
    assert os.path.isfile("%s/households.csv" % output_path)
    assert os.path.isfile("%s/activities.gpkg" % output_path)
    assert os.path.isfile("%s/trips.gpkg" % output_path)
    assert os.path.isfile("%s/meta.json" % output_path)

def test_population_with_entd(tmpdir):
    run_population(tmpdir, "entd")

def test_population_with_egt(tmpdir):
    run_population(tmpdir, "egt")
