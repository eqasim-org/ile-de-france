
def configure(context):
    method = context.config("generate_vehicles_method")

    if method == "fleet_sample":
        context.stage("synthesis.vehicles.fleet_sample.vehicles", alias = "vehicles")
    else:
        raise RuntimeError("Unknown vehicles generation method : %s" % method)

def execute(context):
    return context.stage("vehicles")
