# Changelog

**Under development**

- Fix: Handle commas in coordinates in BPE
- Fix: Make types consistent for mode recognition in ENTD
- Fix: Properly treat non-movers in EDGT 44
- Fix: Avoid duplicate persons in same households
- Add option to export detailed link geometries
- Fix: Arbitrary order of week days in merged GTFS
- Use BPE 2021 instead of BPE 2019
- Update configuration files for Lyon, Nantes, Corsica
- Add a basic sample based vehicle fleet generation tailored for use with the `emissions` matsim contrib
- Fixing socioprofessional category for Nantes and Lyon (Cerema)
- Fix documentation and processing for Nantes GTFS
- Add law status of the SIRENE enterprises for down-stream freight models (this requires both SIREN and SIRET data as input!)
- Update handling of invalid values on the nubmer of employees in SIRENE
- Add alternative source for EDGT Lyon (and set it as default/recommended source)
- Add euclidean distance to Nantes/Lyon GTFS output
- Fix GTFS schedules without transfer times
- Added stage to write out the full merged GTFS feed: `data.gtfs.output`
- Bugfix: Sometimes bug in converting GTFS coordinates (esp. Lyon / Nantes)
- Fixing output stages
- Add output stages for SIRENE and the selected HTS
- Add output prefix to non-MATSim output files as well
- Add code and documentation for Nantes use case
- Bugfix: Generate `meta.json` when code was not cloned but downloaded directly
- Use `eqasim-java:1.3.1`
- Make choice of branch and version of pt2matsim more flexible
- Improve handling of Osmosis on Windows
- Add stages to process EDGT for Lyon

**1.2.0**

- Update code and data to BPE 2019 (verison for 2018 is not available anymore)
- Add additional spatial standard output: `homes.gpkg` and `commutes.gpkg`
- Updated documentation for BD-TOPO
- By default, load SIRENE directly from `zip` file instead of `csv`
- Bugfix: Make sure df_trips are sorted properly in `synthesis.population.trips`
- Bugfix: Do not execute "urban" attribute imputation twice
- Bugfix: Do not consider *inactive* enterprises from SIRENE
- Update analysis scripts
- Remove CRS warnings
- Bugfix: Handle case if very last activity chain in population ends with tail
- Speed up and improve testing
- Improve analysis output for ENTD
- Update to `eqasim-java:1.2.0` to support tails and "free" activity chains
- Allow for activity chains that do not start and end at home
- Improve handling of education attribute in ENTD

**1.1.0**

- Update to `synpp:1.3.1`
- Use addresses for home locations (from BD-TOPO)
- Use enterprise addresses for work locations (from SIRENE + BD-TOPO)
- Add SIRENE and BD-TOPO data sets
- Update to `eqasim-java:1.1.0` and MATSim 12
- Preparation to use Corisca scenario (see config_corsica.yml) as unit test input in `eqasim-java`
- Several auto-fixes for malformatted GTFS schedules (mainly Corsica)
- Make jar output optional and use proper prefix
- Bugfix: Fixing bug where stop times where discarded in GTFS cutting
- Add documentation for Lyon and Toulouse
- Define stage to output HTS reference data
- Make prefix of MATSim output files configurable
- Cut GTFS schedules to the scenario area automatically
- Make possible to merge multiple GTFS files automatically
- Automatically convert, filter and merge OSM data before using it in pt2matsim. This requires that `osmosis` is available in the run environment.
- Provide calibrated Île-de-France/Paris eqasim simulation for 5% sample
- Make use of `isUrban` attribute from eqasim `1.0.6`
- Update to eqasim `1.0.6`
- Make GTFS date configurable
- Use synpp 1.2.2 to fix Windows directory regeneration issue
- Make pipeline configurable for other departments and regions, add documentation
- BC: Make use of INSEE zone summary data (`codes_2017`)
- Add configuration parameters to filter for departments and regions
- Fixed destinations that have coordinates outside of their municipality
- Make error message for runtime dependencies more verbose
- Switch default instructions to Anaconda

**1.0.0**

- Fixed dependency issue for ENTD scenario
- Initial public version of the pipeline
