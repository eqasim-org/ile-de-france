import io, gzip

import numpy as np
import pandas as pd

import matsim.writers as writers

def configure(context):
    context.stage("synthesis.locations.home")
    context.stage("synthesis.locations.work")
    context.stage("synthesis.locations.education")
    context.stage("synthesis.locations.secondary")

    context.stage("synthesis.population.spatial.home.locations")

FIELDS = [
    "location_id", "geometry",
    "offers_work", "offers_education",
]

SECONDARY_FIELDS = FIELDS + [
    "offers_shop", "offers_leisure", "offers_other"
]

def execute(context):
    output_path = "%s/facilities.xml.gz" % context.path()

    with gzip.open(output_path, 'wb+') as writer:
        with io.BufferedWriter(writer, buffer_size = 2 * 1024**3) as writer:
            writer = writers.FacilitiesWriter(writer)
            writer.start_facilities()

            slots = ["home", "work", "education", "secondary"]

            for slot in slots:
                df = context.stage("synthesis.locations.%s" % slot)[FIELDS]

                if slot == "home":
                    df_homes = context.stage("synthesis.population.spatial.home.locations")
                    df = df[df["location_id"].isin(df_homes["location_id"].unique())]

                with context.progress(total = len(df), label = "Writing %s facilities ..." % slot) as progress:
                    for item in df.itertuples(index = False):
                        geometry = item[FIELDS.index("geometry")]

                        writer.start_facility(
                            item[FIELDS.index("location_id")],
                            geometry.x, geometry.y
                        )

                        if slot == "secondary":
                            for purpose in ("shop", "leisure", "other"):
                                if item[SECONDARY_FIELDS.index("offers_%s" % purpose)]:
                                    writer.add_activity(purpose)
                        else:
                            writer.add_activity(slot)

                        writer.add_activity(slot)
                        writer.end_facility()
                        progress.update()

    return "facilities.xml.gz"
