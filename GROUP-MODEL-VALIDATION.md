# B4 group model-validation project

The group's four-model serving implementation is in [group-project](group-project/README.md).
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

Public deployment URLs, Docker execution, the demonstration video, and individual
member contributions must still be recorded in the course submission as they are completed.
