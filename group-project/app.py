"""Streamlit UI using the same group artifacts and functions as api.py."""
import json
import streamlit as st

st.set_page_config(page_title="B4 | Model validation", page_icon="📊", layout="centered")


@st.cache_resource
def load_prediction_module():
    import predictions
    return predictions


p = load_prediction_module()
st.title("B4 · Model validation")
st.caption("Four models from your group's class work · synthetic teaching datasets")
st.info("Enter a new example, make a prediction, and compare the result with an expert's expectation.")
tabs = st.tabs([spec["title"] for spec in p.SPECS.values()])
for (key, spec), tab in zip(p.SPECS.items(), tabs):
    with tab:
        st.subheader(spec["title"])
        st.write(spec["description"])
        with st.form(key):
            payload = {}
            if key == "pharmacy-recommender":
                payload["cart"] = st.multiselect("Products already in the basket",
                    sorted(p.PHARMACY["item_id_to_name"].values()), default=spec["defaults"]["cart"])
                payload["top_n"] = st.number_input("Maximum suggestions", min_value=1, max_value=20, value=3)
            else:
                for field in p.input_schema(key):
                    name, label = field["name"], field["label"]
                    if field["options"]:
                        payload[name] = st.selectbox(label, field["options"],
                            index=field["options"].index(str(field["default"])), key=key + name)
                    else:
                        payload[name] = st.number_input(label, value=float(field["default"]), key=key + name)
            submitted = st.form_submit_button("Make prediction", type="primary")
        if submitted:
            try:
                st.session_state[key + "result"] = {"model": key, "inputs": payload, "output": p.predict(key, payload)}
            except (ValueError, TypeError, KeyError) as error:
                st.session_state.pop(key + "result", None)
                st.error(str(error))
        record = st.session_state.get(key + "result")
        if record:
            result = record["output"]
            if key == "student-exam-score-regressor":
                st.success(f"Predicted final exam score: {result['predicted_final_exam_score']:.2f}")
            elif key == "insurance-fraud-classifier":
                st.success(f"Predicted claim category: {result['category']}")
                st.json(result["class_probabilities"])
            elif key == "bank-account-segmenter":
                st.success(f"Cluster {result['assigned_cluster']}: {result['segment']}")
            else:
                if result["recommendations"]:
                    st.dataframe(result["recommendations"], hide_index=True)
                else:
                    st.info("No rule matches this basket. Try Baby Lotion and Aloe Vera Gel.")
                st.caption(result["meaning"])
            feedback = st.text_area("Expert feedback: is this result reasonable?", key=key + "feedback")
            st.download_button("Download result and feedback", json.dumps({**record, "expert_feedback": feedback}, indent=2),
                               file_name=key + "-validation.json", mime="application/json", key=key + "download")
