import datetime
import logging
import threading

from pynput import mouse, keyboard

class EventLogger:
    def __init__(self):
        self.keyboard_listener = keyboard.Listener(on_press=self.on_key_press)
        self.mouse_listener = mouse.Listener(on_click=self.on_mouse_click, on_move=self.on_mouse_move, on_scroll=self.on_mouse_scroll)

    def on_key_press(self, key):
        logging.info(f'{datetime.datetime.now()} - Key pressed: {key}')
    
    def on_mouse_click(self, x, y, button, pressed):
        logging.info(f'{datetime.datetime.now()} - Mouse clicked at ({x}, {y}) with button {button} {"pressed" if pressed else "released"}')

    def on_mouse_move(self, x, y):
        logging.info(f'{datetime.datetime.now()} - Mouse moved to ({x}, {y})')

    def on_mouse_scroll(self, x, y, dx, dy):
        logging.info(f'{datetime.datetime.now()} - Mouse scrolled at ({x}, {y}) with delta ({dx}, {dy})')

    def start(self):
        self.keyboard_listener.start()
        self.mouse_listener.start()

    def stop(self):
        self.keyboard_listener.stop()
        self.mouse_listener.stop()

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
    logger = EventLogger()
    logger.start()
    threading.Event().wait()  # Wait forever in background