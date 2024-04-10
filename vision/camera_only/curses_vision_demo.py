# From https://www.perplexity.ai/search/write-a-python-ZqWIYEsXTJiLiru0F7XzIg

import cv2
import curses
import time
import numpy as np
import queue
import threading
import sys

colors = [
        (curses.COLOR_BLACK,   (  0,   0,   0)),
        (curses.COLOR_RED,     (255,   0,   0)), 
        (curses.COLOR_GREEN,   (  0, 255,   0)), 
        (curses.COLOR_YELLOW,  (255, 255,   0)), 
        (curses.COLOR_BLUE,    (  0,   0, 255)), 
        (curses.COLOR_MAGENTA, (255,   0, 255)), 
        (curses.COLOR_CYAN,    (  0, 255, 255)), 
        (curses.COLOR_WHITE,   (255, 255, 255))
]


def video_capture(image_queue, port: int):
    cap = cv2.VideoCapture(port)
    while True:
        ret, frame = cap.read()
        image_queue.put(frame)


def video_display(image_queue, stdscr):
    # Get the screen dimensions
    height, width = stdscr.getmaxyx()

    # Create a window to display the webcam feed
    win = curses.newwin(height, width, 0, 0)

    for i, color in enumerate(colors):
        if i > 0:
            curses.init_pair(i, curses.COLOR_BLACK, color[0])

    while True:
        frame = image_queue.get()
        while not image_queue.empty():
            frame = image_queue.get()
        frame = cv2.resize(frame, (width, height))

        for y in range(height - 1):
            for x in range(width):
                win.addch(y, x, '.', curses.color_pair(color_from(frame[y, x]))) 

        # Refresh the window
        win.refresh()


def main(stdscr):
    image_queue = queue.Queue()
    capture_thread = threading.Thread(target=video_capture, args=(image_queue, 0))
    display_thread = threading.Thread(target=video_display, args=(image_queue, stdscr))
    capture_thread.daemon = True
    display_thread.daemon = True
    capture_thread.start()
    display_thread.start()

    while True:
        try:
            time.sleep(1)
        except KeyboardInterrupt:
            sys.exit(0)
    

def euclidean_distance(a, b):
    assert len(a) == len(b)
    return sum((a[i] - b[i])**2 for i in range(len(a)))

def color_from(triple):
    best = None
    best_dist = None
    for i, (color, codes) in enumerate(colors):
        dist = euclidean_distance(codes, triple)
        if best_dist is None or dist < best_dist:
            best = i
            best_dist = dist
    return best

if __name__ == "__main__":
    # Initialize the curses screen
    curses.wrapper(main)
