# Cairo

We have adapted the pipeline for Cairo. There are some steps that are external to the pipeline:

- Generating the synthetic populations (persons and attributes) 
- Obtaining the location candidates (by activity type)

These data need to be requested externally, but eventually it might make sense to include them in the pipeline to have a full process from raw data to the outputs. Currently, the main purpose of the adapted pipeline code is to transform the data in our standard formats and perform location assignment. Here we use the secondary location choice functionality that we have available, but also to assign work and education places. Only home locations are fixed in the Cairo version of the pipeline.

The cairo pipeline is contained in the `cairo` branch of the `iel-de-france` repository for now. We can think of creating a separate repository for it once it becomes more stable.

Note that for the simulation part (MATSim) there is the `cairo` branch in the `eqasim-java` repository.

## How to run the pipeline

### Data preparation

First, you need to prepare the data directory, for instance `/data/`. It is separated in three individual folders, `gtfs_cairo` which contains transit data, `osm_cairo` which contains network data, and `data_cairo` which contains the external data.

- Put the two relevant GTFS schedules into `gtfs_cairo`
- Download the Egypt OSM cutout from Geofabrik (`.osm.pbf` format) and put it into `osm_cairo`
- Take the external data and put them into `data_cairo`.

The final directory structure should look as follows:

- `/data/data_cairo/activity-locations.gpkg`
- `/data/data_cairo/population+home-act.csv`
- `/data/data_cairo/activity-locations.gpkg`
- `/data/gtfs_cairo/bus_new-times.zip`
- `/data/gtfs_cairo/metro-new-times.zip`
- `/data/osm_cairo/egypt-latest.osm.pbf`

### Setting up the environment

Please follow the instructions in this repository on how to set up he environment of the Île-de-France population and simulation (see main description of the repository). You need to install:

- Python environment using `conda`/`mamba`
- Java JDK
- `osmosis`

### Creating population data

To run the pipeline, have a look at `config_cairo.yml` and adjust especially the following options indicating the paths used by the pipeline:

- `working_directory` defines where caching information and premiminary results are saved
- `data_path` defines where the input data is located (see above)
- `output_path` defines where pipeline results will be saved

A common set-up is, for instance, to have the following direcotry structure (here, `/data` is a mounted external drive):

- `working_directory: /data/cairo/cache`
- `data_path: /data/cairo/data` (here goes the structure from above)
- `output_path: /data/cairo/output`

The directories must exist for the pipeline to run properly (i.e., create them empty before performing the first run).

You may work with the `sampling_rate` option to create larger samples of the population (by default only 0.1%).

To start the process, enter the `conda` environment and execute in the root directory of this respository:

```bash
python3 -m synpp config_cairo.yml
```

The OSM file is relatively large, you'll need a certain amount of memory for the process. It has been successfully tested with 14GB.

### Creating simulation data

The above step will only create population data in `csv` and `gpkg` format for analysis. To create the simulation data, comment out the line `- matsim.output` in the `stages` section of the configuration file. Then, execute the pipeline again as above. The ouput folder should then contain all necessary files for a MATSim simulation (mostly `.xml.gz`) and the configuration file `cairo_config.xml`.

### Running the simulation

To run a simulation, either make use of the `cairo` branch in the `eqasim-java` repository (if you want to customize the code) or use the `cairo_run.jar` for a standard version. In the `output` directory, execute:

```bash
java -cp cairo_run.jar -Xmx20g org.eqasim.cairo.RunSimulation --config-path cairo_config.xml --config:controler.lastIteration 0 --config:global.numberOfThreads 12 --config:qsim.numberOfThreads 12 --config:qsim.flowCapacityFactor 1e9 --config:qsim.storageCapacityFactor 1e9
```

Note that here we already pass a couple of configuration parameters that makes the simulation use "free flow" travel times to avoid any congestion for our first trials. The simulation should run for *one* iteration in this case, you can update the `lastIteration` command line option.
