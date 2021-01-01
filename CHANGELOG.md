# Changelog

**Under development**

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
