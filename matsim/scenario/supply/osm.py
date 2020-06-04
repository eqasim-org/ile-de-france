import os.path

import matsim.runtime.pt2matsim as pt2matsim

def configure(context):
    context.stage("matsim.runtime.java")
    context.stage("matsim.runtime.pt2matsim")

    context.config("data_path")
    context.config("osm_path", "osm/ile-de-france-latest.osm.gz")

def execute(context):
    pt2matsim.run(context, "org.matsim.pt2matsim.run.CreateDefaultOsmConfig", [
        "config_template.xml"
    ])

    with open("%s/config_template.xml" % context.path()) as f_read:
        content = f_read.read()

        content = content.replace(
            '<param name="osmFile" value="null" />',
            '<param name="osmFile" value="%s/%s" />' % (context.config("data_path"), context.config("osm_path"))
        )

        content = content.replace(
            '<param name="outputCoordinateSystem" value="null" />',
            '<param name="outputCoordinateSystem" value="EPSG:2154" />'
        )

        content = content.replace(
            '<param name="outputNetworkFile" value="null" />',
            '<param name="outputNetworkFile" value="network.xml.gz" />'
        )

        content = content.replace(
            '</module>',
            """
                <parameterset type="routableSubnetwork">
                    <param name="allowedTransportModes" value="car" />
                    <param name="subnetworkMode" value="car_passenger" />
                </parameterset>
            </module>
            """
        )

        with open("%s/config.xml" % context.path(), "w+") as f_write:
            f_write.write(content)

    pt2matsim.run(context, "org.matsim.pt2matsim.run.Osm2MultimodalNetwork", [
        "config.xml"
    ])

    assert(os.path.exists("%s/network.xml.gz" % context.path()))
    return "network.xml.gz"

def validate(context):
    if not os.path.exists("%s/%s" % (context.config("data_path"), context.config("osm_path"))):
        raise RuntimeError("OSM data is not available")

    return os.path.getsize("%s/%s" % (context.config("data_path"), context.config("osm_path")))
