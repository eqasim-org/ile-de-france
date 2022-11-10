# Running the Île-de-France MATSim simulation

In order to run a simulation of Île-de-France in MATSIM, you first need
to obtain or [generate a synthetic population](population.md). Afterwards, the
pipeline provides additional stages to create and run a full MATSim scenario
including a digital road and public transport network.

This guide covers the following steps:

- [Gathering additional data](#section-data)
- [Running the simulation](#section-simulation)

## <a name="section-data"></a>Gathering additional data

In this section we refere to the same data directory structure as described when
gathering the data for the [synthetic population](population.md).

### I) Road network (OpenStreetMap)

The road network in the pipeline is based on OpenStreetMap data.
A cut-out for Île-de-France is available from Geofabrik:

- [Île-de-France OSM](https://download.geofabrik.de/europe/france/ile-de-france.html)
- We recommend to use the fixed snapshot from 01/01/2022: [ile-de-france-220101.osm.pbf](https://download.geofabrik.de/europe/france/ile-de-france-220101.osm.pbf)
- Download *ile-de-france-220101.osm.pbf* and put it into the folder `data/osm`.

### II) Public transit schedule (GTFS)

A digital public transport schedule for Île-de-France is available from Île-de-France mobilités:

- [Île-de-France GTFS](https://data.iledefrance-mobilites.fr/explore/dataset/offre-horaires-tc-gtfs-idfm/information/)
- Go to *Export*, then download the *csv* file. Open the file, for instance in Excel,
and obtain the URL for *IDFM_gtfs*. Download the *zip* file at this address.
- Copy the `IDFM_gtfs.zip` into the folder `data/gtfs`.

Note that this schedule is updated regularly and only valid for the next three
weeks. It is therefore a bit tricky to work with it, because the schedule varies
strongly with external factors such as the collective strike during fall 2019
or the Covid-19 outbreak which is currently going on at the time of writing
this documentation. Historical data sets are available from [data.gouv.fr](https://transport.data.gouv.fr/datasets/horaires-prevus-sur-les-lignes-de-transport-en-commun-dile-de-france-gtfs/) but
we did not assess yet how long they are kept and if it is the same data set as
the one from Île-de-France mobilités.

### Overview

In your directory structure, there should now be the following additional files:

- `data/osm/ile-de-france-latest.osm.pbf`
- `data/gtfs/IDFM_gtfs.zip`

## <a name="section-simulation">Running the simulation

The pipeline can be used to generate a full runnable [MATSim](https://matsim.org/)
scenario and run it for a couple of iterations to test it. For that, you need
to make sure that the following tools are installed on your system (you can just
try to run the pipeline, it will complain if this is not the case):

- **Java** needs to be installed, with a minimum version of Java 8. In case
you are not sure, you can download the open [AdoptJDK](https://adoptopenjdk.net/).
- **Maven** needs to be installed to build the necessary Java packages for setting
up the scenario (such as pt2matsim) and running the simulation. Maven can be
downloaded [here](https://maven.apache.org/) if it does not already exist on
your system.
- **Osmosis** needs to be accessible from the command line to convert and filter
to convert, filter and merge OSM data sets. Alternatively, you can set the path
to the binary using the `osmosis_binary` option in the confiuration file. Osmosis
can be downloaded [here](https://wiki.openstreetmap.org/wiki/Osmosis).
- **git** is used to clone the repositories containing the simulation code. In
case you clone the pipeline repository previously, you should be all set.

Then, open your `config.yml` and uncomment the `matsim.output` stage in the
`run` section. If you call `python3 -m synpp` again, the pipeline will know
already which stages have been running before, so it will only run additional
stages that are needed to set up and test the simulation.

After running, you should find the MATSim scenario files in the `output`
folder:

- `ile_de_france_population.xml.gz` containing the agents and their daily plans.
- `ile_de_france_facilities.xml.gz` containing all businesses, services, etc.
- `ile_de_france_network.xml.gz` containing the road and transit network
- `ile_de_france_households.xml.gz` containing additional household information
- `ile_de_france_transit_schedule.xml.gz` and `ile_de_france_transit_vehicles.xml.gz` containing public transport data
- `ile_de_france_config.xml` containing the MATSim configuration values
- `ile_de_france-1.0.6.jar` containing a fully packaged version of the simulation code including MATSim and all other dependencies

If you want to run the simulation again (in the pipeline it is only run for
two iterations to test that everything works), you can now call the following:

```bash
java -Xmx14G -cp ile_de_france-1.0.6.jar org.eqasim.ile_de_france.RunSimulation --config-path ile_de_france_config.xml
```

This will create a `simulation_output` folder (as defined in the `ile_de_france_config.xml`)
where all simulation is written.

As of version `1.0.6` of the Île-de-France pipeline, simulations of a 5% population sample use calibrated values for the mode choice model. This means after running for 60 or more iterations, the correct mode shares and network speeds are achieved, compared to the EGT reference data.

For more flexibility and advanced simulations, have a look at the MATSim
simulation code provided at https://github.com/eqasim-org/eqasim-java. The generated
`ile-de-france-*.jar` from this pipeline is an automatically compiled version of
this code.

## <a name="section-data"></a>Optionnaly export detailed link geometries

When creating the matsim network from the OSM data, the `pt2matsim` project simplifies link geometries.
You can export a `detailed_network.csv` file containing the detailed geometries of every network link by the following in the`config.yml` file :

```yaml
# ...

config:
  export_detailed_network: True

# ...
```

## <a name="section-data"></a>Using MATSim's emissions contrib

You can calculate air pollution emissions using matsim by using some additional data.

You must download the crit'air data from this site : https://www.statistiques.developpement-durable.gouv.fr/donnees-sur-le-parc-automobile-francais-au-1er-janvier-2021


You should download both files :

 - Données régionales des voitures particulières - 2011 à 2021 (zip, 1.79 Mo)
 - Données communales des voitures particulières - 2011 à 2021 (zip, 130.33 Mo)

Inside the zip you'll find one data file per year, you can extract the files concerning the year you're intereseted in (let's use `2015` for this exemple). Then unzip and place them in a `data/vehicles_2015/`.

Then, in the `config.yml`, you must enable the vehicle fleet generation :

```yaml
# ...

config:
  generate_vehicles_file: True
  generate_vehicles_method: fleet_sample
  vehicles_data_year: 2015

# ...
```

You should end up, at the end of the `matsim.output` stage, with a vechicles.xml file.

After you run the full simulation, you'll be able to use some classes defined in `eqasim-java` to analyse and compute emissions based on the MATSim outputs.

for exemple :

```bash
java -cp ile_de_france-1.0.6.jar org.eqasim.ile_de_france.emissions.RunComputeEmissionsEvents --config-path config.xml --hbefa-cold-avg ./EFA_ColdStart_Vehcat_2015_Cold_Average.csv --hbefa-hot-avg ./EFA_HOT_Vehcat_2015_Hot_Average.csv --hbefa-cold-detailed ./EFA_ColdStart_Subsegm_2015_Cold_Detailed.csv --hbefa-hot-detailed ./EFA_HOT_Subsegm_2015_Hot_Detailed.csv
```

```bash
java -cp ile_de_france-1.0.6.jar org.eqasim.ile_de_france.emissions.RunExportEmissionsNetwork --config-path config.xml --time-bin-size 3600
```

```bash
java -cp ile_de_france-1.0.6.jar org.eqasim.ile_de_france.emissions.RunComputeEmissionsGrid --config-path config.xml --domain-shp-path idf_2154.shp
```

Please note that you need a copy of the HBEFA database in order to run those.

For further information you can look at [eqasim-java](https://github.com/eqasim-org/eqasim-java) and [matsim-libs/contribs/emissions](https://github.com/matsim-org/matsim-libs/tree/master/contribs/emissions)
