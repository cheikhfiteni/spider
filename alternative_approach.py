import sqlite3
import pynput
import time
from collections import defaultdict
from typing import List, Dict, Tuple
import matplotlib.pyplot as plt

MOUSE_MOVE_DEBOUNCE_SECONDS = 0.5
BUFFER_FLUSH_TIME_SECONDS = 1
class ActivityTracker:
    def __init__(self, db_path='activity_tracker.db'):
        self.mouse_listener = pynput.mouse.Listener(on_move=self.on_move, on_click=self.on_click)
        self.keyboard_listener = pynput.keyboard.Listener(on_press=self.on_press)
        self.start_time = time.time()
        self.last_position = None
        self.last_move_time = None

        self.db_path = db_path
        self.setup_database()
        self.buffer = defaultdict(lambda: {'left_clicks': 0, 'right_clicks': 0, 'middle_clicks': 0, 'keypresses': 0, 'mouse_movement': 0, 'mouse_movement_distance': 0,})
        self.last_flush_time = time.time()
    
    def setup_database(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS activity_data (
                        timestamp INTEGER PRIMARY KEY,
                        left_clicks INTEGER,
                        right_clicks INTEGER,
                        middle_clicks INTEGER,
                        keypresses INTEGER,
                        mouse_movement INTEGER,
                        mouse_movement_distance REAL
                    )
                ''')

    def flush_buffer(self):
        current_time = time.time()
        if current_time - self.last_flush_time >= BUFFER_FLUSH_TIME_SECONDS:
            aggregated_data = defaultdict(lambda: {'left_clicks': 0, 'right_clicks': 0, 'middle_clicks': 0, 'keypresses': 0, 'mouse_movement': 0, 'mouse_movement_distance': 0})

            for timestamp, data in self.buffer.items():
                chunk_timestamp = (timestamp // BUFFER_FLUSH_TIME_SECONDS) * BUFFER_FLUSH_TIME_SECONDS
                for key, value in data.items():
                    aggregated_data[chunk_timestamp][key] += value

            with sqlite3.connect(self.db_path) as conn:
                for timestamp, data in aggregated_data.items():
                    conn.execute('''
                        INSERT OR REPLACE INTO activity_data
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    ''', (timestamp, data['left_clicks'], data['right_clicks'], data['middle_clicks'],
                          data['keypresses'], data['mouse_movement'], data['mouse_movement_distance']))
            self.buffer.clear()
            self.last_flush_time = current_time

    def on_move(self, x, y):
        current_time = time.time()
        if self.last_move_time is None or current_time - self.last_move_time >= MOUSE_MOVE_DEBOUNCE_SECONDS:
            if self.last_position:
                dx, dy = x - self.last_position[0], y - self.last_position[1]
                distance = (dx**2 + dy**2)**0.5
                self.buffer[int(current_time - self.start_time)]['mouse_movement'] += 1
                self.buffer[int(current_time - self.start_time)]['mouse_movement_distance'] += distance
            self.last_position = (x, y)
            self.last_move_time = current_time
            self.flush_buffer()

    def on_click(self, x, y, button, pressed):
        if pressed:
            if button == pynput.mouse.Button.left:
                self.buffer[int(time.time() - self.start_time)]['left_clicks'] += 1
            elif button == pynput.mouse.Button.right:
                self.buffer[int(time.time() - self.start_time)]['right_clicks'] += 1
            elif button == pynput.mouse.Button.middle:
                self.buffer[int(time.time() - self.start_time)]['middle_clicks'] += 1
            self.flush_buffer()

    def on_press(self, key):
        self.buffer[int(time.time() - self.start_time)]['keypresses'] += 1
        self.flush_buffer()

    def start(self):
        self.mouse_listener.start()
        self.keyboard_listener.start()

    def stop(self):
        self.mouse_listener.stop()
        self.keyboard_listener.stop()

    @staticmethod
    def format_data(data: List[Tuple[int, int, int, int, int, int, float]]) -> Dict[int, Dict[str, float]]:
        formatted_data: Dict[int, Dict[str, float]] = {}
        for row in data:
            timestamp, left_clicks, right_clicks, middle_clicks, keypresses, mouse_movement, mouse_movement_distance = row
            formatted_data[timestamp] = {
                'left_clicks': float(left_clicks),
                'right_clicks': float(right_clicks),
                'middle_clicks': float(middle_clicks),
                'keypresses': float(keypresses),
                'mouse_movement': float(mouse_movement),
                'mouse_movement_distance': mouse_movement_distance
            }
        return formatted_data

    def plot_data(self):

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM activity_data ORDER BY timestamp')
            data = cursor.fetchall()

        formatted_data = ActivityTracker.format_data(data)
        times = list(formatted_data.keys())
        left_clicks = [d['left_clicks'] for d in formatted_data.values()]
        right_clicks = [d['right_clicks'] for d in formatted_data.values()]
        middle_clicks = [d['middle_clicks'] for d in formatted_data.values()]
        keypresses = [d['keypresses'] for d in formatted_data.values()]
        mouse_movement = [d['mouse_movement'] for d in formatted_data.values()]

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

        print(f"Total Left Clicks: {sum(left_clicks)}")
        print(f"Total Right Clicks: {sum(right_clicks)}")
        print(f"Total Middle Clicks: {sum(middle_clicks)}")
        print(f"Total Keypresses: {sum(keypresses)}")
        print(f"Total Mouse Movement: {sum(mouse_movement):.2f} pixels")

        plt.show()

# Usage
if __name__ == "__main__":
    tracker = ActivityTracker()
    tracker.start()
    time.sleep(15) 
    tracker.stop()
    tracker.plot_data()