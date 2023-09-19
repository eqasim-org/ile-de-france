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

### 1) Census data (RP 2019)

Census data containing the socio-demographic information of people living in
France is available from INSEE:

- [Census data](https://www.insee.fr/fr/statistiques/6544333)
- Download the data set in **csv** format by clicking the link under *Individus localisés au canton-ou-ville*.
- Copy the *zip* file into the folder `data/rp_2019`

### 2) Population totals (RP 2019)

We also make use of more aggregated population totals available from INSEE:

- [Population data](https://www.insee.fr/fr/statistiques/6543200)
- Download the data for *France hors Mayotte* in **xlsx** format.
- Copy the *zip* file into the folder `data/rp_2019`.

### 3) Origin-destination data (RP-MOBPRO / RP-MOBSCO 2019)

Origin-destination data is available from INSEE (at two locations):

- [Work origin-destination data](https://www.insee.fr/fr/statistiques/6456056)
- [Education origin-destination data](https://www.insee.fr/fr/statistiques/6456052)
- Download the data from the links, both in **csv** format.
- Copy both *zip* files into the folder `data/rp_2019`.

### 4) Income tax data (Filosofi 2019)

The tax data set is available from INSEE:

- [Income tax data](https://insee.fr/fr/statistiques/6036907)
- Download the munipality data (first link): *Base niveau communes en 2019* in **xlsx** format
- Copy the *zip* file into the folder `data/filosofi_2019`
- Download the administrative level data (second link): *Base niveau administratif en 2019* in **xlsx** format
- Copy the second *zip* file into `data/filosofi_2019`

### 5) Service and facility census (BPE 2021)

The census of services and facilities in France is available from INSEE:

- [Service and facility census](https://www.insee.fr/fr/statistiques/3568638)
- Download the uppermost data set in **csv** format. It contains all available
services while the lower data sets only contain observations for specific sectors.
- Copy the *zip* file into the folder `data/bpe_2021`.

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
- Put the downloaded *csv* files in to the folder `data/entd_2008`.

### 6b) *(Optional)* Regional household travel survey (EGT)

Usually, you do not have access to the regional household travel
survey, which is not available publicly. In case you have access (but we cannot
guarantee that you have exactly the correct format), you should make sure that
the following files are accessible in the folder `data/egt_2010`:
`Menages_semaine.csv`, `Personnes_semaine.csv`, `Deplacements_semaine.csv`.

### 7) IRIS zoning system (2021)

The IRIS zoning system is available from IGN:

- [IRIS data](https://geoservices.ign.fr/contoursiris)
- Download the **2021** edition.
- Copy the *7z* file into the folder `data/iris_2021`


### 8) Zoning registry (2021)

We make use of a zoning registry by INSEE that establishes a connection between
the identifiers of IRIS, municipalities, departments and regions:

- [Zoning data](https://www.insee.fr/fr/information/2017499)
- Download the **2021** edition as a *zip* file.
- Copy the *zip* file into `data/codes_2021`.

### 9) Enterprise census (SIRENE)

The enterprise census of France is available on data.gouv.fr:

- [Enterprise census](https://www.data.gouv.fr/fr/datasets/base-sirene-des-entreprises-et-de-leurs-etablissements-siren-siret/)
- Scroll down and click on the blue download button on the right for the two following data sets:
  - **Sirene : Fichier StockUniteLegale** (followed by a date), the database of enterprises
  - **Sirene : Fichier StockEtablissement** (followed by a date), the database of enterprise facilities
- The files are updated monthly and are rather large. After downloading, you should have two files:
  - `StockEtablissement_utf8.zip`
  - `StockUniteLegale_utf8.zip`
- Move both *zip* files into `data/sirene`.

The geolocated enterprise census is available on data.gouv.fr:

- [Geolocated enterprise census](https://www.data.gouv.fr/fr/datasets/geolocalisation-des-etablissements-du-repertoire-sirene-pour-les-etudes-statistiques/)
- Scroll down and click on the blue download button on the right for the following data set:
    - **Sirene : Fichier GeolocalisationEtablissement_Sirene_pour_etudes_statistiques** (followed by a date), 
- Put the downloaded *zip* file into `data/sirene`

### 10) Buildings database (BD TOPO)

The French Buildings database is available from IGN:

- [Buildings database](https://geoservices.ign.fr/bdtopo)
- In the sidebar on the right, under *Téléchargement anciennes éditions*, click on *BD TOPO® 2022 GeoPackage Départements* to go to the saved data publications from 2022.
- The data is split by department and they are identified with a number. For the Île-de-France region, download:
  - Paris (75)
  - Seine-et-Marne (77)
  - Yvelines (78)
  - Essonne (91)
  - Hauts-de-Seine (92)
  - Seine-Saint-Denis (93)
  - Val-de-Marne (94)
  - Val-d'Oise (95)
- Copy the eight *7z* files into `data/bdtopo_idf`.

### 11) Adresses database (BAN)

The French adresses database is available on data.gouv.fr :

- [Adresses database](https://adresse.data.gouv.fr/data/ban/adresses/latest/csv/)
- Click on the link *adresses-xx.csv.gz* where xx = departments codes (75, 77, 78, 91, 92, 93, 94, 95) 
- Copy the *gz* files into `data/ban_idf`.


### Overview

Your folder structure should now have at least the following files:

- `data/rp_2019/RP2019_INDCVI_csv.zip`
- `data/rp_2019/RP2019_MOBPRO_csv.zip`
- `data/rp_2019/RP2019_MOBSCO_csv.zip`
- `data/rp_2019/base-ic-evol-struct-pop-2019.zip`
- `data/filosofi_2019/indic-struct-distrib-revenu-2019-COMMUNES.zip`
- `data/filosofi_2019/indic-struct-distrib-revenu-2019-SUPRA.zip`
- `data/bpe_2021/bpe21_ensemble_xy_csv.zip`
- `data/entd_2008/Q_individu.csv`
- `data/entd_2008/Q_tcm_individu.csv`
- `data/entd_2008/Q_menage.csv`
- `data/entd_2008/Q_tcm_menage_0.csv`
- `data/entd_2008/K_deploc.csv`
- `data/entd_2008/Q_ind_lieu_teg.csv`
- `data/iris_2021/CONTOURS-IRIS_2-1__SHP__FRA_2021-01-01.7z`
- `data/codes_2021/reference_IRIS_geo2021.zip`
- `data/sirene/StockEtablissement_utf8.csv`
- `data/sirene/StockUniteLegale_utf8.zip`
- `data/sirene/GeolocalisationEtablissement_Sirene_pour_etudes_statistiques_utf8.zip`
- `data/bdtopo_idf/BDTOPO_3-0_TOUSTHEMES_GPKG_LAMB93_D075_2022-03-15.7z`
- `data/bdtopo_idf/BDTOPO_3-0_TOUSTHEMES_GPKG_LAMB93_D077_2022-03-15.7z`
- `data/bdtopo_idf/BDTOPO_3-0_TOUSTHEMES_GPKG_LAMB93_D078_2022-03-15.7z`
- `data/bdtopo_idf/BDTOPO_3-0_TOUSTHEMES_GPKG_LAMB93_D091_2022-03-15.7z`
- `data/bdtopo_idf/BDTOPO_3-0_TOUSTHEMES_GPKG_LAMB93_D092_2022-03-15.7z`
- `data/bdtopo_idf/BDTOPO_3-0_TOUSTHEMES_GPKG_LAMB93_D093_2022-03-15.7z`
- `data/bdtopo_idf/BDTOPO_3-0_TOUSTHEMES_GPKG_LAMB93_D094_2022-03-15.7z`
- `data/bdtopo_idf/BDTOPO_3-0_TOUSTHEMES_GPKG_LAMB93_D095_2022-03-15.7z`
- `data/ban_idf/adresses-75.csv.gz`
- `data/ban_idf/adresses-77.csv.gz`
- `data/ban_idf/adresses-78.csv.gz`
- `data/ban_idf/adresses-91.csv.gz`
- `data/ban_idf/adresses-92.csv.gz`
- `data/ban_idf/adresses-93.csv.gz`
- `data/ban_idf/adresses-94.csv.gz`

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

This will create a new Anaconda environment with the name `ile-de-france`.

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
of activities.
- `activities.gpkg` and `trips.gpkg` represent the same trips and
activities, but in the spatial *GPKG* format. Activities contain point
geometries to indicate where they happen and the trips file contains line
geometries to indicate origin and destination of each trip.

### Mode choice

The synthetic data generated by the pipeine so far does not include transport modes (car, bike, walk, pt, ...) for the individual trips as assigning them consistently is a more computation-heavy process (including routing the individual trips for the modes). To add modes to the trip table, a light-weight MATSim simulation needs to be performed. For that, please configure the additional data requirements as described in the procedure to run a MATSim simulation:

- [Running a MATSim simulation](https://github.com/eqasim-org/ile-de-france/blob/develop/docs/simulation.md)

After that, you can change the `mode_choice` entry in the pipeline configuration file `config.yml` to `true`:

```yaml
config:
  mode_choice: true
```

Running the pipeline again will add the `mode` colum to the `trips.csv` file and its spatial equivalent.
