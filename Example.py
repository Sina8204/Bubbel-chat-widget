from Bubbel_chat_qtpy6 import *
from google import genai # pip install -U google-genai
from PySide6.QtWidgets import QMainWindow
from dotenv import load_dotenv
import os , threading

load_dotenv()
api_key = os.getenv("API_KEY")

class GeminiAPI:
    def __init__(self, api_key):
        self.key = api_key
        self.client = genai.Client(api_key=api_key)

    def send_prompt(self , promt : str , model = "gemini-3.8-flash" , **kwargs):
        """
        keys : output_text , id
        """
        interaction = self.client.interactions.create(
            model=model,
            input=promt,
            **kwargs
        )
        return {
            "output_text": interaction.output_text ,
            "id": interaction.id
        }

    def strem_answer(self, prompt: str, model="gemini-3.5-flash-lite" , **kwargs):
        """
        keys : output_text , id
        """
        stream = self.client.interactions.create(
            model=model,
            input=prompt,
            stream=True,
            **kwargs
        )
        return stream

ai = GeminiAPI(api_key=api_key)
model = "gemini-3.5-flash-lite"

class ai_chat(ChatWindow):
    def __init__(self):
        super().__init__()
        self.message_policy = self.send_prompt
        self.end_msg_id = None
    
    def send_prompt(self):
        text = self.get_input_field()
        self.send(text=text)
        self.set_waiting(True)
        threading.Thread(target=lambda : self.receive_msg_with_streaming(text) , daemon=True).start()

    def receive_msg_directly(self  , text):
        ai_answer = ai.send_prompt(text, model=model)["output_text"]
        self.receive(text=ai_answer)
        self.set_waiting(False)
        # print(ai_answer)

    def receive_msg_with_streaming(self  , text):
        stream = ai.strem_answer(
            text, model=model)
        for event in stream:
            # Text generate => check event type : that must be delta type 
            if event.event_type == "step.delta":
                # delta type must be 'text'
                if event.delta.type == "text":
                    # Show generated text
                    self.stream(event.delta.text)
                    # print(event.delta.text , end="" , flush=True)
        self.set_waiting(False)
        self.end_msg_id = None
    
    def stream(self , txt):
        try:
            if self.end_msg_id is None:
                self.receive(text=txt)
                self.end_msg_id = self.model.messages[-1]["id"]
            else:
                self.edit_message(
                    msg_id=self.end_msg_id ,
                    edited_text = self.model.messages[-1]['text'] + f" {txt}"
                )
        except Exception as e:
            print(f"Error : {e}")

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.resize(400, 600)
        self.setWindowTitle("Chat bot")

        self.widgets = ai_chat()
        self.setCentralWidget(self.widgets)

if __name__ == "__main__":
    from PySide6.QtWidgets import QApplication
    app = QApplication([])

    window = MainWindow()
    window.show()

    app.exec()