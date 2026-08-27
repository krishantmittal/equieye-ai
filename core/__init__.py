# core/
#
# Framework-agnostic infrastructure shared by both hosts: the existing
# Streamlit app and the FastAPI backend. Nothing here imports Streamlit at
# module level — config.py imports it lazily, and only as a fallback when
# an environment variable is absent.
