---
title: B4 Model Validation
emoji: 📊
colorFrom: green
colorTo: blue
sdk: gradio
sdk_version: 6.30.0
app_file: gradio_app.py
python_version: '3.12'
---

# B4: put your trained models in other people's hands

The aim is to let a domain expert enter a new example, inspect a prediction, and give feedback. The apps load saved models; they do not retrain them when a user clicks a button.

For a plain-language explanation and a submission-video outline, read [STUDENT-WALKTHROUGH.md](STUDENT-WALKTHROUGH.md).

**Selected submission tier: Intermediate.** The local API, Docker/Gunicorn/Nginx setup and public Render API have passed all four model examples. The required video and real member contributions still need to be added. Streamlit is an additional working demo; Hugging Face hosting is outside this selected tier.

**Live Streamlit app:** <https://b4-model-validation-nadine.streamlit.app/>. All four tabs were tested with real predictions on 19 October 2026. It deploys from `feature/b4-model-validation`, using `group-project/app.py` and Python 3.12. The app's sharing panel confirms public access. See `deployment-status.json` for the verified examples and remaining work.

**Live Render API and HTML demo:** <https://b4-group-models-nadine.onrender.com/demo>. All four API endpoints returned HTTP 200 with the expected examples on 19 October 2026. The service uses the same branch and artifacts, the Free plan, Python 3.12.14, and one Gunicorn worker. Saved public responses are in `deployment-evidence/render-public-results.json`. Auto-deploy is off for this public-repository connection; deploy future code changes manually in Render.

| Your model | New inputs | Output |
| --- | --- | --- |
| Regression | Study, attendance and student-profile fields | Estimated exam score |
| Classification | Insurance-claim details | Fraudulent/Legitimate and model probabilities |
| Clustering | Account balance, activity, tenure and digital usage | One of three bank-account segments |
| Association rules | Products already in a pharmacy basket | Products frequently bought with them |

## Set up a fresh copy

Use Python 3.12. From the `group-project` folder:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m streamlit run app.py
```

For the Flask API, run `.\.venv\Scripts\python.exe api.py`. To repeat the validation checks, run `.\.venv\Scripts\python.exe check_group_activity.py`. The parent-folder launchers described below apply to the prepared copy on the student's laptop.

The saved artifacts are already included. Rebuilding them is an optional offline recovery step: install `requirements-training.txt` and run `rebuild_missing_models.py`. It is not part of starting or deploying the apps.

## Try this now

Open <http://127.0.0.1:8502> while the local app is running. To start it later, double-click `Start-My-Group-Demo.cmd` in the parent folder.

1. Select **Bank accounts**.
2. Keep the example: balance **3,200,000 KES**, **7** transactions per month, **10** years as a customer, digital usage **55**.
3. Click **Make prediction**. The tested result is **Cluster 2: High-balance established accounts**.
4. Change the profile and compare the assignment. Cluster numbers are labels; the segment name describes the pattern learned from training accounts.
5. Try the other tabs. In **Pharmacy basket**, `Baby Lotion` and `Aloe Vera Gel` produce `Baby Diapers` and `Sunscreen SPF50` from the saved rules.
6. Enter an expert's observation and click **Download result and feedback**. That saves a record locally; it does not send feedback to someone else.

The first three rebuilt artifacts use the original notebook recipes. The recovered classifier uses the group's original saved file. See [PROVENANCE.md](PROVENANCE.md) before describing the recovery in your submission.

## What is verified

- All four saved artifacts load and return predictions through the Flask API.
- Every Streamlit form submits and displays the same result as the API.
- Every Gradio callback returns the same result as the API.
- Basic missing-input and invalid-basket requests return clear HTTP 400 errors.
- Model-file checksums agree with `artifact-manifest.json`.
- Regression RMSE, bank cluster sizes and pharmacy rule counts match the recorded notebook results at the documented precision.
- Docker built successfully and both services ran. All four requests through Nginx at `http://127.0.0.1:8081` returned HTTP 200 with the same saved validation results. A missing-input request returned HTTP 400. The four model hashes inside the container match `artifact-manifest.json`. Evidence is in `deployment-evidence/docker-nginx-results.json` and `deployment-evidence/docker-environment.json`.
- The public Streamlit app and Render API are live; all four models returned the expected example results on each. Hugging Face deployment remains pending because this account's Space setup page requires a paid plan for Gradio hosting.

