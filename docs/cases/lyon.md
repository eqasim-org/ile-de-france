# Lyon

The pipeline makes it easy to create synthetic populations and simulations
for other regions than Île-de-France. In any case, we recommend to first
follow instructions to set up a [synthetic population for Île-de-France](../population.md)
and (if desired) the [respective simulation](../simulation.md). The following
describes the steps and additional data sets necessary to create a population and
simulation for **Lyon** and surroundings.

## Additional data

### A) Regional census data

Lyon is not included in the census data set that is uesd for Île-de-France
(*Zone A*). Instead, *Zone E* needs to be obtained from the [same source](https://www.insee.fr/fr/statistiques/3625223). Download the *dbase* version of *Zone E* and put the
respective file (*FD_INDCVIZE_2015.dbf*) into the `data/rp_2015` folder.

### B) Address database (BD-TOPO)

You need to download the region-specific address database. Go to [IGN Open data database](https://geoservices.ign.fr/documentation/diffusion/telechargement-donnees-libres.html#bd-topo), scroll down until you see *BD TOPO® Décembre 2020 Tous Thèmes par région édition Décembre 2020 format shapefile*. Click on the download link under
*Région Auvergne-Rhône-Alpes - R 84*. Open the downloaded archive and copy the files `ADRESSE.*` from the folder `ADDRESSES` in *shape file* format into `data/bdtopo` (overriding the data for Île-de-France if you had set up that scenario before).

### C) OpenStreetMap data

Only if you plan to run a simulation (and not just generate a synthetic population),
you need to obtain additional data from OpenStreetMap.
Geofabrik provides a cut-out for the former [Rhône-Alpes](https://download.geofabrik.de/europe/france/rhone-alpes.html) region. Download the region file in *.osm.pbf* format and put the file into the
folder `data/osm`.

### D) GTFS data

Again, only if you want to run simulations, the digital transit schedule is required.
Unfortunately, there is no consolidated GTFS schedule avaiable for the region of interest. Hence,
it is necessary to collect all relevant GTFS schedules one by one. Here, we
provide a selection of links, which is not necessarily exhaustive (for instance,
it would be possible to add schedules for Saint Etienne or Grenoble)

- [TCL (Lyon)](https://transport.data.gouv.fr/datasets/horaires-theoriques-du-reseau-transports-en-commun-lyonnais-1/)
- [SNCF TER](https://ressources.data.sncf.com/explore/dataset/sncf-ter-gtfs/information/)
- [SNCF Intercités](https://ressources.data.sncf.com/explore/dataset/sncf-intercites-gtfs/information/)
- [SNCF TGV](https://ressources.data.sncf.com/explore/dataset/horaires-des-train-voyages-tgvinouiouigo/information/)

Download all the *zip*'d GTFS schedules and put them into the folder `data/gtfs`.

### E) *Optional*: Regional Household Travel Survey 2015

For Lyon, a regional household travel survey (EDGT Lyon 2015) is available on request
from the authorities. If you have the data available, you can use it in the pipeline.
To do so, put the relevant files into `data/edgt_lyon_2015`. The following files
should be present:

- `data/edgt_lyon_2015/EDGT-AML-2015_Total_Dessin&Dictionnaire.xls`
- `data/edgt_lyon_2015/EDGT_AML2015_ZF_GT.DAT`
- `data/edgt_lyon_2015/EDGT_AML2015_ZF_GT.ID`
- `data/edgt_lyon_2015/EDGT_AML2015_ZF_GT.IND`
- `data/edgt_lyon_2015/EDGT_AML2015_ZF_GT.MAP`
- `data/edgt_lyon_2015/EDGT_AML2015_ZF_GT.TAB`
- `EDGT_AML_DEPLA_DIST_2015-10-27.txt`
- `EDGT_AML_MENAGE_FAF_TEL_2015-08-03.txt`
- `EDGT_AML_PERSO_DIST_DT_2015-10-27.txt`
- `EDGT_AML_TRAJET_DIST_2015-10-27.txt`

### Overview

Afterwards, you should have the following additional files in your directory structure:

- `data/rp_2015/FD_INDCVIZE_2015.dbf`
- Plus the files from the EDGT if you want / can use them in `data/edgt_lyon_2015`

*Only for simulation:*

- `osm/rhone-alpes-latest.osm.pbf`
- `gtfs/GTFS_TCL.ZIP`
- `gtfs/export_gtfs_voyages.zip`
- `gtfs/export-intercites-gtfs-last.zip`
- `gtfs/export-ter-gtfs-last.zip`

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
  regions: []
  departments: ["01", 38, 42, 69, 69M] # 26 "07"
  # ...
```

This will make the pipeline filter all data sets for the departments noted
in the list above, which is a set of the closest departments around Lyon.
If you want to generate the whole (ancient) Rhône-Alpes region, add the commented out
department identifiers to the list.

In case you want to *optionally* use the regional HTS (otherwise the national ENTD)
is used, choose the updated HTS in the config:

```yaml
config:
  # ...
  hts: edgt_lyon
  # ...
```

You can now enter your Anaconda environment and call the pipeline with the
`synthesis.output` stage activated. This will generate a synthetic population
for Lyon and surroundings.

## Running the simulation

To prepare the pipeline for a simulation of Lyon, the paths to the OSM data sets and to the GTFS schedule must be adjusted explicitly:

```yaml
config:
  # ...
  gtfs_path: gtfs/GTFS_TCL.ZIP;gtfs/export_gtfs_voyages.zip;gtfs/export-intercites-gtfs-last.zip;gtfs/export-ter-gtfs-last.zip
  osm_path: osm/rhone-alpes-latest.osm.pbf
  # ...
```

Note that the pipeline will automatically cut GTFS and OpenStreetMap data
to the relevant area (defined by the filter above) if you run the simulation.

To test the simulation and generate the relevant MATSim files, run the pipeline
with the `matsim.output` stage enabled.
