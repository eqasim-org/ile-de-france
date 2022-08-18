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

You need to download the region-specific address database.

- [Address database](https://geoservices.ign.fr/bdtopo)
- Use a ftp client to download the *Région Auvergne-Rhône-Alpes - R 84* . Most browsers will not be able to download the data.
- Open the downloaded archive and open/unpack it to to access the folder
  - `BDTOPO_3-0_TOUSTHEMES_SHP_LAMB93_R84_2020-12-15`
  - `BDTOPO`
  - `1_DONNEES_LIVRAISON_2021-01-00120`
  - `BDT_3-0_SHP_LAMB93_R84-ED2020-12-15`
  - `ADRESSES`
- Copy the files `ADRESSE.*` from the folder `ADDRESSES` in *shape file* format into `data/bdtopo`.

### C) OpenStreetMap data

Only if you plan to run a simulation (and not just generate a synthetic population),
you need to obtain additional data from OpenStreetMap.
Geofabrik provides a cut-out for the former [Rhône-Alpes](https://download.geofabrik.de/europe/france/rhone-alpes.html) region: [rhone-alpes-220101.osm.pbf](https://download.geofabrik.de/europe/france/rhone-alpes-220101.osm.pbf). Download the region file in *.osm.pbf* format and put the file into the
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
- [TAG (Grenoble)](https://transport.data.gouv.fr/datasets/horaires-theoriques-du-reseau-tag/)
- [Ruban (Porte d'Isère)](https://transport.data.gouv.fr/datasets/reseau-ruban-donnees-theoriques/)
- [L'va (Vienne)](https://transport.data.gouv.fr/datasets/reseau-lva/?locale=en)
- [STAS (St. Etienne)](https://transport.data.gouv.fr/datasets/donnees-horaires-theoriques-gtfs-du-reseau-de-transport-de-la-metropole-de-saint-etienne-stas/?locale=fr&slug=donnees-horaires-theoriques-gtfs-du-reseau-de-transport-de-la-metropole-de-saint-etienne-stas)
- [Rhône Express](https://transport.data.gouv.fr/datasets/horaires-theoriques-du-service-rhonexpress-de-la-metropole-de-lyon-et-du-departement-du-rhone/)

Download all the *zip*'d GTFS schedules and put them into the folder `data/gtfs`.

### E) *Optional*: Regional Household Travel Survey 2015

For Lyon, a regional household travel survey (EDGT Lyon 2015) is available on request
from the authorities. If you have the data available, you can use it in the pipeline.
To do so, put the relevant files into `data/edgt_lyon_2015`.

The data can be obtained either directly from the CEREMA or through the ADISP portal (http://www.progedo-adisp.fr/serie_emd.php).

#### E.a) Data from CEREMA

If you get the EDGT directly from the CEREMA, the following files should be present:

- `data/edgt_lyon_2015/EDGT-AML-2015_Total_Dessin&Dictionnaire.xls`
- `data/edgt_lyon_2015/EDGT_AML2015_ZF_GT.DAT`
- `data/edgt_lyon_2015/EDGT_AML2015_ZF_GT.ID`
- `data/edgt_lyon_2015/EDGT_AML2015_ZF_GT.IND`
- `data/edgt_lyon_2015/EDGT_AML2015_ZF_GT.MAP`
- `data/edgt_lyon_2015/EDGT_AML2015_ZF_GT.TAB`
- `data/edgt_lyon_2015/EDGT_AML_DEPLA_DIST_2015-10-27.txt`
- `data/edgt_lyon_2015/EDGT_AML_MENAGE_FAF_TEL_2015-08-03.txt`
- `data/edgt_lyon_2015/EDGT_AML_PERSO_DIST_DT_2015-10-27.txt`
- `data/edgt_lyon_2015/EDGT_AML_TRAJET_DIST_2015-10-27.txt`

#### E.a) Data from the ADISP portal

If you get the EDGT data from the ADISP portal, the following files should be present:

- `data/edgt_lyon_2015/lyon_2015_std_faf_men.csv`
- `data/edgt_lyon_2015/lyon_2015_std_tel_men.csv`
- `data/edgt_lyon_2015/lyon_2015_std_faf_pers.csv`
- `data/edgt_lyon_2015/lyon_2015_std_tel_pers.csv`
- `data/edgt_lyon_2015/lyon_2015_std_faf_traj.csv`
- `data/edgt_lyon_2015/lyon_2015_std_tel_traj.csv`
- `data/edgt_lyon_2015/EDGT_AML2015_ZF_GT.DAT`
- `data/edgt_lyon_2015/EDGT_AML2015_ZF_GT.ID`
- `data/edgt_lyon_2015/EDGT_AML2015_ZF_GT.IND`
- `data/edgt_lyon_2015/EDGT_AML2015_ZF_GT.MAP`
- `data/edgt_lyon_2015/EDGT_AML2015_ZF_GT.TAB`

### Overview

Afterwards, you should have the following additional files in your directory structure:

- `data/rp_2015/FD_INDCVIZE_2015.dbf`
- Plus the files from the EDGT if you want / can use them in `data/edgt_lyon_2015`

*Only for simulation:*

- `osm/rhone-alpes-latest.osm.pbf`
- `gtfs/GTFS_TCL.ZIP`
- `gtfs/CAPI.GTFS.zip`
- `gtfs/GTFS_RX.ZIP`
- `gtfs/SEM-GTFS.zip`
- `gtfs/stas.gtfs.zip`
- `gtfs/VIENNE.GTFS.zip`
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
is used, choose the updated HTS in the config file.

**Important** : when using `edgt_lyon` you **must** set the `edgt_lyon_source` to either `adisp` or `cerema`, else an error will be raised.

```yaml
config:
  # ...
  hts: edgt_lyon
  edgt_lyon_source: adisp  # adisp/cerema
  # ...
```

Finally, to not confuse output names, we can define a new prefix for the output files:

```yaml
config:
  # ...
  output_prefix: lyon_
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
  gtfs_path: gtfs/GTFS_TCL.ZIP;gtfs/export_gtfs_voyages.zip;gtfs/export-intercites-gtfs-last.zip;gtfs/export-ter-gtfs-last.zip;gtfs/CAPI.GTFS.zip;gtfs/GTFS_RX.ZIP;gtfs/SEM-GTFS.zip;gtfs/stas.gtfs.zip;gtfs/VIENNE.GTFS.zip
  osm_path: osm/rhone-alpes-220101.osm.pbf
  # ...
```

Note that the pipeline will automatically cut GTFS and OpenStreetMap data
to the relevant area (defined by the filter above) if you run the simulation.

To test the simulation and generate the relevant MATSim files, run the pipeline
with the `matsim.output` stage enabled.
