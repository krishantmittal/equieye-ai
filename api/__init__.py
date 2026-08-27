# api/
# FastAPI backend. Contains no analysis logic — routers own HTTP concerns
# only and delegate to the framework-agnostic services/ and modules/
# packages, which the Streamlit app also uses. That shared spine is what
# keeps the two hosts from drifting apart during the migration.
