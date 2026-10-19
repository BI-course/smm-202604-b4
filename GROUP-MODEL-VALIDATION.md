# B4 group model-validation project

The group's four-model serving implementation is in [group-project](group-project/README.md).

**Live app:** <https://b4-model-validation-nadine.streamlit.app/> — all four tabs verified on 19 October 2026.
**Live API and HTML forms:** <https://b4-group-models-nadine.onrender.com/demo> — all four API endpoints verified on 19 October 2026.
It covers exam-score regression, insurance-fraud classification, bank-account clustering,
and pharmacy basket recommendations through one Flask API, a Streamlit app, a Gradio app,
and optional HTML forms.

- [Setup, local practice and hosting instructions](group-project/README.md)
- [Model sources and offline recovery record](group-project/PROVENANCE.md)
- [Saved-model checksums and recovery checks](group-project/artifact-manifest.json)
- [Validated sample responses](group-project/validation-results.json)

For Streamlit Community Cloud, select `group-project/app.py` and Python 3.12.
For Render, set Root Directory to `group-project` and follow its README.
For Hugging Face Spaces, upload the contents of `group-project` as the Space repository root.

The Streamlit and Render deployment URLs are recorded in `group-project/deployment-status.json`.
Docker with Gunicorn and Nginx has also passed all four requests at `http://127.0.0.1:8081`.
Hugging Face deployment (this account requires paid Gradio hosting access), the demonstration video, and individual
member contributions still need to be completed and recorded in the course submission.