Run the checks again from this folder:

```powershell
..\.group-venv\Scripts\python.exe check_group_activity.py
```

`validation-results.json` contains the checked sample outputs. They demonstrate execution and agreement, not business accuracy.

## The three hosting choices in the activity

The same four files under `model/` must be used everywhere.

### Streamlit Community Cloud

Upload or commit this reviewed project to the group's [model-serving repository](https://github.com/BI-course/smm-202604-b4). Do not upload the parent folder's virtual environments. If this project is kept in a subfolder named `group-project`, use **group-project/app.py** as the entry point. If its contents become the repository root, use **app.py**. Select Python 3.12 and the branch containing the changes.

At <https://share.streamlit.io>, choose **Create app**, select that repository/branch/file, and deploy. Test one prediction in every tab. [Official instructions](https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app).

### Hugging Face Spaces

Create a Gradio Space if your account has suitable hosting access. Upload this folder's contents, with `model/` preserved. The README metadata points Hugging Face at **gradio_app.py**. The models use CPU inference. Check available hardware and account eligibility on the platform; a local GPU installation is unnecessary. Test all four tabs after the build. [Spaces documentation](https://huggingface.co/docs/hub/spaces-overview).

On 19 October 2026, the signed-in account's [new Space page](https://huggingface.co/new-space) disabled the Gradio and Docker choices and displayed "Gradio and Docker Spaces require a paid plan". No Space was created and no subscription was purchased. The prepared Gradio callbacks have passed locally; a public Gradio deployment has not been verified. Use an account with suitable hosting access to complete the Advanced tier.

Local Gradio launcher: `Start-My-Group-Gradio.cmd` in the parent folder.

### Render

Connect the same repository. If this project is nested, set **Root Directory** to **group-project**. Choose a Free instance when available and Python 3.12. Set:

```text
Build Command: pip install -r requirements.txt
Start Command: gunicorn -w 1 -b 0.0.0.0:$PORT api:app
```

Your API has four routes:

```text
POST /api/v1/models/student-exam-score-regressor/predictions
POST /api/v1/models/insurance-fraud-classifier/predictions
POST /api/v1/models/bank-account-segmenter/predictions
POST /api/v1/models/pharmacy-recommender/predictions
```

The optional HTML forms are at **/demo**. They call the API on the same origin, so no separate CORS setup is required.

After deployment, test all four endpoints from PowerShell:

```powershell
.\Test-API.ps1 -BaseUrl 'https://b4-group-models-nadine.onrender.com'
```

Local API launcher: `Start-My-Group-API.cmd` in the parent folder. The local API is at <http://127.0.0.1:5001>, with the forms at <http://127.0.0.1:5001/demo>. [Render's Flask deployment guide](https://render.com/docs/deploy-flask).

## Docker and Nginx, if you choose Intermediate or Advanced

Start Docker Desktop first. From this folder:

```powershell
docker compose -p b4-model-validation up --build -d
.\Test-API.ps1 -BaseUrl 'http://127.0.0.1:8081'
```

Nginx forwards requests to Gunicorn. Open <http://127.0.0.1:8081/demo> for the HTML forms. This setup was built and tested successfully on the laptop on 19 October 2026. The verified run used Docker Engine 29.4.3, Python 3.12.15, Gunicorn 26.2.0 and Nginx 1.30.6. Only Nginx's port is published to the laptop; Gunicorn remains on the Docker network.

## Before submitting

Follow the [course submission instructions](https://github.com/BI-course/smm-202604-b4/blob/main/lab_submission_instructions.md): record the required walkthrough of no more than 10 minutes, include the public URLs required for your chosen tier, and fill in every member's actual contribution and branch link. Show real predictions, including public deployments and Docker/Nginx when required by your tier. Do not claim a prepared deployment as a live deployment.

In PyCharm, open this project and use the interpreter at `../.group-venv/Scripts/python.exe`. There is no need to reinstall PyCharm.
