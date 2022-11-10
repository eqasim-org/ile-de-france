# Corsica

The pipeline makes it easy to create synthetic populations and simulations
for other regions than Île-de-France. In any case, we recommend to first
follow instructions to set up a [synthetic population for Île-de-France](../population.md)
and (if desired) the [respective simulation](../simulation.md). The following
describes the steps and additional data sets necessary to create a population and
simulation for **Corsica**.

## Additional data

### A) Regional census data

Corsica is not included in the census data set that is used for Île-de-France
(*Zone A*). Instead, *Zone E* needs to be obtained from the [same source](https://www.insee.fr/fr/statistiques/3625223). Download the *dbase* version of *Zone E* and put the
respective file (*FD_INDCVIZE_2015.dbf*) into the `data/rp_2015` folder.

### B) Address database (BD-TOPO)

You need to download the region-specific address database.

- [Address database](https://geoservices.ign.fr/bdtopo)
- Use a ftp client to download the *Région Corse - R 94* . Most browsers will not be able to download the data.
- Open the downloaded archive and open/unpack it to to access the folder
  - `BDTOPO_3-0_TOUSTHEMES_SHP_LAMB93_R94_2020-12-15`
  - `BDTOPO`
  - `1_DONNEES_LIVRAISON_2021-01-00120`
  - `BDT_3-0_SHP_LAMB93_R94-ED2020-12-15`
  - `ADRESSES`
- Copy the files `ADRESSE.*` from the folder `ADDRESSES` in *shape file* format into `data/bdtopo`.

### C) OpenStreetMap data

Only if you plan to run a simulation (and not just generate a synthetic population),
you need to obtain additional data from OpenStreetMap.
Geofabrik provides a cut-out for the [Corsica](https://download.geofabrik.de/europe/france/corse.html) region: [corse-220101.osm.pbf](https://download.geofabrik.de/europe/france/corse-220101.osm.pbf). Download the region file in *.osm.pbf* format and put the file into the
folder `data/osm`.

### D) GTFS data

Again, only if you want to run simulations, the digital transit schedule is required.
Unfortunately, there is no consolidated GTFS schedule avaiable for the region of interest. Hence,
it is necessary to collect all relevant GTFS schedules one by one.

- [Chemins de fer de Corse](https://www.data.corsica/explore/dataset/horaires-cfc-gtfs/export/)
- [Cars Corse du Sud](https://www.data.corsica/explore/dataset/horaires-cars2a-gtfs/export/)
- [Cars Haute Corse](https://www.data.corsica/explore/dataset/horaires-cars2b-gtfs/export/)

Download all the *zip*'d GTFS schedules and put them into the folder `data/gtfs`.

### Overview

Afterwards, you should have the following additional files in your directory structure:

- `data/rp_2015/FD_INDCVIZE_2015.dbf`

*Only for simulation:*

- `osm/corse-220101.osm.pbf`
- `gtfs/GTFS été 2021.zip`
- `gtfs/cars2a-gtfs.zip`
- `gtfs/cars2b-gtfs.zip`

Note that the file names may change slightly over time as GTFS schedule are
updated continuously.

## Generating the population

To generate the synthetic population, the `config.yml` needs to be updated. While
the relevant code points to the Île-de-France data sets by default, you can
adjust the paths inidividually. To let the pipeline use the *Zone E* census
data set, add the following to `config.yml` in the `config` section:

```yaml
config:
  # ...
  census_path: rp_2015/FD_INDCVIZE_2015.dbf
  # ...
```

Furthermore, by default the pipeline will filter all other data sets for the
Île-de-France region. To make it use the selected region, adjust the
configuration as follows:

```yaml
config:
  # ...
  regions: [94]
  # ...
```

This will make the pipeline filter all data sets for the Corsica region.

Finally, to not confuse output names, we can define a new prefix for the output files:

```yaml
config:
  # ...
  output_prefix: corsica_
  # ...
```

For the specific use case of Corsica, it makes sense to reduce the matching threshold between activity chains and persons as only little data for Corsica is available in the ENTD survey. This might be improved in the future by reusing data from other regions or using a more detailed HTS:

```yaml
config:
  # ...
  matching_minimum_observations: 5
  # ...
```

You can now enter your Anaconda environment and call the pipeline with the
`synthesis.output` stage activated. This will generate a synthetic population
for Corsica.

## Running the simulation

To prepare the pipeline for a simulation of Lyon, the paths to the OSM data sets and to the GTFS schedule must be adjusted explicitly:

```yaml
config:
  # ...
  gtfs_path: gtfs/cars2a-gtfs.zip;gtfs/cars2b-gtfs.zip;gtfs/GTFS été 2021.zip
  osm_path: osm/corse-220101.osm.pbf
  # ...
```

To test the simulation and generate the relevant MATSim files, run the pipeline
with the `matsim.output` stage enabled.
