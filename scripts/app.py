import gradio as gr
from rembg import remove
from PIL import Image
import io
import os

OUTPUT_FILE = "output.png"

# Background removal function
def remove_background(image):
    input_bytes = io.BytesIO()
    image.save(input_bytes, format='PNG')
    input_bytes = input_bytes.getvalue()

    output_bytes = remove(input_bytes)
    output_img = Image.open(io.BytesIO(output_bytes))
    output_img.save(OUTPUT_FILE, format="PNG")

    return OUTPUT_FILE, "Background removed successfully!"

# Example images
example_images = [
    "examples/1.jpg",
    "examples/2.jpg",
    "examples/3.jpg",
    "examples/4.jpg",
    "examples/5.jpg",
    "examples/6.png"
]

with gr.Blocks(title="Background Remover") as demo:
    gr.Markdown("# Background Remover")
    gr.Markdown("""
    Upload an image or use an example to remove its background.  
    PS: Not the best image background remover out there but good enough for a free tool.
    """)

    with gr.Row():
        with gr.Column():
            image_input = gr.Image(type="pil", label="Input Image")
            submit_btn = gr.Button("Submit")
            clear_btn = gr.Button("Clear")
        with gr.Column():
            output_image = gr.Image(label="Output", type="filepath")
            output_text = gr.Textbox(label="Status", lines=1)
            download_html = gr.HTML(visible=False)

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
        download_button = f"""
        <a href="file/{output_path}" download style="
            display:inline-block;
            padding: 10px 20px;
            background-color: #4CAF50;
            color: white;
            text-align: center;
            text-decoration: none;
            border-radius: 5px;
            font-weight: bold;
            margin-top: 10px;
        ">⬇ Download Output</a>
        """
        return output_path, msg, gr.update(visible=True, value=download_button)

    submit_btn.click(fn=process, inputs=image_input, outputs=[output_image, output_text, download_html])
    clear_btn.click(fn=lambda: (None, "", gr.update(visible=False, value="")), outputs=[image_input, output_text, download_html])

demo.launch()
