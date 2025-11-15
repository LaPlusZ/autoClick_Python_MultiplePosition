import time
import threading
import pyautogui
import pydirectinput

class ClickerThread(threading.Thread):
    def __init__(self, actions, interval):
        super().__init__(daemon=True)
        self.actions = actions
        self.interval = interval
        self._stop_event = threading.Event()

    def move_slightly(self, x, y):
        """Moves to a position and wiggles slightly to register as a 'real' move."""
        pydirectinput.moveTo(x, y)
        pydirectinput.moveRel(1, 0)

    def run(self):
        """The main click loop. Runs until the stop_event is set."""
        next_time = time.perf_counter()
        while not self._stop_event.is_set():
            for action in self.actions:
                # Check if we've been told to stop *during* the action list
                if self._stop_event.is_set():
                    break

                if action["type"] == "click":
                    if action.get("move_before_click", False):
                        self.move_slightly(action["x"], action["y"])
                    else:
                        pyautogui.moveTo(action["x"], action["y"], duration=0.1)
                    
                    pydirectinput.mouseDown()
                    pydirectinput.mouseUp()
                
                elif action["type"] == "keypress":
                    pyautogui.press(action["key"])

                # Calculate sleep time
                next_time += self.interval
                sleep_time = next_time - time.perf_counter()
                
                if sleep_time > 0:
                    self._stop_event.wait(sleep_time)

    def stop(self):
        self._stop_event.set()