import gradio as gr
from backend.chat import TherapyAgent


def create_ui():
    agent = TherapyAgent()
    
    def reset_all():
        return "", [], agent.get_system_prompt()
    
    with gr.Blocks(title="Pocket Therapy") as demo:
        gr.Markdown("# Pocket Therapy Chatbot \n\nYour personal AI therapist.")
        
        with gr.Row():
            with gr.Column(scale=3):
                chatbot = gr.Chatbot(height=500)
                with gr.Row():
                    msg = gr.Textbox(
                        label=None, # Removed label for a cleaner 'chat bar' look
                        placeholder="How are you feeling today?",
                        show_label=False,
                        scale=8 # Textbox takes up most of the row
                    )
                    submit_btn = gr.Button("Send", variant="primary", scale=1)

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
            user_message = {"role": "user", "content": message}
            bot_res = {"role": "assistant", "content": res}
            history.append(user_message)
            history.append(bot_res)
            # Return empty msg, updated history, updated prompt
            return "", history, agent.get_system_prompt()
        
        clear_btn.click(reset_all, None, [msg, chatbot, system_prompt_viewer])
        msg.submit(handle_message, [msg, chatbot], [msg, chatbot, system_prompt_viewer])
        submit_btn.click(handle_message, [msg, chatbot], [msg, chatbot, system_prompt_viewer])

    return demo
