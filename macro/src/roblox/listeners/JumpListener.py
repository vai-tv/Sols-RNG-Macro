from pynput import keyboard
from pynput.keyboard import Key, KeyCode
from ..ListenerManager import Listener

__all__ = ["JumpListener"]

class JumpListener(Listener):
	
	def __init__(self):
		self.config = {
			"key" : "1"
		}
		
		super().__init__(keychar=self.config["key"])
		self.keychar = self.keychar

		self.keyboard = keyboard.Controller()
        
	def start(self):
		print(f"JumpListener started with key: {self.keychar}")

	def handle(self) -> bool | None:
		self.keyboard.press(key=Listener._keycode("space"))

		return True