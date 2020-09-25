# Changelog

**1.0.0-dev**

- Use addresses for home locations (from BD-TOPO)
- Use enterprise addresses for work locations (from SIRENE + BD-TOPO)
- Add SIRENE and BD-TOPO data sets
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
