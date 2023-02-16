"""
Provides the municipality zoning system.
"""

def configure(context):
    context.stage("data.spatial.municipalities")

def execute(context):
    df_departements = context.stage("data.spatial.municipalities").dissolve(
        by = "departement_id").drop(columns = ["commune_id", "has_iris"]).reset_index()

    return df_departements
