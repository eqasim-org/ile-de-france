import data.gtfs.utils as gtfs
import os

"""
This file reads GTFS schedules, cuts them to the scenario area (defined by the
selected regions and departments) and merges them together.
"""

def configure(context):
    context.config("data_path")
    context.config("gtfs_path", "gtfs/IDFM_gtfs.zip")

    context.stage("data.spatial.municipalities")

def execute(context):
    input_files = context.config("gtfs_path").split(";")

    # Prepare bounding area
    df_area = context.stage("data.spatial.municipalities")

    # Load and cut feeds
    feeds = []
    for path in input_files:
        feed = gtfs.read_feed("%s/%s" % (context.config("data_path"), path))
        feed = gtfs.cut_feed(feed, df_area)

        # This was fixed in pt2matsim, so we can remove one a new release (> 20.7) is available.
        feed = gtfs.despace_stop_ids(feed) # Necessary as MATSim does not like stops/links with spaces

        feeds.append(feed)

    # Merge feeds
    merged_feed = gtfs.merge_feeds(feeds) if len(feeds) > 1 else feeds[0]

    # Fix for pt2matsim (will be fixed after PR #173)
    # Order of week days must be fixed
    days = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
    columns = list(merged_feed["calendar"].columns)
    for day in days: columns.remove(day)
    columns += ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
    merged_feed["calendar"] = merged_feed["calendar"][columns]

    # Write feed (not as a ZIP, but as files, for pt2matsim)
    gtfs.write_feed(merged_feed, "%s/output" % context.path())

    return "gtfs"

def validate(context):
    input_files = context.config("gtfs_path").split(";")
    total_size = 0

    for path in input_files:
        if not os.path.exists("%s/%s" % (context.config("data_path"), path)):
            raise RuntimeError("GTFS data is not available: %s" % path)
        else:
            total_size += os.path.getsize("%s/%s" % (context.config("data_path"), path))

    return total_size
