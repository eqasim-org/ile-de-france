# Generating the Île-de-France population

The following sections describe how to generate a synthetic population for
Île-de-France using the pipeline. First all necessary data must be gathered.
Afterwards, the pipeline can be run to create a synthetic population in *CSV*
and *GPKG* format. These outputs can be used for analysis, or serve as input
to [run a transport simulation in MATSim](simulation.md). Also, this guide
is the basis for creating populations and simulations of other regions and
cities such as [Toulouse](cases/toulouse.md) or [Lyon](cases/lyon.md).

This guide will cover the following steps:

- [Gathering the data](#section-data)
- [Running the pipeline](#section-population)

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

### 2) Origin-destination data (RP-MOBPRO / RP-MOBSCO 2015)

Origin-destination data is also available from INSEE at two locations:

- [Work origin-destination data](https://www.insee.fr/fr/statistiques/3566008)
- [Education origin-destination data](https://www.insee.fr/fr/statistiques/3565982)
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

### 5) Service and facility census (BPE 2019)

The census of services and facilities in France is available from INSEE:

- [Service and facility census](https://www.insee.fr/fr/statistiques/3568638)
- Download the uppermost data set in **CSV** format. It contains all available
services while the lower data sets only contain observations for specific sectors.
- Copy the content of the *zip* file into the folder `data/bpe_2021`.

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

- [IRIS data](https://geoservices.ign.fr/contoursiris)
- Download the **2017** edition.
- In the *zip* file, follow the following path:
  - *CONTOURS-IRIS_2-1__SHP__FRA_2017-01-01*
  - *CONTOURS-IRIS*
  - *1_DONNEES_LIVRAISON_2018-06-00105*
  - *CONTOURS-IRIS_2-1_SHP_LAMB93_FXX-2017*
- Copy the contents of this folder (like *CONTOURS-IRIS.shp*) into the folder `data/iris_2017`.
- ***Attention***: Currently, the data set is not avaialble at IGN. As a fallback, you can download the data [here](https://drive.google.com/file/d/1lv3LkxZMJj_W0pqZ2rOl6oepZ4ogtkbh/view?usp=sharing).

### 8) Zoning registry

We make use of a zoning registry by INSEE that establishes a connection between
the identifiers of IRIS, municipalities, departments and regions:

- [Zoning data](https://www.insee.fr/fr/information/2017499)
- Download the **2017** edition as a *zip* file.
- Open the *zip* and copy the file `reference_IRIS_geo2017.xls` into `data/codes_2017`.

### 9) Enterprise census (SIRENE)

The enterprise census of France is available on data.gouv.fr:

- [Enterprise census](https://www.data.gouv.fr/fr/datasets/base-sirene-des-entreprises-et-de-leurs-etablissements-siren-siret/)
- Scroll down and click on the green download button on the right for the two following data sets:
  - **Sirene : Fichier StockUniteLegale** (followed by a date), the database of enterprises
  - **Sirene : Fichier StockEtablissement** (followed by a date), the database of enterprise facilities
- The files are updated monthly and are rather large. After downloading, you should have two files:
  - `StockEtablissement_utf8.zip`
  - `StockUniteLegale_utf8.zip`
- Move both *zip* files into `data/sirene`.

### 10) Address database (BD-TOPO)

The French address database is available from IGN:

- [Address database](https://geoservices.ign.fr/bdtopo)
- Use a ftp client to download the *Région Île-de-France - R 11* . Most browsers will not be able to download the data.
- Open the downloaded archive and open/unpack it to to access the folder
  - `BDTOPO_3-0_TOUSTHEMES_SHP_LAMB93_R11_2020-12-15`
  - `BDTOPO`
  - `1_DONNEES_LIVRAISON_2021-01-00120`
  - `BDT_3-0_SHP_LAMB93_R11-ED2020-12-15`
  - `ADRESSES`
- Copy the files `ADRESSE.*` from the folder `ADDRESSES` in *shape file* format into `data/bdtopo`.

### Overview

Your folder structure should now have at least the following files:

- `data/rp_2015/FD_INDCVIZA_2015.dbf`
- `data/rp_2015/FD_MOBPRO_2015.dbf`
- `data/rp_2015/FD_MOBSCO_2015.dbf`
- `data/rp_2015/base-ic-evol-struct-pop-2015.xls`
- `data/filosofi_2015/FILO_DISP_COM.xls`
- `data/filosofi_2015/FILO_DISP_REG.xls`
- `data/bpe_2019/bpe19_ensemble_xy.dbf`
- `data/entd_2008/Q_individu.csv`
- `data/entd_2008/Q_tcm_individu.csv`
- `data/entd_2008/Q_menage.csv`
- `data/entd_2008/Q_tcm_menage_0.csv`
- `data/entd_2008/K_deploc.csv`
- `data/entd_2008/Q_ind_lieu_teg.csv`
- `data/iris_2017/CONTOURS-IRIS.cpg`
- `data/iris_2017/CONTOURS-IRIS.dbf`
- `data/iris_2017/CONTOURS-IRIS.prj`
- `data/iris_2017/CONTOURS-IRIS.shp`
- `data/iris_2017/CONTOURS-IRIS.shx`
- `data/codes_2017/reference_IRIS_geo2017.xls`
- `data/sirene/StockEtablissement_utf8.csv`
- `data/bdtopo/ADRESSE.shp`
- `data/bdtopo/ADRESSE.cpg`
- `data/bdtopo/ADRESSE.dbf`
- `data/bdtopo/ADRESSE.prj`
- `data/bdtopo/ADRESSE.shx`

In case you are using the regional household travel survey (EGT), the following
files should also be in place:

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

Now have a look at `config.yml` which is the configuration of the pipeline code.
Have a look at [synpp](https://github.com/eqasim-org/synpp) in case you want to get a more general
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

It will automatically deshptect the `config.yml`, process all the pipeline code
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
