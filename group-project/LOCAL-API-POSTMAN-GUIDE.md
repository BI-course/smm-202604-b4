# Local Flask API: regression and classification demo

This guide supports the video segment that demonstrates the exam-score regressor and insurance-fraud classifier through the local Flask API.

## Start the API

From the `group-project` folder, start the API with the project's Python environment:

```bash
./.venv/Scripts/python.exe api.py
```

Leave that terminal open while sending requests. The local API listens at `http://127.0.0.1:5001`. Opening that address in a browser checks that the API is ready; it does not make a model prediction.

## Send the two Postman requests

Create or open a Postman collection and use **POST**, **Body → raw → JSON** for each request. Copy the matching JSON object from `examples.json` into the request body.

| Model task | Request URL | Expected example response |
| --- | --- | --- |
| Exam-score regression | `http://127.0.0.1:5001/api/v1/models/student-exam-score-regressor/predictions` | HTTP 200; predicted score about 91.781 |
| Insurance-fraud classification | `http://127.0.0.1:5001/api/v1/models/insurance-fraud-classifier/predictions` | HTTP 200; class 1, labelled `Fraudulent`, with class probabilities |

`200 OK` means the request succeeded. Regression returns a numeric estimate. Classification returns a category and probabilities for this example; those probabilities are not proof that a real claim is fraudulent.

## Explain what happens

Postman sends the JSON input values to Flask. `api.py` routes the request to the right prediction function, and `predictions.py` loads and uses the saved model artifact. The prediction is returned to Postman as JSON. The API does not retrain a model for each request.

Artifact details: the insurance classifier was recovered from the group's saved model file. The exam-score artifact was rebuilt once offline from the original notebook recipe because its original saved file was unavailable. See `PROVENANCE.md` for the full record.
