from textual.app import App, ComposeResult
from textual.screen import Screen
from textual.color import Color
from textual.events import Key
from textual.widgets import Static, Header, Footer, Button, Input, RichLog, Log, Label
from textual.containers import Container, VerticalScroll


class LOGIN(Screen[str]):
	CSS_PATH = "foo.tcss"
	def compose(self) -> ComposeResult:
		yield Label("What is your Username?", id="username_query")
		self.username_input_box = Input(id="username_input")
		yield self.username_input_box

	def on_input_submitted(self) -> None:
		self.dismiss(self.username_input_box.value)

class CHAT(Screen):
	CSS_PATH = "foo.tcss"
	def compose(self) -> ComposeResult:
		
		self.widget1 = RichLog(id="chat")
		yield self.widget1
		self.widget2 = RichLog(id="whisper")
		yield self.widget2
		self.typing_zone = Input(validate_on=["submitted"],valid_empty=(False),id="textbox")
		yield self.typing_zone
		yield Footer()
		yield Header()

	def on_mount(self) -> None:
		self.widget1.border_title = "Main Chat"
		self.widget1.auto_scroll = True
		self.widget2.border_title = "Whisper"
		self.widget2.auto_scroll = True

	def _on_input_changed(self) -> None:
		self.widget1.write(self.typing_zone.value + "\n")

	def on_input_submitted(self) -> None:
		input = self.typing_zone
		self.widget2.write(input.value + "\n")
		input.value = ""
	

class CS3800_CHATROOM(App):
	CSS_PATH = "foo.tcss"
	SCREENS = {
		"login" : LOGIN(),
		"chat" : CHAT()
	}
	
	def on_mount(self) -> None:
		self.push_screen(CHAT())
		self.push_screen(LOGIN())
	

	


if __name__ == "__main__":
	app = CS3800_CHATROOM()
	app.run()
