# Understand and demonstrate your B4 serving lab

**Your selected tier is Intermediate.** Record the local API, the same API through Docker/Nginx, and the public Render API. Each must return a prediction for all four models. The public Streamlit app is available as an extra demo. A Hugging Face Space is not required for your selected tier.

The class activity takes models your group already trained and lets other people try them. A domain expert enters a new example, checks whether the result makes sense, and records feedback. Starting these apps loads the saved files in `model/`; clicking a prediction button does not train a new model.

## What each part does

| Part | Its job in your project |
| --- | --- |
| Saved model or rules | Stores the pattern learned in an earlier lab |
| Flask API (`api.py`) | Receives a JSON input and returns a JSON prediction |
| Streamlit and Gradio | Provide forms and tabs for a person to use |
| HTML page (`/demo`) | Uses JavaScript to send the form to the Flask API |
| Gunicorn | Runs the Flask app inside the container and on Render |
| Nginx | Receives requests on port 8081 and forwards them to Gunicorn inside Docker |
| Docker | Packages the app and its dependencies for a repeatable run |
| Render | Hosts the API publicly so another computer can call it |
| GitHub | Stores the source, saved artifacts, instructions, and verification evidence |

The four tasks are different:

- **Regression:** estimate an exam score, which is a number. The supplied example returns **91.781**.
- **Classification:** assign an insurance claim to a category. The supplied example returns **Fraudulent**. The displayed model probabilities describe this prediction; they do not measure overall model accuracy.
- **Clustering:** assign an account to a group of similar accounts. The supplied example returns **Cluster 2: High-balance established accounts**. Cluster numbers identify groups; they do not rank account quality.
- **Association rules:** suggest products that appeared with items in a basket. Baby Lotion and Aloe Vera Gel produce **Baby Diapers** and **Sunscreen SPF50**. Confidence describes the observed co-purchase proportion; lift compares it with the item's overall frequency.

Use `PROVENANCE.md` when explaining where the files came from: the fraud pipeline is the recovered original saved artifact. Three missing artifacts were rebuilt once, offline, using the documented original notebook recipes. The same saved files are used by every serving interface.

## Practice before recording

Open the prepared `group-project` folder in PyCharm. On this laptop the prepared interpreter is `C:\Users\admin\Desktop\IS PROJECT\model-validation-lab\.group-venv\Scripts\python.exe`.

The parent folder contains `Start-My-Group-API.cmd` and `Start-My-Group-Demo.cmd` for the local API and Streamlit app. Keep the API window open while testing it.

In PowerShell, open this folder and run:

```powershell
.\Test-API.ps1 -BaseUrl 'http://127.0.0.1:5001'
.\Test-API.ps1 -BaseUrl 'http://127.0.0.1:8081'
.\Test-API.ps1 -BaseUrl 'https://b4-group-models-nadine.onrender.com'
```

Each command submits the four examples from `examples.json`. Port 5001 is the local Flask server. Port 8081 reaches Nginx in Docker. The HTTPS address reaches Render. The Docker command requires the class containers to be running:

```powershell
docker compose -p b4-model-validation up --build -d
docker compose -p b4-model-validation ps
```

Compare the predictions across all three. A sleeping free host may need time to wake up. If a browser form reports a temporary connection error, wait for the service to become ready and submit again.

## A video outline of under 10 minutes

Only describe a deployment as working after showing it working in your recording.

| Approximate time | Show and explain |
| --- | --- |
| 0:00–1:00 | Introduce the group and the four tasks. Show `api.py`, `predictions.py`, and `model/`. Explain that artifacts load at startup. |
| 1:00–3:00 | Run the local API and the first PowerShell command above. Show a successful request and response for every model. |
| 3:00–5:00 | Show the two running Docker services, then test port 8081. Explain Nginx → Gunicorn → Flask → saved model. |
| 5:00–7:00 | Test the public Render API. Show its public address and successful responses for all four models. |
| 7:00–8:00 | Explain one prediction and how an expert could review it. You may briefly show the HTML or Streamlit form as extra work. |
| 8:00–9:00 | State each member's actual contribution and what each person learned. |

Public links and remaining deployment work are recorded in `deployment-status.json`. Put the final video link, chosen tier, names, student IDs, and honest individual contributions in the repository's `lab_submission_instructions.md`. Check the lecturer can view the video. Keep the video itself out of the Git repository.

The local API, Docker/Nginx API and public Render API have passed all four example requests. These cover the Intermediate technical deployment requirements. The public Streamlit app is also verified. The optional Advanced tier would need a public Gradio Space; the checked Hugging Face account currently requires paid hosting access for that SDK.

Before presenting, be ready to explain: what input each model needs, what its output means, why all hosts use identical saved files, and how the API differs from the user interface.
