"""Gradio interface for the same four saved group artifacts."""
import gradio as gr
from predictions import SPECS, PHARMACY, input_schema, predict


def make_callback(key, fields):
    def callback(*values):
        payload = dict(zip(fields, values))
        if key == "pharmacy-recommender":
            payload["cart"] = [token.strip() for token in payload["cart"].split(",") if token.strip()]
            payload["top_n"] = int(payload["top_n"])
        try:
            return predict(key, payload)
        except (ValueError, TypeError, KeyError) as error:
            raise gr.Error(str(error)) from error
    return callback


CALLBACKS = {}
with gr.Blocks(title="B4 | Model validation") as demo:
    gr.Markdown("# B4 · Model validation\nTry the four models from your group's class work. Synthetic teaching data.")
    for key, spec in SPECS.items():
        with gr.Tab(spec["title"]):
            gr.Markdown(spec["description"])
            if key == "pharmacy-recommender":
                fields = ["cart", "top_n"]
                inputs = [gr.Textbox(label="Products already in basket (comma separated)",
                                     value=", ".join(spec["defaults"]["cart"])),
                          gr.Number(label="Maximum suggestions", value=3, precision=0, minimum=1, maximum=20)]
            else:
                schema = input_schema(key)
                fields = [field["name"] for field in schema]
                inputs = [gr.Dropdown(label=field["label"], choices=field["options"], value=field["default"])
                          if field["options"] else gr.Number(label=field["label"], value=field["default"])
                          for field in schema]
            callback = make_callback(key, fields)
            CALLBACKS[key] = (callback, fields)
            gr.Interface(callback, inputs=inputs, outputs=gr.JSON(label="Prediction result"),
                         flagging_mode="never")

if __name__ == "__main__":
    demo.launch()
