import gradio as gr

def greet(name, intensity):
    return "hello," + name + "!"* int(intensity)


# 建立interface實體
demo = gr.Interface(
    fn=greet,
    inputs=["text", "slider"],
    outputs=["text"],
    examples=[["gd",1],["xxx", 2]]
    
)



demo.launch()


