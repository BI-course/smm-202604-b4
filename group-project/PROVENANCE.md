# Model sources and recovery

This project adapts the supplied model-serving example to Group B4's own tasks.
The four serving artifacts are kept together in `model/`. They are loaded once;
the Flask, Streamlit and Gradio apps never train or mine rules.

| Task | Source | Serving artifact | Status |
| --- | --- | --- | --- |
| Exam score regression | [Regression_Tuning_Linear_Regression (1).ipynb](https://colab.research.google.com/drive/1NQ3c6PBRBilQNopDNJ7JzWpgSZWqwk4u) | `exam_score_regressor.joblib` | Rebuilt once offline using the original selected features, split, preprocessing and tuning grid |
| Insurance fraud classification | [Classification notebook](https://colab.research.google.com/drive/11qhqCv_6oCUPBhFbdymtxxpgIyNu92-Z) and [saved group model](https://drive.google.com/file/d/1cmnEnIfuE8moKPD5ssYj72D3ONnxxCLr/view) | `fraud_logreg_pipeline.pkl` | Recovered unchanged from the group's Drive folder; records scikit-learn 1.6.1 |
| Bank account segmentation | [b4_clusteringXassociation.ipynb](https://colab.research.google.com/drive/185QzJaL_uxy3ramwflghXz5wTVSDA4Ni) | `bank_segmentation.joblib` | Rebuilt once offline with the notebook's four raw features, median imputation, scaling, k=3, random_state=42 and n_init=20 |
| Pharmacy basket rules | [b4_clusteringXassociation.ipynb](https://colab.research.google.com/drive/185QzJaL_uxy3ramwflghXz5wTVSDA4Ni) | `pharmacy_recommender.json` | Rebuilt once offline with the notebook's Jan–May training split, support .02, confidence .50, lift 2.50 and redundancy cleanup |

The alternative [B4-Lab3_Clustering](https://colab.research.google.com/drive/1yzLGvGv-arYOh6Cn4t5jhuXbpJbTL-so) uses a log-balance transformation and a different two-object save format. It has not been mixed with the combined notebook's raw-balance pipeline.

Recovery was necessary because the regression notebook did not persist its final model, and the combined clustering/association notebook saved to a relative Colab output directory. Those two saved artifacts were not found in persistent Drive storage. This is a new offline rebuild of their recipes, not a claim that their original binary files were recovered.

`source-recipes/` contains the selected original code cells. Regression parallelism was reduced from all cores to one. Bank plot/table cross-references were omitted. The prediction and data-preprocessing algorithms were retained. `rebuild_missing_models.py` is the explicit offline recovery step. `mlxtend==0.23.4` is required only for rebuilding pharmacy rules; JSON inference does not require it.

The bank/pharmacy teaching data are pinned to course repository commit `8733fd215f6bcd08168741220005458e38b8a090`. All three input CSVs are checked against the hashes recorded in the notebooks before rebuilding. The student-score CSV's bytes also match the hash recorded in Member 2's notebook.

Recovery checks against archived notebook outputs:

- Regression: test RMSE 6.4941 (rounded), MAE 4.9684, R² .5245; best CV RMSE 7.3916.
- Banking: three clusters with 60, 299 and 341 accounts.
- Pharmacy: 3,012 training receipts, 30 itemsets, 34 candidate rules, 11 cleaned rules.

These are consistency checks; they do not establish bit-for-bit equivalence with unavailable original trained files or validate business accuracy. `artifact-manifest.json` records the new serving artifacts' checksums and library versions. `check_group_activity.py` checks successful predictions and agreement across the API, Streamlit forms and Gradio callbacks.

The supplied SME and mall models remain in the parent folder for learning. They are not used by this group project.
