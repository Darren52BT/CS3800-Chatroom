from typing import Coroutine
from textual.app import App, ComposeResult
from textual.color import Color
from textual.events import Key
from textual.widgets import Static, Header, Footer, Button, Input, RichLog
from textual.containers import Container, Horizontal

TEXT = """I must not fear.
Fear is the mind-killer.
Fear is the little-death that brings total obliteration.
I will face my fear.
I will permit it to pass over me and through me.
And when it has gone past, I will turn the inner eye to see its path.
Where the fear has gone there will be nothing. Only I will remain."""
QUESTION = "May thy knife chip and shatter"


class GUI(App):
	CSS_PATH = "foo.tcss"

	def compose(self) -> ComposeResult:
		self.widget1 = RichLog(id="chat")
		yield self.widget1
		self.widget2 = RichLog(id="whisper")
		yield self.widget2
		yield Input(QUESTION, id="textbox")
		yield Footer()
		yield Header()

	def on_mount(self) -> None:
		self.widget1.border_title = "Main Chat"
		self.widget2.border_title = "Whisper"

	def _on_input_changed(self) -> None:
		self.widget1.write(self.query_one(Input).value)


	def on_input_submitted(self) -> None:
		input = self.query_one(Input)
		self.widget2.write(input.value)
		input.value = ""

	

		
if __name__ == "__main__":
	app = GUI()
	app.run()
