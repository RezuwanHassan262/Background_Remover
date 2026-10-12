import os
import io
import uuid
import tempfile

# rembg downloads its model (~176MB) to this directory on first use.
# Force it to a directory we know is writable inside the container,
# instead of relying on the default ~/.u2net (which can fail silently
# or hang retrying if $HOME isn't writable in this environment).
MODEL_CACHE_DIR = "/tmp/.u2net"
os.makedirs(MODEL_CACHE_DIR, exist_ok=True)
os.environ.setdefault("U2NET_HOME", MODEL_CACHE_DIR)

import gradio as gr
from rembg import remove
from PIL import Image

OUTPUT_DIR = "/tmp/bg_remove_outputs"
os.makedirs(OUTPUT_DIR, exist_ok=True)


def remove_background(image):
    if image is None:
        return None, "Please upload or select an image first."

    try:
        input_bytes = io.BytesIO()
        image.save(input_bytes, format="PNG")
        input_bytes = input_bytes.getvalue()

        output_bytes = remove(input_bytes)
        output_img = Image.open(io.BytesIO(output_bytes))

        # unique filename per request so concurrent users never collide
        output_path = os.path.join(OUTPUT_DIR, f"{uuid.uuid4().hex}.png")
        output_img.save(output_path, format="PNG")

        return output_path, "Background removed successfully!"
    except Exception as e:
        return None, f"Something went wrong while removing the background: {e}"


# Example images
example_images = [
    "examples/1.jpg",
    "examples/2.jpg",
    "examples/3.jpg",
    "examples/4.jpg",
    "examples/5.jpg",
    "examples/6.png",
]

with gr.Blocks(title="Background Remover") as demo:
    gr.Markdown("# Background Remover")
    gr.Markdown(
        """
        Upload an image or use an example to remove its background.
        PS: Not the best image background remover out there but good enough for a free tool.
        """
    )

    with gr.Row():
        with gr.Column():
            image_input = gr.Image(type="pil", label="Input Image")
            submit_btn = gr.Button("Submit")
            clear_btn = gr.Button("Clear")
        with gr.Column():
            output_image = gr.Image(label="Output", type="filepath")
            output_text = gr.Textbox(label="Status", lines=1)
            download_file = gr.File(label="Download Output", visible=False)

    with gr.Row():
        gr.Markdown("### Example Images")
    with gr.Row():
        gr.Examples(
            examples=example_images,
            inputs=image_input,
            label="Click to try an example",
        )

    # Logic
    def process(img):
        output_path, msg = remove_background(img)
        has_output = output_path is not None
        return (
            output_path,
            msg,
            gr.update(visible=has_output, value=output_path if has_output else None),
        )

    submit_btn.click(fn=process, inputs=image_input, outputs=[output_image, output_text, download_file])
    clear_btn.click(
        fn=lambda: (None, "", gr.update(visible=False, value=None)),
        outputs=[output_image, output_text, download_file],
    )

if __name__ == "__main__":
    demo.launch()