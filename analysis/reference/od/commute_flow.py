def configure(context):
    context.stage("data.od.cleaned")

def execute(context):
    result = {}

    for df_data, name in zip(context.stage("data.od.cleaned"), ("work", "education")):
        df_data = df_data.rename(columns = {
            "origin_id": "home",
            "destination_id": name
        })

        df_data["home"] = df_data["home"] // 1000
        df_data[name] = df_data[name] // 1000

        df_data = df_data.groupby(["home", name])["weight"].sum().reset_index()
        result[name] = df_data

    return result
