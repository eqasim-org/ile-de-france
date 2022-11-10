# Toulouse / Occitanie

The pipeline makes it easy to create synthetic populations and simulations
for other regions than Île-de-France. In any case, we recommend to first
follow instructions to set up a [synthetic population for Île-de-France](../population.md)
and (if desired) the [respective simulation](../simulation.md). The following
describes the steps and additional data sets necessary to create a population and
simulation for **Toulouse**.

## Additional data

### A) Regional census data

Toulouse is not included in the census data set that is uesd for Île-de-France
(*Zone A*). Instead, *Zone D* needs to be obtained from the [same source](https://www.insee.fr/fr/statistiques/3625223). Download the *dbase* version of *Zone D* and put the
respective file (*FD_INDCVIZD_2015.dbf*) into the `data/rp_2015` folder.

### B) Address database (BD-TOPO)

You need to download the region-specific address database.

- [Address database](https://geoservices.ign.fr/bdtopo)
- Use a ftp client to download the *Région Occitanie - R 76* . Most browsers will not be able to download the data.
- Open the downloaded archive and open/unpack it to to access the folder
  - `BDTOPO_3-0_TOUSTHEMES_SHP_LAMB93_R76_2020-12-15`
  - `BDTOPO`
  - `1_DONNEES_LIVRAISON_2021-01-00120`
  - `BDT_3-0_SHP_LAMB93_R76-ED2020-12-15`
  - `ADRESSES`
- Copy the files `ADRESSE.*` from the folder `ADDRESSES` in *shape file* format into `data/bdtopo`.

### C) OpenStreetMap data

Only if you plan to run a simulation (and not just generate a synthetic population),
you need to obtain additional data from OpenStreetMap.
Geofabrik does not provide a continuous cut-out for Occitanie. Instead, the
former regions of [Midi-Pyrennées](https://download.geofabrik.de/europe/france/midi-pyrenees.html) and [Languedoc-Roussilon](https://download.geofabrik.de/europe/france/languedoc-roussillon.html) are available: [midi-pyrenees-220101.osm.pbf](https://download.geofabrik.de/europe/france/midi-pyrenees-220101.osm.pbf) and [languedoc-roussillon-220101.osm.pbf](https://download.geofabrik.de/europe/france/languedoc-roussillon-220101.osm.pbf). Download both regions in *.osm.pbf* format and put the files into the
folder `data/osm`.

### D) GTFS data

Again, only if you want to run simulations, the digital transit schedule is required.
Unfortunately, there is no consolidated GTFS schedule avaiable for the Occitanie region. Hence,
it is necessary to collect all relevant GTFS schedules one by one. Here, we
provide a selection of links, which is not necessarily exhaustive:

- [TISSEO (Toulouse)](https://data.toulouse-metropole.fr/explore/dataset/tisseo-gtfs/information/)
- [TAM (Montpellier)](http://data.montpellier3m.fr/dataset/offre-de-transport-tam-en-gtfs)
- [Arc-en-Ciel (Busses Occitanie)](https://www.data.gouv.fr/fr/datasets/offre-de-transport-du-reseau-lio-arc-en-ciel-gtfs/)
- [SNCF TER](https://ressources.data.sncf.com/explore/dataset/sncf-ter-gtfs/information/)
- [SNCF Intercités](https://ressources.data.sncf.com/explore/dataset/sncf-intercites-gtfs/information/)
- [SNCF TGV](https://ressources.data.sncf.com/explore/dataset/horaires-des-train-voyages-tgvinouiouigo/information/)

Download all the *zip*'d GTFS schedules and put them into the folder `data/gtfs`.

### Overview

Afterwards, you should have the following additional files in your directory structure:

- `data/rp_2015/FD_INDCVIZD_2015.dbf`

*Only for simulation:*

- `osm/midi-pyrenees-latest.osm.pbf`
- `osm/languedoc-roussillon-latest.osm.pbf`
- `gtfs/tisseo.zip`
- `gtfs/TAM_MMM_GTFS.zip`
- `gtfs/RESEAU_LR_GTFS_20200706.zip`
- `gtfs/export_gtfs_voyages.zip`
- `gtfs/export-intercites-gtfs-last.zip`
- `gtfs/export-ter-gtfs-last.zip`

Note that the file names may change slightly over time as GTFS schedule are
updated continuously.

## Generating the population

To generate the synthetic population, the `config.yml` needs to be updated. While
the relevant code points to the Île-de-France data sets by default, you can
adjust the paths inidividually. To let the pipeline use the *Zone D* census
data set, add the following to `config.yml` in the `config` section:

```yaml
config:
  # ...
  census_path: rp_2015/FD_INDCVIZD_2015.dbf
  # ...
```

Furthermore, by default the pipeline will filter all other data sets for the
Île-de-France region. To make it use the Occitanie region, adjust the
configuration as follows:

```yaml
config:
  # ...
  regions: []
  departments: ["09", 82, 81, 11, 31, 32] # 12 30 34 46 48 65 66
  # ...
```

This will make the pipeline filter all data sets for the departments noted
in the list above, which is a set of the closest departments around Toulouse.
If you want to generate the whole Occitanie region, add the commented out
department identifiers to the list.

Finally, to not confuse output names, we can define a new prefix for the output files:

```yaml
config:
  # ...
  output_prefix: toulouse_
  # ...
```

You can now enter your Anaconda environment and call the pipeline with the
`synthesis.output` stage activated. This will generate a synthetic population
for Toulouse and surroundings.

## Running the simulation

To prepare the pipeline for a simulation of Toulouse, the paths to the OSM data sets and to the GTFS schedule must be adjusted explicitly:

```yaml
config:
  # ...
  gtfs_path: gtfs/tisseo.zip;gtfs/TAM_MMM_GTFS.zip;gtfs/export_gtfs_voyages.zip;gtfs/export-intercites-gtfs-last.zip;gtfs/export-ter-gtfs-last.zip;gtfs/RESEAU_LR_GTFS_20200706.zip
  osm_path: osm/midi-pyrenees-220101.osm.pbf;osm/languedoc-roussillon-220101.osm.pbf
  # ...
```

Note that the pipeline will automatically cut GTFS and OpenStreetMap data
to the relevant area (defined by the filter above) if you run the simulation.

To test the simulation and generate the relevant MATSim files, run the pipeline
with the `matsim.output` stage enabled.
