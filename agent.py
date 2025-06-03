import gradio as gr


def greet(name):
    return "Hello " + name + "!"


with gr.Blocks() as gui:
    name = gr.Textbox(label="Name")
    output = gr.Textbox(label="Output Box")
    greet_btn = gr.Button("Greet")
    greet_btn.click(fn=greet, inputs=name, outputs=output, api_name="greet")


def main():
    gui.launch(debug=True, share=False)


if __name__ == "__main__":
    main()
