import logging
import time
import tkinter as tk
import tkinter.messagebox
import Pathfinders.dijkstra as dijkstra

LOGGER = logging.getLogger(__name__)

DEFAULT_WH = 800
TOPPANEL_H = 100


class GUI:
    def __init__(self, rows, cols):
        self.draw = True
        self.mode = 'wall'
        self.type = 'dijkstra'
        self.start = (-1, -1)
        self.end = (-1, -1)
        self.rows = rows
        self.cols = cols
        self.grid = [[None for _ in range(self.cols)]
                     for _ in range(self.rows)]
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
        self.c = tk.Canvas(self.btmFrame, width=DEFAULT_WH, height=DEFAULT_WH, highlightthickness=0,
                           borderwidth=0, background='grey')
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
                          command=lambda: self.run(self.type))
        goBtn.grid(row=1, column=3, padx=10, pady=2, sticky=tk.W+tk.E)
        self.btnFrame.columnconfigure(3, weight=1)

        self.set_status(row=1, column=4)
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
    def draw_rectangle(self, row, col, width=1, color='black'):
        c_width = self.c.winfo_width()/self.cols
        r_height = self.c.winfo_height()/self.rows

        return self.c.create_rectangle(col*c_width,
                                       row*r_height,
                                       (col+width)*c_width,
                                       (row+width)*r_height,
                                       fill=color)

    # Delete rectangle at given row, col
    def delete_rectangle(self, row, col):
        self.c.delete(self.grid[row][col])
        self.grid[row][col] = None

    # Clear the grid
    def clear_grid(self):
        for row in range(self.rows):
            for col in range(self.cols):
                self.delete_rectangle(row, col)
        LOGGER.debug('Grid cleared!')
        self.start = (-1, -1)
        self.end = (-1, -1)
        LOGGER.debug('Start and End reset')

    # Set the status text
    def set_status(self, row=0, column=0):
        try:
            self.status['text'] = 'Current Mode: {0}'.format(self.mode.upper())
        except AttributeError:
            self.status = tk.Label(
                self.btnFrame, width=25, text='Current Mode: {0}'.format(self.mode.upper()))
            self.status.grid(row=row, column=column, padx=10,
                             pady=2, sticky=tk.W+tk.E)

    # Set the drawing mode (start, end, walls)
    def set_mode(self, mode):
        self.mode = mode
        self.set_status()

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
            self.grid[row][col] = self.draw_rectangle(row, col, color='green')
        elif self.mode == 'end':
            r, c = self.end

            # Prevent deleting bottom right square if (-1,-1)
            if r >= 0 and c >= 0:
                self.delete_rectangle(r, c)

            self.end = (row, col)
            self.delete_rectangle(row, col)
            self.grid[row][col] = self.draw_rectangle(row, col, color='red')

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

    # Main running function
    def run(self, type):
        if self.start == (-1, -1) or self.end == (-1, -1):
            LOGGER.debug('Missing start and/or end points')
            tk.messagebox.showinfo(
                message='Must include a start and end point!')
            return
        alg = dijkstra.dijkstra(self.grid, self.start, self.end)
        while not alg.finished:
            LOGGER.debug('Waiting...')
            time.sleep(1)
        return
