import logging
import time
from colour import Color
import tkinter as tk
import tkinter.messagebox
import Pathfinders.dijkstra as dijkstra
import threading

LOGGER = logging.getLogger(__name__)

DEFAULT_WH = 800
TOPPANEL_H = 100
TIMEOUT = 60


class GUI:
    def __init__(self, rows, cols):
        self.draw = True
        self.mode = 'wall'
        self.algorithm = 'dijkstra'
        self.status = ''
        self.start = (-1, -1)
        self.end = (-1, -1)
        self.rows = rows
        self.cols = cols
        self.grid = [[None for _ in range(self.cols)]
                     for _ in range(self.rows)]
        self.line = []
        LOGGER.debug(
            'Grid created. Rows: {r}\tCols: {c}'.format(r=rows, c=cols))

    # Creates window with default values and stores reference
    def create_window(self):
        root = tk.Tk()
        root.wm_title('Pathfinding Tool')
        root.config(background='#FFFFFF')
        self.window = root

    # Create canvas with click and click-drag events and stores as self.c
    def create_canvas(self, frame, row=0, column=0):
        self.c = tk.Canvas(self.btmFrame, width=DEFAULT_WH, height=DEFAULT_WH,
                           highlightthickness=0, borderwidth=0, background='grey')
        self.c.grid(row=row, column=column, padx=5, pady=5)
        self.c.bind('<ButtonPress-1>', self.set_draw)
        self.c.bind('<B1-Motion>', self.callback)

    def create_buttons(self, frame):
        self.btnFrame = tk.Frame(frame, width=DEFAULT_WH, height=200)
        self.btnFrame.grid(row=1, column=0, padx=10, pady=2, sticky=tk.W+tk.E)

        startBtn = tk.Button(self.btnFrame, text='Start',
                             command=lambda: self.set_mode('start'))
        startBtn.grid(row=1, column=0, padx=10, pady=2, sticky=tk.W+tk.E)
        self.btnFrame.columnconfigure(0, weight=1)

        wallBtn = tk.Button(self.btnFrame, text='Wall',
                            command=lambda: self.set_mode('wall'))
        wallBtn.grid(row=1, column=1, padx=10, pady=2, sticky=tk.W+tk.E)
        self.btnFrame.columnconfigure(1, weight=1)

        endBtn = tk.Button(self.btnFrame, text='End',
                           command=lambda: self.set_mode('end'))
        endBtn.grid(row=1, column=2, padx=10, pady=2, sticky=tk.W+tk.E)
        self.btnFrame.columnconfigure(2, weight=1)

        goBtn = tk.Button(self.btnFrame, text='GO!',
                          command=lambda: self.run(self.algorithm))
        goBtn.grid(row=1, column=3, padx=10, pady=2, sticky=tk.W+tk.E)
        self.btnFrame.columnconfigure(3, weight=1)

        self.set_mode_text(row=1, column=4)
        self.btnFrame.columnconfigure(4, weight=5)

        clearBtn = tk.Button(self.btnFrame, text='Clear Grid',
                             command=lambda: self.clear_grid())
        clearBtn.grid(row=1, column=5, padx=10, pady=2, sticky=tk.W+tk.E)
        self.btnFrame.columnconfigure(5, weight=1)

    # Creates the top panel within the window
    def top_panel(self):
        self.topFrame = tk.Frame(
            self.window, width=DEFAULT_WH, height=TOPPANEL_H)
        self.topFrame.grid(row=0, column=0, sticky=tk.W+tk.E)
        self.topFrame.columnconfigure(0, weight=1)
        self.create_buttons(self.topFrame)

    # Creates the bottom panel (canvas) within the window
    def bottom_panel(self):
        self.btmFrame = tk.Frame(
            self.window, width=DEFAULT_WH, height=(DEFAULT_WH-TOPPANEL_H))
        self.btmFrame.grid(row=1, column=0)
        self.create_canvas(self.btmFrame)

    def render(self):
        self.create_window()
        self.top_panel()
        self.bottom_panel()
        LOGGER.debug('Launching...')
        self.window.mainloop()

    # Returns row, col for the mouse x, y coord
    def get_rc(self, x, y):
        c_width = self.c.winfo_width()/self.cols
        r_height = self.c.winfo_height()/self.rows
        col = int(x//c_width)
        row = int(y//r_height)
        return row, col

    # Draw a rectangle with given color
    def draw_rectangle(self, row, col, color='black', border=1):
        c_width = self.c.winfo_width()/self.cols
        r_height = self.c.winfo_height()/self.rows

        return self.c.create_rectangle(col*c_width,
                                       row*r_height,
                                       (col+1)*c_width,
                                       (row+1)*r_height,
                                       fill=color, width=border)

    # Draw SPT line
    def draw_line(self, start, end, color='black', width=1):
        c_width = self.c.winfo_width()/self.cols
        r_height = self.c.winfo_height()/self.rows

        return self.c.create_line(start[1]*c_width + .5*c_width, start[0]*r_height + .5*r_height, end[1]*c_width + .5*c_width, end[0]*r_height + .5*r_height, fill=color, width=width)

    # Delete rectangle at given row, col
    def delete_rectangle(self, row, col):
        self.c.delete(self.grid[row][col])
        self.grid[row][col] = None

    # Delete line at given index
    def delete_line(self, index):
        self.c.delete(self.line[index])
        self.line.pop(index)

    # Clear the grid
    def clear_grid(self):
        for row in range(self.rows):
            for col in range(self.cols):
                self.delete_rectangle(row, col)
        for i in reversed(range(len(self.line))):
            self.delete_line(i)

        LOGGER.debug('Grid cleared!')
        self.start = (-1, -1)
        self.end = (-1, -1)
        LOGGER.debug('Start and End reset')

    # Set the mode_text text
    def set_mode_text(self, row=0, column=0):
        try:
            self.mode_text['text'] = 'Current Mode: {0}'.format(
                self.mode.upper())
        except AttributeError:
            self.mode_text = tk.Label(
                self.btnFrame, width=25, text='Current Mode: {0}'.format(self.mode.upper()))
            self.mode_text.grid(row=row, column=column, padx=10,
                                pady=2, sticky=tk.W+tk.E)

    # Set the drawing mode (start, end, walls)
    def set_mode(self, mode):
        self.mode = mode
        self.set_mode_text()

    # Inverts grid[row][col] at x, y and stores in self.draw. Then calls self.callback for click and drag drawing
    def set_draw(self, event):
        row, col = self.get_rc(event.x, event.y)

        if self.mode == 'wall':
            if not self.grid[row][col]:
                self.draw = True
            else:
                self.draw = False
            self.callback(event)
        elif self.mode == 'start':
            r, c = self.start

            # Prevent deleting bottom right square if (-1,-1)
            if r >= 0 and c >= 0:
                self.delete_rectangle(r, c)

            self.start = (row, col)
            self.delete_rectangle(row, col)
            self.grid[row][col] = self.draw_rectangle(
                row, col, color='green', border=3)
        elif self.mode == 'end':
            r, c = self.end

            # Prevent deleting bottom right square if (-1,-1)
            if r >= 0 and c >= 0:
                self.delete_rectangle(r, c)

            self.end = (row, col)
            self.delete_rectangle(row, col)
            self.grid[row][col] = self.draw_rectangle(
                row, col, color='red', border=3)

    # Draws/erases rectangles at given x, y coordinates when called as event
    def callback(self, event):
        if self.mode != 'wall':
            return

        row, col = self.get_rc(event.x, event.y)

        # If mouse goes out of bounds, prevent error spam in logs
        if len(self.grid) <= row or len(self.grid[0]) <= col or row < 0 or col < 0:
            return
        # If (row, col) is start or end point, skip
        if (row, col) == self.start or (row, col) == self.end:
            return

        if not self.grid[row][col] and self.draw:
            self.grid[row][col] = self.draw_rectangle(row, col, color='black')
        elif self.grid[row][col] and not self.draw:
            self.delete_rectangle(row, col)

    # Test function for dijkstra
    def run_dijkstra(self):
        alg = dijkstra.Dijkstra(self.grid, self.start, self.end)

        alg.dijkstra()

        # Use alg.max_step if valid path, else use alg.max_step+1 to account for walls
        max_step = alg.max_step if alg.finished else alg.max_step + 1

        green = Color('green')
        colors = list(green.range_to(Color('red'), max_step))

        self.status = 'Drawing'

        for step in range(1, max_step):
            for r, c in alg.steps[step]:
                if (r, c) != self.end:
                    self.grid[r][c] = self.draw_rectangle(
                        r, c, color=colors[step])
            time.sleep(.5)
            LOGGER.debug('Drew step: {}'.format(step))

        current_step = self.start
        for next_step in alg.spt:
            self.line.append(self.draw_line(current_step, next_step, width=2))
            current_step = next_step

        self.status = 'Finished' if alg.finished else 'No Path'

    def check_dijkstra(self):
        if alg_thread.is_alive():
            self.window.after(20, self.check_dijkstra)
        else:
            tk.messagebox.showinfo(
                message='Algorithm finished!'
            )

    # Main running function
    def run(self, algorithm):
        # Check if start and end are assigned
        if self.start == (-1, -1) or self.end == (-1, -1):
            LOGGER.debug('Missing start and/or end points')
            tk.messagebox.showinfo(
                message='Must include a start and end point!')
            return

        global alg_thread

        if algorithm == 'dijkstra':
            alg_thread = threading.Thread(target=self.run_dijkstra)
            alg_thread.daemon = True
            alg_thread.start()
            self.window.after(20, self.check_dijkstra)

        return
