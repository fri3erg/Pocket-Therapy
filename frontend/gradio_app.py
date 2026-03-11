import gradio as gr
from backend.chat import TherapyAgent


def create_ui():
    agent = TherapyAgent()
    
    def reset_all():
        return "", [], agent.get_system_prompt()
    
    # Custom CSS for the neon cyan button and layout
    custom_css = """
    #send-button {
        background-color: rgba(20, 255, 234, 0.6) !important;
        border: none !important;
        min-width: 60px !important;
        height: 42px !important;
        align-self: center !important;
        transition: all 0.2s ease !important;
        display: flex !important;
        justify-content: center !important;
        align-items: center !important;
    }
    #send-button:hover {
        background-color: rgba(20, 255, 234, 0.9) !important;
        transform: scale(1.05);
    }
    /* Ensure only the icon from our SVG shows correctly */
    #send-button img {
        height: 24px !important;
        width: 24px !important;
    }
    """
    
    with gr.Blocks(title="Pocket Therapy", css=custom_css) as demo:
        gr.Markdown("# Pocket Therapy Chatbot \n\nYour personal AI therapist.")
        
        with gr.Row():
            with gr.Column(scale=3):
                chatbot = gr.Chatbot(height=500)
                with gr.Row(equal_height=True):
                    msg = gr.Textbox(
                        placeholder="How are you feeling today?",
                        show_label=False,
                        scale=9,
                        container=False # Removes the extra padding/box around the field
                    )
                    submit_btn = gr.Button(
                        value="", # Empty text, only icon
                        icon="frontend/paper-plane.svg",
                        variant="primary", 
                        scale=1, 
                        elem_id="send-button"
                    )

                clear_btn = gr.Button("Reset Conversation")

                
            with gr.Column(scale=1):
                system_prompt_viewer = gr.Textbox(
                    label="Current System Prompt",
                    value=agent.get_system_prompt(),
                    interactive=False,
                    lines=10,
                    visible=True
                )
        
        # We wrap the update to update both chatbot and system prompt viewer
        def handle_message(message, history):
            res = agent.get_response(message, history)
            # Use dictionary format required by modern Gradio version
            history.append({"role": "user", "content": message})
            history.append({"role": "assistant", "content": res})
            # Return empty msg, updated history, updated prompt
            return "", history, agent.get_system_prompt()

        
        clear_btn.click(reset_all, None, [msg, chatbot, system_prompt_viewer])
        msg.submit(handle_message, [msg, chatbot], [msg, chatbot, system_prompt_viewer])
        submit_btn.click(handle_message, [msg, chatbot], [msg, chatbot, system_prompt_viewer])

    return demo
