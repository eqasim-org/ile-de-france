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
- Download *ile-de-france-latest.osm.pbf* and put it into the folder `data/osm`.

### II) Public transit schedule (GTFS)

A digital public transport schedule for Île-de-France is available from Île-de-France mobilités:

- [Île-de-France GTFS](https://data.iledefrance-mobilites.fr/explore/dataset/offre-horaires-tc-gtfs-idf/information/)
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
simulation code provided at https://github.com/eqasim-org/eqasim-java. The generate
`ile-de-france-*.jar` from this pipeline is a automatically compiled version of
this code.
