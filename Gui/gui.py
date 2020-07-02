import logging
import tkinter as tk

LOGGER = logging.getLogger(__name__)

DEFAULT_WH = 900

class GUI:
    def __init__(self, rows, cols):
        self.draw = True
        self.rows = rows
        self.cols = cols
        self.grid = [[None for _ in range(self.cols)]
                     for _ in range(self.rows)]
        LOGGER.debug(
            'Grid created. Rows: {r}\tCols: {c}'.format(r=rows, c=cols))

    # Create canvas with click and click-drag events and stores as self.c
    def create_canvas(self):
        self.c = tk.Canvas(self.window, width=DEFAULT_WH, height=DEFAULT_WH,
                           borderwidth=5, background='grey')
        self.c.pack()
        self.c.bind('<ButtonPress-1>', self.set_draw)
        self.c.bind('<B1-Motion>', self.callback)

    # Inverts grid[row][col] at x, y and stores in self.draw. Then calls self.callback for click and drag drawing
    def set_draw(self, event):
        row, col = self.get_rc(event.x, event.y)
        if not self.grid[row][col]:
            self.draw = True
        else:
            self.draw = False
        self.callback(event)

    # Creates window with default values and stores reference
    def create_window(self):
        root = tk.Tk()
        root.wm_title('Pathfinding Tool')
        root.config(background = '#FFFFFF')
        self.window = root

    # Creates the top panel within the window
    def top_panel(self):
        self.topFrame = tk.Frame(self.window, width=DEFAULT_WH, height=100)
        self.topFrame.grid(row=0, column=0, padx=10, pady=2)
        tk.Label(self.topFrame, text='Controls:').grid(row=0, column=0, padx=10, pady=2)
        btnFrame = tk.Frame(self.topFrame, width=DEFAULT_WH, height=200)
        btnFrame.grid(row=1, column=0, padx=10, pady=2)
        startBtn = tk.Button(btnFrame, text='Start', command=None)
        startBtn.grid(row=1, column=0, padx=10, pady=2)
        wallBtn = tk.Button(btnFrame, text='Wall', command=None)
        wallBtn.grid(row=1, column=1, padx=10, pady=2)
        endBtn = tk.Button(btnFrame, text='End', command=None)
        endBtn.grid(row=1, column=2, padx=10, pady=2)
        goBtn = tk.Button(btnFrame, text='GO!', command=None)
        goBtn.grid(row=1, column=3, padx=10, pady=2)

    def render(self):
        self.create_window()
        self.top_panel()
        # self.create_canvas()
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

    # Draws/erases rectangles at given x, y coordinates when called as event
    def callback(self, event):
        row, col = self.get_rc(event.x, event.y)

        if not self.grid[row][col] and self.draw:
            self.grid[row][col] = self.draw_rectangle(row, col, color='black')
        elif self.grid[row][col] and not self.draw:
            self.c.delete(self.grid[row][col])
            self.grid[row][col] = None
