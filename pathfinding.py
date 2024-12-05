import tkinter as tk
from collections import deque
import tkinter.font as font

EMPTY = ' '
OBSTACLE = 'X'
START = 'S'
END = 'E'
PATH = '-'

class GridApp:
    def __init__(self, rows, cols):
        self.root = tk.Tk()
        self.root.title("Grid Solving and Optimization Tool")
        self.rows = rows
        self.cols = cols
        self.cell_size = 40
        self.grid_state = [[EMPTY for _ in range(cols)] for _ in range(rows)]
        self.start_pos = None
        self.end_pos = None
        self.current_mode = None
        self.canvas = None
        self.create_canvas()
        self.create_menu()

    def create_canvas(self):
        self.canvas = tk.Canvas(self.root, width=self.cols * self.cell_size, height=self.rows * self.cell_size)
        self.canvas.pack()
        self.draw_grid()
        self.canvas.bind("<Button-1>", self.on_canvas_click)

    def draw_grid(self):
        for r in range(self.rows):
            for c in range(self.cols):
                x1 = c * self.cell_size
                y1 = r * self.cell_size
                x2 = x1 + self.cell_size
                y2 = y1 + self.cell_size
                self.canvas.create_rectangle(x1, y1, x2, y2, fill='white', outline='black')
                self.draw_cell_content(r, c)

    def draw_cell_content(self, r, c):
        cell_content = self.grid_state[r][c]
        x = c * self.cell_size + self.cell_size // 2
        y = r * self.cell_size + self.cell_size // 2
        if cell_content == START:
            self.canvas.itemconfig(self.canvas.find_closest(x, y), fill='green')
            self.canvas.create_text(x, y, text='S', fill='red', font=("Arial", 12, "bold"))
        elif cell_content == END:
            self.canvas.itemconfig(self.canvas.find_closest(x, y), fill='red')
            self.canvas.create_text(x, y, text='E', fill='black', font=("Arial", 12, "bold"))
        elif cell_content == OBSTACLE:
            self.canvas.itemconfig(self.canvas.find_closest(x, y), fill='black')
        elif cell_content == PATH:
            self.canvas.itemconfig(self.canvas.find_closest(x, y), fill='green')
            self.canvas.create_text(x, y, text='-', fill='black', font=("Arial", 12, "bold"))

    def create_menu(self):
        menu_bar = tk.Menu(self.root)
        self.root.config(menu=menu_bar)
        
        set_menu = tk.Menu(menu_bar, tearoff=0)
        menu_bar.add_cascade(label="Set", menu=set_menu)
        set_menu.add_command(label="Set Start", command=lambda: self.set_mode('start'))
        set_menu.add_command(label="Set End", command=lambda: self.set_mode('end'))
        set_menu.add_command(label="Set Obstacle", command=lambda: self.set_mode('obstacle'))
        
        algorithm_menu = tk.Menu(menu_bar, tearoff=0)
        menu_bar.add_cascade(label="Run Algorithm", menu=algorithm_menu)
        algorithm_menu.add_command(label="BFS", command=lambda: self.run_algorithm('bfs'))
        algorithm_menu.add_command(label="DFS", command=lambda: self.run_algorithm('dfs'))
        algorithm_menu.add_command(label="A*", command=lambda: self.run_algorithm('a_star'))
        
        reset_menu = tk.Menu(menu_bar, tearoff=0)
        menu_bar.add_cascade(label="Reset", menu=reset_menu)
        reset_menu.add_command(label="Reset Path", command=self.reset_path)
        
        menu_bar.add_command(label="Exit", command=self.exit_app)

    def set_mode(self, mode):
        self.current_mode = mode

    def on_canvas_click(self, event):
        c = event.x // self.cell_size
        r = event.y // self.cell_size
        self.on_cell_click(r, c)

    def on_cell_click(self, r, c):
        if not (0 <= r < self.rows and 0 <= c < self.cols):
            return
        if self.current_mode == 'start':
            if self.grid_state[r][c] in [OBSTACLE, END]:
                return
            if self.start_pos:
                prev_r, prev_c = self.start_pos
                self.grid_state[prev_r][prev_c] = EMPTY
                self.draw_cell_content(prev_r, prev_c)
            self.grid_state[r][c] = START
            self.draw_cell_content(r, c)
            self.start_pos = (r, c)
        elif self.current_mode == 'end':
            if self.grid_state[r][c] in [OBSTACLE, START]:
                return
            if self.end_pos:
                prev_r, prev_c = self.end_pos
                self.grid_state[prev_r][prev_c] = EMPTY
                self.draw_cell_content(prev_r, prev_c)
            self.grid_state[r][c] = END
            self.draw_cell_content(r, c)
            self.end_pos = (r, c)
        elif self.current_mode == 'obstacle':
            if self.grid_state[r][c] in [START, END]:
                return
            self.grid_state[r][c] = OBSTACLE
            self.draw_cell_content(r, c)

    def reset_path(self):
        for r in range(self.rows):
            for c in range(self.cols):
                if self.grid_state[r][c] == PATH:
                    self.grid_state[r][c] = EMPTY
                    self.draw_cell_content(r, c)

    def exit_app(self):
        self.root.quit()

    def run_algorithm(self, algorithm):
        if not self.start_pos or not self.end_pos:
            return
        if algorithm == 'bfs':
            path = self.bfs(self.grid_state, self.start_pos, self.end_pos, self.rows, self.cols)
        elif algorithm == 'dfs':
            path = self.dfs(self.grid_state, self.start_pos, self.end_pos, self.rows, self.cols)
        elif algorithm == 'a_star':
            path = self.a_star(self.grid_state, self.start_pos, self.end_pos, self.rows, self.cols)
        else:
            return
        if path:
            self.mark_path(path)
        else:
            print("No path found using selected algorithm.")

    def bfs(self, grid, start, end, rows, cols):
        queue = deque()
        queue.append((start, [start]))
        visited = set()
        visited.add(start)
        while queue:
            current, path = queue.popleft()
            if current == end:
                return path
            for neighbor in self.get_neighbors(current, rows, cols):
                if grid[neighbor[0]][neighbor[1]] != OBSTACLE and neighbor not in visited:
                    visited.add(neighbor)
                    new_path = path + [neighbor]
                    queue.append((neighbor, new_path))
        return None

    def dfs(self, grid, start, end, rows, cols):
        stack = deque()
        stack.append((start, [start]))
        visited = set()
        visited.add(start)
        while stack:
            current, path = stack.pop()
            if current == end:
                return path
            for neighbor in self.get_neighbors(current, rows, cols):
                if grid[neighbor[0]][neighbor[1]] != OBSTACLE and neighbor not in visited:
                    visited.add(neighbor)
                    new_path = path + [neighbor]
                    stack.append((neighbor, new_path))
        return None

    def a_star(self, grid, start, end, rows, cols):
        import heapq
        open_set = []
        heapq.heappush(open_set, (self.heuristic(start, end), start, [start]))
        came_from = {}
        cost_so_far = {}
        came_from[start] = None
        cost_so_far[start] = 0
        while open_set:
            priority, current, path = heapq.heappop(open_set)
            if current == end:
                return path
            for neighbor in self.get_neighbors(current, rows, cols):
                if grid[neighbor[0]][neighbor[1]] == OBSTACLE:
                    continue
                if abs(neighbor[0] - current[0]) + abs(neighbor[1] - current[1]) == 1:
                    move_cost = 1
                else:
                    move_cost = 1.414
                new_cost = cost_so_far[current] + move_cost
                if neighbor not in cost_so_far or new_cost < cost_so_far[neighbor]:
                    cost_so_far[neighbor] = new_cost
                    priority = new_cost + self.heuristic(neighbor, end)
                    heapq.heappush(open_set, (priority, neighbor, path + [neighbor]))
                    came_from[neighbor] = current
        return None

    def get_neighbors(self, pos, rows, cols):
        dirs = [(-1,0),(1,0),(0,-1),(0,1), (-1,-1), (-1,1), (1,-1), (1,1)]
        neighbors = []
        for d in dirs:
            nr = pos[0] + d[0]
            nc = pos[1] + d[1]
            if 0 <= nr < rows and 0 <= nc < cols:
                neighbors.append((nr, nc))
        return neighbors

    def heuristic(self, a, b):
        return max(abs(a[0] - b[0]), abs(a[1] - b[1]))

    def mark_path(self, path):
        if path:
            for pos in path:
                r, c = pos
                if self.grid_state[r][c] not in [START, END]:
                    self.grid_state[r][c] = PATH
                    self.draw_cell_content(r, c)
        else:
            print("No path found.")

def get_grid_dimensions():
    while True:
        input_str = input("Enter grid dimensions (rows cols): ")
        if input_str.strip() == '':
            continue
        parts = input_str.strip().split()
        if len(parts) != 2:
            print("Please enter exactly two integers for rows and columns.")
            continue
        try:
            rows = int(parts[0])
            cols = int(parts[1])
            if rows <= 0 or cols <= 0:
                continue
            return rows, cols
        except ValueError:
            print("Invalid input. Please enter integers for rows and columns.")

def main():
    rows, cols = get_grid_dimensions()
    app = GridApp(rows, cols)
    app.root.mainloop()

if __name__ == "__main__":
    main()