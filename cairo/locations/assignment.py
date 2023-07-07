from .components import CandidateIndex

def configure(context):
    context.stage("cairo.locations.candidates")

def execute(context):
    df_candidates = context.stage("cairo.locations.candidates")
    candidate_index = CandidateIndex(df_candidates, "location_id")

    
    



