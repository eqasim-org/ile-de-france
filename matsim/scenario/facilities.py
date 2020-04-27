import io, gzip

import numpy as np
import pandas as pd

import matsim.writers as writers

def configure(context):
    context.stage("synthesis.destinations")
    context.stage("synthesis.population.spatial.home.locations")

FACILITY_FIELDS = [
    "destination_id", "geometry",
    "offers_work", "offers_education", "offers_shop", "offers_leisure", "offers_other"
]

HOME_FIELDS = [
    "household_id", "geometry"
]

def execute(context):
    output_path = "%s/facilities.xml.gz" % context.path()

    df_destinations = context.stage("synthesis.destinations")
    df_destinations = df_destinations[FACILITY_FIELDS]

    df_homes = context.stage("synthesis.population.spatial.home.locations")
    df_homes = df_homes[HOME_FIELDS]

    with gzip.open(output_path, 'wb+') as writer:
        with io.BufferedWriter(writer, buffer_size = 2 * 1024**3) as writer:
            writer = writers.FacilitiesWriter(writer)
            writer.start_facilities()

            with context.progress(total = len(df_destinations), label = "Writing facilities ...") as progress:
                for item in df_destinations.itertuples(index = False):
                    geometry = item[FACILITY_FIELDS.index("geometry")]

                    writer.start_facility(
                        item[FACILITY_FIELDS.index("destination_id")],
                        geometry.x, geometry.y
                    )

                    for purpose in ("work", "education", "shop", "leisure", "other"):
                        if item[FACILITY_FIELDS.index("offers_%s" % purpose)]:
                            writer.add_activity(purpose)

                    writer.end_facility()
                    progress.update()

            with context.progress(total = len(df_homes), label = "Writing homes ...") as progress:
                for item in df_homes.itertuples(index = False):
                    geometry = item[HOME_FIELDS.index("geometry")]

                    writer.start_facility(
                        "home_%s" % item[HOME_FIELDS.index("household_id")],
                        geometry.x, geometry.y
                    )

                    writer.add_activity("home")
                    writer.end_facility()

                    progress.update()

            writer.end_facilities()

    return "facilities.xml.gz"
