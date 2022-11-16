import topojson

def configure(context):
    context.stage("data.spatial.departments")
    context.stage("data.spatial.municipalities")
    context.stage("data.spatial.iris")

def execute(context):
    df_departments = context.stage("data.spatial.departments")
    df_departments["departement_id"] = df_departments["departement_id"].astype(str)
    df_departments = df_departments[["geometry", "departement_id"]]
    df_departments = df_departments.to_crs("EPSG:4326")

    df_municipalities = context.stage("data.spatial.municipalities")
    df_municipalities["municipality_id"] = df_municipalities["commune_id"].astype(str)
    df_municipalities = df_municipalities[["geometry", "municipality_id"]]
    df_municipalities = df_municipalities.to_crs("EPSG:4326")

    df_iris = context.stage("data.spatial.iris")
    df_iris["iris_id"] = df_iris["iris_id"].astype(str)
    df_iris = df_iris[["geometry", "iris_id"]]
    df_iris = df_iris.to_crs("EPSG:4326")

    return {
        "department_count": len(df_departments),
        "departments": topojson.Topology(df_departments, prequantize=False).to_json(),
        "municipality_count": len(df_municipalities),
        "municipalities": topojson.Topology(df_municipalities, prequantize=False).to_json(),
        "iris_count": len(df_iris),
        "iris": topojson.Topology(df_iris, prequantize=False).to_json(),
    }
