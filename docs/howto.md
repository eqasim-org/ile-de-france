# How to create a scenario

The following sections describe three steps of using the pipeline. To generate
the synthetic population, first all necessary data must be gathered. Afterwards,
the pipeline can be run to create a synthetic population in *CSV* and *GPKG*
format. Optionally, the pipeline can then prepare a [MATSim](https://matsim.org/)
simulation and run it in a third step:

- [Gathering the data](#section-data)
- [Running the pipeline](#section-data)
- *(Optional)* [Running the simulation](#section-simulation)

## <a name="section-data"></a>Gathering the data

To create the scenario, a couple of data sources must be collected. It is best
to start with an empty folder, e.g. `/data`. All data sets need to be named
in a specific way and put into specific sub-directories. The following paragraphs
describe this process.

### 1) Census data (RP 2015)

Census data containing the socio-demographic information of people living in
France is available at the website of INSEE:

- [Census data](https://www.insee.fr/fr/statistiques/3625223)
- Download the data for **Zone A** in **dbase** format by clicking the link under *Individus localisés au canton-ou-ville - Zone A*.
- Copy the contents of the *zip* file into the folder `data/rp_2015`

### 2) Origin-destiation data (RP-MOBPRO / RP-MOBSCO 2015)

Origin-destination data is also available from INSEE at two locations:

- [Work origin-destiation data](https://www.insee.fr/fr/statistiques/3566008)
- [Education origin-destiation data](https://www.insee.fr/fr/statistiques/3565982)
- Download the data from the links, both in **dbase** format.
- Copy the contents of both *zip* files into the folder `data/rp_2015`.

### 3) Population totals 2015

We also make use of more aggregated population totals:

- [Population data](https://www.insee.fr/fr/statistiques/3627376)
- Download the data for *France hors Mayotte*.
- Copy the contents of the *zip* file into the folder `data/rp_2015`.

### 4) Income tax data (Filosofi 2015)

The tax data set is available from INSEE:

- [Income tax data](https://insee.fr/fr/statistiques/3560118)
- Download the munipality data (first link): *Base niveau communes en 2015*
- Copy the content of the *zip* file into the folder `data/filosofi_2015`
- Download the administrative level data (second linke): *Base niveau administratif en 2015*
- Unpack the *zip* file, it contains more *zip* files.
- Copy the content of *indic-struct-distrib-revenu-2015-REG.zip* into `data/filosofi_2015`

### 5) Service and facility census (BPE 2018)

The census of services and facilities in France is available from INSEE:

- [Service and facility census](https://www.insee.fr/fr/statistiques/3568638)
- Download the uppermost data set in **dbase** format. It contains all available
services while the lower data sets only contain observations for specific sectors.
- Copy the content of the *zip* file into the folder `data/bpe_2018`.

### 6a) National household travel survey (ENTD 2008)

The national household travel survey is available from the Ministry of Ecology:

- [National household travel survey](https://www.statistiques.developpement-durable.gouv.fr/enquete-nationale-transports-et-deplacements-entd-2008)
- Scroll all the way down the website to the **Table des donnés** (a clickable
pop-down menu).
- You can either download all the available *csv* files in the list, but only
a few are actually relevant for the pipeline. Those are:
  - Données socio-démographiques des ménages (Q_tcm_menage_0.csv)
  - Données socio-démographiques des individus (Q_tcm_individu.csv)
  - Logement, stationnement, véhicules à disposition des ménages (Q_menage.csv)
  - Données trajets domicile-travail, domicile-étude, accidents (Q_individu.csv)
  - Données mobilité contrainte, trajets vers lieu de travail (Q_ind_lieu_teg.csv)
  - Données mobilité déplacements locaux (K_deploc.csv)
- Put the downloaded *csv* files int othe folder `data/entd_2008`.

### 6b) *(Optional)* Regional household travel survey (EGT)

Usually, you do not have access to the regional household travel
survey, which is not available publicly. In case you have access (but we cannot
guarantee that you have exactly the correct format), you should make sure that
the following files are accessible in the folder `data/egt_2010`:
`Menages_semaine.csv`, `Personnes_semaine.csv`, `Deplacements_semaine.csv`.

### 7) IRIS zoning system

The IRIS zoning system is available from IGN:

- [IRIS data](https://geoservices.ign.fr/documentation/diffusion/telechargement-donnees-libres.html#contoursiris)
- Download the **2017** edition. Don't worry about the 2018 in the file name, the naming is a bit confusing!)
- In the *zip* file, follow the following path:
  - *CONTOURS-IRIS_2-1__SHP__FRA_2018-06-08*
  - *CONTOURS-IRIS*
  - *1_DONNEES_LIVRAISON_2018-06-00105*
  - *CONTOURS-IRIS_2-1_SHP_LAMB93_FXX-2017*
- Copy the contents of this folder (like *CONTOURS-IRIS.shp*) into the folder `data/iris_2017`.

### 8) Zoning registry

We make use of a zoning registry by INSEE that establishes a connection between
the identifiers of IRIS, municipalities, departments and regions:

- [Zoning data](https://www.insee.fr/fr/information/2017499)
- Download the **2017** edition as a *zip* file.
- Open the *zip* and copy the file `reference_IRIS_geo2017.xls` into `data/codes_2017`.

### 9) *(Optional)* Road network (OpenStreetMap)

Only in case you want to run a full simulation of the scenario (rather than
creating the synthetic population in itself), you need to download OpenStreetMap
data. A cut-out for Île-de-France is available from Geofabrik:

- [Île-de-France OSM](https://download.geofabrik.de/europe/france/ile-de-france.html)
- Download *ile-de-france-latest.osm.bz2* under *Other Formats and Auxiliary Files*.
- Put the *bz2* file (do not unpack!) into the folder `data/osm`.

Unfortunately, the converter ([pt2matsim](https://github.com/matsim-org/pt2matsim))
used in the current version of the pipeline does
not understand the *bz2* format yet (but it will in the near future when MATSim 12.0 is
considered). For now, the file must be converted manually from *bz2* to *gzip*. To
do so, the *gzip* and *bzip2* command line tools must be available. Then, the following
commands comvert the file:

- `bunzip2 ile-de-france-latest.osm.bz2`
- `gzip ile-de-france-latest.osm`

At the end, the `ile-de-france-latest.osm.gz` should be located in the folder.

### 10) *(Optional)* Public transit schedule (GTFS)

Again, only if you want to run a full simulation, you need to download the
public transit schedule. It is available from Île-de-France mobilités:

- [Île-de-France GTFS](https://data.iledefrance-mobilites.fr/explore/dataset/offre-horaires-tc-gtfs-idf/information/)
- Go to *Export*, then download the *csv* file. Open the file, for instance in Excel,
and obtain the URL for *IDFM_gtfs*. Download the *zip* file at this address.
- Copy the contents of the *zip* file into the folder `data/gtfs`.

Note that this schedule is updated regularly and only valid for the next three
weeks. It is therefore a bit tricky to work with it, because the schedule varies
strongly with external factors such as the collective strike during fall 2019
or the Covid-19 outbreak which is currently going on at the time of writing
this documentation. Historical data sets are available from [data.gouv.fr](https://transport.data.gouv.fr/datasets/horaires-prevus-sur-les-lignes-de-transport-en-commun-dile-de-france-gtfs/) but
we did not assess yet how long they are kept and if it is the same data set as
the one from Île-de-France mobilités. Currently, the pipeline will examine the
schedule provided and take the day as a reference on which *most* services are
active. In a future version, we will require that the user explicitly defines
this date.

**Note:** In the current IDFm GTFS data (27 Apr 2020), there is a formatting error
in `routes.txt`, which can be easily fixed. Replace the line

```
014014090:TBUS3,339,"T\\\\\\\\\","T\\\\\\\\\\\\\\\'Bus 3","",3,,0EACE3,ffffff
```

by

```
014014090:TBUS3,339,"T'Bus 3","T'Bus 3","",3,,0EACE3,ffffff
```

### Overview

Your folder structure should now have at least the following files:

- `data/rp_2015/FD_INDCVIZA_2015.dbf`
- `data/rp_2015/FD_MOBPRO_2015.dbf`
- `data/rp_2015/FD_MOBSCO_2015.dbf`
- `data/rp_2015/base-ic-evol-struct-pop-2015.xls`
- `data/filosofi_2015/FILO_DISP_COM.xls`
- `data/filosofi_2015/FILO_DISP_REG.xls`
- `data/bpe_2018/bpe18_ensemble_xy.dbf`
- `data/entd_2008/Q_individu.csv`
- `data/entd_2008/Q_tcm_individu.csv`
- `data/entd_2008/Q_menage.csv`
- `data/entd_2008/Q_tcm_menage.csv`
- `data/entd_2008/K_deploc.csv`
- `data/entd_2008/Q_ind_lieu_teg.csv`
- `data/iris_2017/CONTOURS-IRIS.cpg`
- `data/iris_2017/CONTOURS-IRIS.dbf`
- `data/iris_2017/CONTOURS-IRIS.prj`
- `data/iris_2017/CONTOURS-IRIS.shp`
- `data/iris_2017/CONTOURS-IRIS.shx`
- `data/codes_2017/reference_IRIS_geo2017.xls`

If you want to run the simulation, there should be also the following files:

- `data/osm/ile-de-france-latest.osm.gz`
- `data/gtfs/agency.txt`
- `data/gtfs/calendar.txt`
- `data/gtfs/calendar_dates.txt`
- `data/gtfs/routes.txt`
- `data/gtfs/stop_extensions.txt`
- `data/gtfs/stops.txt`
- `data/gtfs/stop_times.txt`
- `data/gtfs/transfers.txt`
- `data/gtfs/trips.txt`

In case you are using the regional household travel survey (EGT), the following
files should be also in place:

- `data/egt_2010/Menages_semaine.csv`
- `data/egt_2010/Personnes_semaine.csv`
- `data/egt_2010/Deplacements_semaine.csv`

## <a name="section-population">Running the pipeline

The pipeline code is available in [this repository](https://github.com/eqasim-org/ile-de-france).
To use the code, you have to clone the repository with `git`:

```bash
git clone https://github.com/eqasim-org/ile-de-france
```

which will create the `ile-de-france` folder containing the pipeline code. To
set up all dependencies, especially the [synpp](https://github.com/eqasim-org/synpp) package,
which is the code of the pipeline code, we recommend setting up a Python
environment using [Anaconda](https://www.anaconda.com/):

```bash
cd ile-de-france
conda env create -f environment.yml
```

This will create a new Anaconda environment with the name `ile-de-france`. (In
case you don't want to use Anaconda, we also provide a `requirements.txt` to
install all dependencies in a `virtualenv` using `pip install -r requirements.txt`).

To activate the environment, run:

```bash
conda activate ile-de-france
```

Now have a look at `config.yml` which is the configuration of the pipeline.
Check out [synpp](https://github.com/eqasim-org/synpp) to get a more general
understanding of what it does. For the moment, it is important to adjust
two configuration values inside of `config.yml`:

- `working_directory`: This should be an *existing* (ideally empty) folder where
the pipeline will put temporary and cached files during runtime.
- `data_path`: This should be the path to the folder where you were collecting
and arranging all the raw data sets as described above.
- `output_path`: This should be the path to the folder where the output data
of the pipeline should be stored. It must exist and should ideally be empty
for now.

To set up the working/output directory, create, for instance, a `cache` and a
`output` directory. These are already configured in `config.yml`:

```bash
mkdir cache
mkdir output
```

Everything is set now to run the pipeline. The way `config.yml` is configured
it will create the relevant output files in the `output` folder.

To run the pipeline, call the [synpp](https://github.com/eqasim-org/synpp) runner:

```bash
python3 -m synpp
```

It will automatically detect the `config.yml`, process all the pipeline code
and eventually create the synthetic population. You should see a couple of
stages running one after another. Most notably, first, the pipeline will read all
the raw data sets to filter them and put them into the correct internal formats.

After running, you should be able to see a couple of files in the `output`
folder:

- `meta.json` contains some meta data, e.g. with which random seed or sampling
rate the population was created and when.
- `persons.csv` and `households.csv` contain all persons and households in the
population with their respective sociodemographic attributes.
- `activities.csv` and `trips.csv` contain all activities and trips in the
daily mobility patterns of these people including attributes on the purposes
of activities or transport modes for the trips.
- `activities.gpkg` and `trips.gpkg` represent the same trips and
activities, but in the spatial *GPKG* format. Activities contain point
geometries to indicate where they happen and the trips file contains line
geometries to indicate origin and destination of each trip.

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
- **git** is used to clone the repositories containing the simulation code. In
case you clone the pipeline repository previously, you should be all set.

Then, open again `config.yml` and uncomment the `matsim.output` stage in the
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
- `ile_de_france-1.0.5.jar` containing a fully packaged version of the simulation code including MATSim and all other dependencies

If you want to run the simulation again (in the pipeline it is only run for
two iterations to test that everything works), you can now call the following:

```bash
java -Xmx14G -cp ile_de_france-1.0.5.jar org.eqasim.ile_de_france.RunSimulation --config-path ile_de_france_config.xml
```

This will create a `simulation_output` folder (as defined in the `ile_de_france_config.xml`)
where all simulation is written.
