# services/
#
# Framework-agnostic service layer extracted from app.py (Phase 1 of the
# website rebuild — see project notes). Every module in this package has
# zero Streamlit dependency, matching the existing pattern in modules/:
# caching, st.secrets, and st.error/st.warning calls all stay in app.py's
# thin wrapper functions, so this package can be imported unchanged by a
# future FastAPI service layer.
