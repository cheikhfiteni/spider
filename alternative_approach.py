import pynput
import time
from collections import defaultdict
import matplotlib.pyplot as plt

class ActivityTracker:
    def __init__(self):
        self.mouse_listener = pynput.mouse.Listener(on_move=self.on_move, on_click=self.on_click)
        self.keyboard_listener = pynput.keyboard.Listener(on_press=self.on_press)
        self.start_time = time.time()
        self.data = defaultdict(lambda: {'left_clicks': 0, 'right_clicks': 0, 'middle_clicks': 0, 'keypresses': 0, 'mouse_movement': 0})
        self.last_position = None
        self.last_move_time = None

    def on_move(self, x, y):
        current_time = time.time()
        if not hasattr(self, 'last_move_time') or current_time - self.last_move_time >= 0.5:
            if self.last_position:
                dx, dy = x - self.last_position[0], y - self.last_position[1]
                distance = (dx**2 + dy**2)**0.5
                self.data[int(current_time - self.start_time)]['mouse_movement'] += distance
            self.last_position = (x, y)
            self.last_move_time = current_time

    def on_click(self, x, y, button, pressed):
        if pressed:
            if button == pynput.mouse.Button.left:
                self.data[int(time.time() - self.start_time)]['left_clicks'] += 1
            elif button == pynput.mouse.Button.right:
                self.data[int(time.time() - self.start_time)]['right_clicks'] += 1
            elif button == pynput.mouse.Button.middle:
                self.data[int(time.time() - self.start_time)]['middle_clicks'] += 1

    def on_press(self, key):
        self.data[int(time.time() - self.start_time)]['keypresses'] += 1

    def start(self):
        self.mouse_listener.start()
        self.keyboard_listener.start()

    def stop(self):
        self.mouse_listener.stop()
        self.keyboard_listener.stop()

    def plot_data(self):
        times = list(self.data.keys())
        left_clicks = [d['left_clicks'] for d in self.data.values()]
        right_clicks = [d['right_clicks'] for d in self.data.values()]
        middle_clicks = [d['middle_clicks'] for d in self.data.values()]
        keypresses = [d['keypresses'] for d in self.data.values()]
        mouse_movement = [d['mouse_movement'] for d in self.data.values()]

        plt.figure(figsize=(12, 6))
        plt.plot(times, left_clicks, label='Left Clicks')
        plt.plot(times, right_clicks, label='Right Clicks')
        plt.plot(times, middle_clicks, label='Middle Clicks')
        plt.plot(times, keypresses, label='Keypresses')
        plt.plot(times, mouse_movement, label='Mouse Movement')
        plt.xlabel('Time (seconds)')
        plt.ylabel('Count')
        plt.title('Mouse and Keyboard Activity')
        plt.legend()
        plt.show()

        print(f"Total Left Clicks: {sum(left_clicks)}")
        print(f"Total Right Clicks: {sum(right_clicks)}")
        print(f"Total Middle Clicks: {sum(middle_clicks)}")
        print(f"Total Keypresses: {sum(keypresses)}")
        print(f"Total Mouse Movement: {sum(mouse_movement):.2f} pixels")

# Usage
tracker = ActivityTracker()
tracker.start()
time.sleep(10)  # Run for 1 hour
tracker.stop()
tracker.plot_data()