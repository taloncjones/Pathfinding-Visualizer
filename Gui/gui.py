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

    def set_master(self, master):
        self.master = master

    def set_canvas(self):
        self.c = tk.Canvas(self.master, width=DEFAULT_WH, height=DEFAULT_WH,
                           borderwidth=5, background='grey')
        self.c.pack()
        self.c.bind('<ButtonPress-1>', self.set_draw)
        self.c.bind('<B1-Motion>', self.callback)
        self.c.bind('<ButtonRelease-1>', self.callback)

    def set_draw(self, event):
        row, col = self.get_rc(event.x, event.y)
        if not self.grid[row][col]:
            self.draw = True
        else:
            self.draw = False

    def render(self):
        root = tk.Tk()
        self.set_master(root)
        self.set_canvas()
        LOGGER.debug('Launching...')
        root.mainloop()

    def get_rc(self, x, y):
        c_width = self.c.winfo_width()/self.cols
        r_height = self.c.winfo_height()/self.rows
        col = int(x//c_width)
        row = int(y//r_height)
        return row, col

    def callback(self, event):
        c_width = self.c.winfo_width()/self.cols
        r_height = self.c.winfo_height()/self.rows

        row, col = self.get_rc(event.x, event.y)

        if not self.grid[row][col] and self.draw:
            self.grid[row][col] = self.c.create_rectangle(
                col*c_width, row*r_height, (col+1)*c_width, (row+1)*r_height, fill='black')
        elif self.grid[row][col] and not self.draw:
            self.c.delete(self.grid[row][col])
            self.grid[row][col] = None
