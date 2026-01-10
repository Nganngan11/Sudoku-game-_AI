import tkinter as tk
from tkinter import ttk, messagebox
import time
import copy
import random
import json
import os
from datetime import datetime

# ====== MODERN COLOR PALETTE ======
BG_MAIN = "#f1f5f9"
BG_CARD = "#ffffff"
PRIMARY = "#4f46e5"
PRIMARY_HOVER = "#4338ca"
TEXT_DARK = "#1e293b"
TEXT_MUTE = "#64748b"
ACCENT = "#10b981"
ERROR_COLOR = "#ef4444" 
BORDER = "#e2e8f0"

class SudokuApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Ultimate Multi-Size Sudoku")
        self.geometry("1200x850")
        self.configure(bg=BG_MAIN)

        self.grid_size = 9
        self.sub_rows = 3
        self.sub_cols = 3
        self.difficulty_level = 1
        self.hints_left = 3
        self.mistakes = 0
        self.max_mistakes = 5
        self.player_name = ""
        self.current_puzzle = None
        self.solution = None
        self.player_entries = []
        self.start_time = 0
        self.timer_running = False
        
        self.scores_file = "scores.json"
        self.setup_styles()

        container = tk.Frame(self, bg=BG_MAIN)
        container.pack(fill="both", expand=True)
        
        self.frames = {}
        # REGISTER ALL PAGES
        for F in (StartPage, DifficultyPage, GamePage, ResultPage, RulesPage, LeaderboardPage):
            frame = F(container, self)
            self.frames[F] = frame
            frame.grid(row=0, column=0, sticky="nsew")
        
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.show_frame(StartPage)

    def setup_styles(self):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Main.TButton", font=("Segoe UI", 11, "bold"), background=PRIMARY, foreground="white", padding=12, borderwidth=0)
        style.map("Main.TButton", background=[("active", PRIMARY_HOVER)])
        style.configure("Secondary.TButton", font=("Segoe UI", 11), background=BG_CARD, foreground=TEXT_DARK, padding=10)

    def show_frame(self, cont):
        frame = self.frames[cont]
        frame.tkraise()
        if hasattr(frame, 'on_show'):
            frame.on_show()

    def load_scores(self):
        if not os.path.exists(self.scores_file):
            return []
        try:
            with open(self.scores_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []

    def save_score(self, completion_time):
        try:
            diff_map = {1: "Easy", 2: "Medium", 3: "Hard", 4: "Insane"}
            new_score = {
                "player": self.player_name,
                "grid": f"{self.grid_size}x{self.grid_size}",
                "difficulty": diff_map.get(self.difficulty_level, "Unknown"),
                "time_seconds": completion_time,
                "date": datetime.now().strftime("%Y-%m-%d %H:%M")
            }
            scores = self.load_scores()
            scores.append(new_score)
            with open(self.scores_file, "w", encoding="utf-8") as f:
                json.dump(scores, f, indent=4)
        except Exception as e:
            print(f"Error saving score: {e}")

    def is_valid(self, board, row, col, num, size, s_rows, s_cols):
        for x in range(size):
            if board[row][x] == num or board[x][col] == num: return False
        sr, sc = (row // s_rows) * s_rows, (col // s_cols) * s_cols
        for i in range(s_rows):
            for j in range(s_cols):
                if board[sr + i][sc + j] == num: return False
        return True

    def solve(self, board, size, s_rows, s_cols):
        for i in range(size):
            for j in range(size):
                if board[i][j] == 0:
                    nums = list(range(1, size + 1))
                    random.shuffle(nums)
                    for num in nums:
                        if self.is_valid(board, i, j, num, size, s_rows, s_cols):
                            board[i][j] = num
                            if self.solve(board, size, s_rows, s_cols): return True
                            board[i][j] = 0
                    return False
        return True

    def generate_puzzle(self):
        size, sr, sc = self.grid_size, self.sub_rows, self.sub_cols
        board = [[0]*size for _ in range(size)]
        self.solve(board, size, sr, sc)
        self.solution = copy.deepcopy(board)
        ratios = {1: 0.35, 2: 0.5, 3: 0.65, 4: 0.8}
        empty_count = int(size*size * ratios.get(self.difficulty_level, 0.5))
        pos = [(r, c) for r in range(size) for c in range(size)]
        random.shuffle(pos)
        for i in range(empty_count): board[pos[i][0]][pos[i][1]] = 0
        self.current_puzzle = board

# ====== UI PAGES ======

class StartPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=BG_MAIN)
        content = tk.Frame(self, bg=BG_MAIN)
        content.place(relx=0.5, rely=0.5, anchor="center")
        tk.Label(content, text="SUDOKU", font=("Segoe UI", 48, "bold"), bg=BG_MAIN, fg=PRIMARY).pack()
        tk.Label(content, text="MASTER EDITION", font=("Segoe UI", 14), bg=BG_MAIN, fg=TEXT_MUTE).pack(pady=(0, 40))
        
        ttk.Button(content, text="START GAME", width=25, style="Main.TButton", command=lambda: controller.show_frame(DifficultyPage)).pack(pady=5)
        ttk.Button(content, text="LEADERBOARD", width=25, style="Secondary.TButton", command=lambda: controller.show_frame(LeaderboardPage)).pack(pady=5)
        ttk.Button(content, text="RULES", width=25, style="Secondary.TButton", command=lambda: controller.show_frame(RulesPage)).pack(pady=5)
        ttk.Button(content, text="EXIT", width=25, style="Secondary.TButton", command=controller.quit).pack(pady=5)

class RulesPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=BG_MAIN)
        card = tk.Frame(self, bg=BG_CARD, padx=40, pady=40, highlightthickness=1, highlightbackground=BORDER)
        card.place(relx=0.5, rely=0.5, anchor="center", width=700)
        
        tk.Label(card, text="How to Play Sudoku", font=("Segoe UI", 24, "bold"), bg=BG_CARD, fg=PRIMARY).pack(pady=(0,20))
        rules_text = (
            "1. The Goal: Fill the grid with numbers correctly.\n"
            "2. Errors: If you enter a wrong number, it counts as 1 mistake.\n"
            "3. Game Over: You lose if you make 5 mistakes.\n"
            "4. Give Up: You can view the full solution at any time.\n"
            "5. Visual Cues: Conflict numbers will turn RED automatically."
        )
        tk.Label(card, text=rules_text, font=("Segoe UI", 12), bg=BG_CARD, justify="left", fg=TEXT_DARK).pack(pady=10)
        ttk.Button(card, text="BACK TO MENU", style="Main.TButton", command=lambda: controller.show_frame(StartPage)).pack(pady=(20,0))

class DifficultyPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=BG_MAIN)
        self.controller = controller
        card = tk.Frame(self, bg=BG_CARD, padx=40, pady=40, highlightthickness=1, highlightbackground=BORDER)
        card.place(relx=0.5, rely=0.5, anchor="center")
        
        tk.Label(card, text="Match Settings", font=("Segoe UI", 24, "bold"), bg=BG_CARD, fg=TEXT_DARK).pack(pady=(0, 30))
        
        tk.Label(card, text="PLAYER NAME", font=("Segoe UI", 9, "bold"), bg=BG_CARD, fg=TEXT_MUTE).pack(anchor="w")
        self.name_ent = tk.Entry(card, font=("Segoe UI", 12), bg=BG_MAIN, bd=0, highlightthickness=1, highlightbackground=BORDER)
        self.name_ent.pack(fill="x", pady=(5, 20), ipady=8)
        
        self.size_var = tk.IntVar(value=9)
        size_f = tk.Frame(card, bg=BG_CARD)
        size_f.pack(pady=(5, 20))
        for s in [3, 6, 9]:
            tk.Radiobutton(size_f, text=f"{s}x{s}", variable=self.size_var, value=s, bg=BG_CARD).pack(side="left", padx=15)
            
        self.diff_var = tk.IntVar(value=1)
        diff_f = tk.Frame(card, bg=BG_CARD)
        diff_f.pack(pady=(5, 30))
        for t, v in [("Easy", 1), ("Medium", 2), ("Hard", 3), ("Insane", 4)]:
            tk.Radiobutton(diff_f, text=t, variable=self.diff_var, value=v, bg=BG_CARD).pack(side="left", padx=10)
            
        ttk.Button(card, text="START GAME", style="Main.TButton", command=self.confirm).pack(fill="x")

    def confirm(self):
        self.controller.player_name = self.name_ent.get() or "Guest"
        self.controller.grid_size = self.size_var.get()
        self.controller.difficulty_level = self.diff_var.get()
        self.controller.hints_left = 3
        self.controller.mistakes = 0
        
        s = self.controller.grid_size
        if s == 3: self.controller.sub_rows, self.controller.sub_cols = 1, 3
        elif s == 6: self.controller.sub_rows, self.controller.sub_cols = 2, 3
        else: self.controller.sub_rows, self.controller.sub_cols = 3, 3
        
        self.controller.generate_puzzle()
        self.controller.start_time = time.time()
        self.controller.show_frame(GamePage)

class GamePage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=BG_MAIN)
        self.controller = controller
        
        header = tk.Frame(self, bg=BG_CARD, height=70, highlightthickness=1, highlightbackground=BORDER)
        header.pack(fill="x", side="top")
        header.pack_propagate(False)
        self.title_lbl = tk.Label(header, text="SUDOKU SESSION", font=("Segoe UI", 16, "bold"), bg=BG_CARD, fg=TEXT_DARK)
        self.title_lbl.pack(side="left", padx=30)
        
        self.main_container = tk.Frame(self, bg=BG_MAIN)
        self.main_container.pack(expand=True, fill="both", padx=40, pady=20)
        
        self.sidebar = tk.Frame(self.main_container, bg=BG_CARD, width=280, padx=25, pady=25, highlightthickness=1, highlightbackground=BORDER)
        self.sidebar.pack(side="right", fill="y", padx=(20, 0))
        self.sidebar.pack_propagate(False)

        tk.Label(self.sidebar, text="TIME ELAPSED", font=("Segoe UI", 9, "bold"), bg=BG_CARD, fg=TEXT_MUTE).pack(anchor="w")
        self.timer_lbl = tk.Label(self.sidebar, text="00:00", font=("Consolas", 24, "bold"), bg=BG_CARD, fg=PRIMARY)
        self.timer_lbl.pack(anchor="w", pady=(0, 15))

        tk.Label(self.sidebar, text="MISTAKES", font=("Segoe UI", 9, "bold"), bg=BG_CARD, fg=TEXT_MUTE).pack(anchor="w")
        self.mistake_lbl = tk.Label(self.sidebar, text="0 / 5", font=("Segoe UI", 18, "bold"), bg=BG_CARD, fg=ERROR_COLOR)
        self.mistake_lbl.pack(anchor="w", pady=(0, 20))

        self.info_lbl = tk.Label(self.sidebar, text="", font=("Segoe UI", 11), bg=BG_CARD, justify="left")
        self.info_lbl.pack(anchor="w", pady=(0, 30))
        
        ttk.Button(self.sidebar, text="💡 USE HINT", style="Secondary.TButton", command=self.use_hint).pack(fill="x", pady=5)
        ttk.Button(self.sidebar, text="🏳️ GIVE UP", style="Secondary.TButton", command=self.give_up).pack(fill="x", pady=5)
        ttk.Button(self.sidebar, text="✅ SUBMIT", style="Main.TButton", command=self.check_result).pack(fill="x", pady=(20, 5))
        ttk.Button(self.sidebar, text="QUIT", style="Secondary.TButton", command=self.exit_game).pack(fill="x", pady=5)

        self.canvas_frame = tk.Frame(self.main_container, bg=BG_MAIN)
        self.canvas_frame.pack(side="left", expand=True)
        self.canvas = None

    def on_show(self):
        self.controller.timer_running = True
        self.draw_grid()
        self.update_info()
        self.update_timer()

    def update_timer(self):
        if self.controller.timer_running:
            elapsed = int(time.time() - self.controller.start_time)
            mins, secs = divmod(elapsed, 60)
            self.timer_lbl.config(text=f"{mins:02d}:{secs:02d}")
            self.after(1000, self.update_timer)

    def update_info(self):
        self.mistake_lbl.config(text=f"{self.controller.mistakes} / {self.controller.max_mistakes}")
        self.info_lbl.config(text=f"PLAYER: {self.controller.player_name}\n"
                                  f"MODE: {self.controller.grid_size}x{self.controller.grid_size}\n"
                                  f"HINTS: {self.controller.hints_left} Left")

    def draw_grid(self):
        if self.canvas: self.canvas.destroy()
        size = self.controller.grid_size
        canvas_w = 600
        cell_size = canvas_w // size
        self.canvas = tk.Canvas(self.canvas_frame, width=canvas_w, height=canvas_w, bg="white", highlightthickness=2, highlightbackground=TEXT_DARK)
        self.canvas.pack()
        
        self.controller.player_entries = []
        puzzle = self.controller.current_puzzle
        sr, sc = self.controller.sub_rows, self.controller.sub_cols
        
        for r in range(size):
            for c in range(size):
                x1, y1 = c * cell_size, r * cell_size
                x2, y2 = x1 + cell_size, y1 + cell_size
                mid_x, mid_y = (x1 + x2)/2, (y1 + y2)/2
                
                if puzzle[r][c] != 0:
                    self.canvas.create_rectangle(x1, y1, x2, y2, outline=BORDER, fill="#fdfdfd")
                    self.canvas.create_text(mid_x, mid_y, text=str(puzzle[r][c]), font=("Segoe UI", int(20*(9/size)), "bold"), fill=TEXT_DARK)
                else:
                    entry = tk.Entry(self.canvas, font=("Segoe UI", int(18*(9/size))), justify="center", bd=0, bg="#f8fafc", fg=PRIMARY)
                    self.canvas.create_window(mid_x, mid_y, window=entry, width=cell_size-4, height=cell_size-4)
                    entry.bind("<KeyRelease>", lambda e, row=r, col=c, ent=entry: self.handle_input(e, row, col, ent))
                    self.controller.player_entries.append((r, c, entry))
                    
        for i in range(size + 1):
            lw = 3 if i % sc == 0 else 1
            self.canvas.create_line(i * cell_size, 0, i * cell_size, canvas_w, width=lw)
            lw = 3 if i % sr == 0 else 1
            self.canvas.create_line(0, i * cell_size, canvas_w, i * cell_size, width=lw)

    def handle_input(self, event, r, c, ent):
        val = ent.get().strip()
        if not val: return
        if not val.isdigit():
            ent.delete(0, tk.END)
            return

        # Mistake detection logic
        if int(val) != self.controller.solution[r][c]:
            self.controller.mistakes += 1
            ent.config(fg=ERROR_COLOR)
            self.update_info()
            if self.controller.mistakes >= self.controller.max_mistakes:
                self.game_over_loss()
        else:
            ent.config(fg=PRIMARY)
            
        self.validate_grid()

    def game_over_loss(self):
        self.controller.timer_running = False
        messagebox.showerror("GAME OVER", "You've made 5 mistakes! Better luck next time.")
        self.controller.show_frame(StartPage)

    def give_up(self):
        if messagebox.askyesno("Confirm", "Are you sure you want to give up and see the solution?"):
            self.controller.timer_running = False
            for r, c, ent in self.controller.player_entries:
                sol = self.controller.solution[r][c]
                ent.delete(0, tk.END)
                ent.insert(0, str(sol))
                ent.config(state="readonly", fg=ACCENT)
            messagebox.showinfo("Given Up", "The complete solution is now displayed.")

    def validate_grid(self):
        size = self.controller.grid_size
        sr, sc = self.controller.sub_rows, self.controller.sub_cols
        current_data = copy.deepcopy(self.controller.current_puzzle)
        
        for r, c, ent in self.controller.player_entries:
            val = ent.get().strip()
            current_data[r][c] = int(val) if (val.isdigit() and 0 < int(val) <= size) else 0

        for r, c, ent in self.controller.player_entries:
            val = current_data[r][c]
            if val == 0: continue
            
            is_err = False
            if current_data[r].count(val) > 1: is_err = True
            if [current_data[i][c] for i in range(size)].count(val) > 1: is_err = True
            
            box_r, box_c = (r // sr) * sr, (c // sc) * sc
            subgrid = [current_data[box_r+i][box_c+j] for i in range(sr) for j in range(sc)]
            if subgrid.count(val) > 1: is_err = True
            
            # Highlight incorrect entries in red
            if val != self.controller.solution[r][c]: is_err = True
            ent.config(fg=ERROR_COLOR if is_err else PRIMARY)

    def use_hint(self):
        if self.controller.hints_left <= 0: return
        empty_or_wrong = [(r, c, e) for r, c, e in self.controller.player_entries if e.get() != str(self.controller.solution[r][c])]
        if empty_or_wrong:
            r, c, ent = random.choice(empty_or_wrong)
            ent.delete(0, tk.END)
            ent.insert(0, str(self.controller.solution[r][c]))
            ent.config(fg=ACCENT)
            self.controller.hints_left -= 1
            self.validate_grid()
            self.update_info()

    def check_result(self):
        correct = True
        for r, c, ent in self.controller.player_entries:
            val = ent.get().strip()
            if not val or int(val) != self.controller.solution[r][c]:
                correct = False
                break

        if correct:
            self.controller.timer_running = False
            elapsed = int(time.time() - self.controller.start_time)
            self.controller.save_score(elapsed)
            messagebox.showinfo("VICTORY", f"Fantastic! You solved it in {elapsed} seconds.")
            self.controller.show_frame(ResultPage)
        else:
            messagebox.showwarning("Incomplete", "The grid is not yet complete or has errors!")

    def exit_game(self):
        self.controller.timer_running = False
        self.controller.show_frame(StartPage)

class LeaderboardPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=BG_MAIN)
        self.controller = controller
        card = tk.Frame(self, bg=BG_CARD, padx=30, pady=30, highlightthickness=1, highlightbackground=BORDER)
        card.place(relx=0.5, rely=0.5, anchor="center", width=850, height=650)

        tk.Label(card, text="🏆 LEADERBOARD", font=("Segoe UI", 28, "bold"), bg=BG_CARD, fg=PRIMARY).pack(pady=(0, 20))

        self.tree = ttk.Treeview(card, columns=("Name", "Grid", "Difficulty", "Time", "Date"), show="headings", height=12)
        for col, text in [("Name", "PLAYER"), ("Grid", "SIZE"), ("Difficulty", "LEVEL"), ("Time", "TIME"), ("Date", "DATE")]:
            self.tree.heading(col, text=text)
            self.tree.column(col, anchor="center", width=120)
        self.tree.pack(fill="both", expand=True)

        btn_f = tk.Frame(card, bg=BG_CARD)
        btn_f.pack(pady=20)
        ttk.Button(btn_f, text="BACK TO MENU", style="Main.TButton", command=lambda: controller.show_frame(StartPage)).pack(side="left", padx=10)
        ttk.Button(btn_f, text="CLEAR ALL", style="Secondary.TButton", command=self.clear_scores).pack(side="left", padx=10)

    def on_show(self):
        for item in self.tree.get_children(): self.tree.delete(item)
        scores = self.controller.load_scores()
        scores.sort(key=lambda x: x.get("time_seconds", 999999))
        for s in scores[:15]:
            m, sec = divmod(s['time_seconds'], 60)
            self.tree.insert("", "end", values=(s['player'], s['grid'], s['difficulty'], f"{m:02d}:{sec:02d}", s['date']))

    def clear_scores(self):
        if messagebox.askyesno("Confirm", "Are you sure you want to clear all high scores?"):
            if os.path.exists(self.controller.scores_file): os.remove(self.controller.scores_file)
            self.on_show()

class ResultPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=BG_MAIN)
        self.controller = controller
        content = tk.Frame(self, bg=BG_MAIN)
        content.place(relx=0.5, rely=0.5, anchor="center")
        tk.Label(content, text="MISSION COMPLETE", font=("Segoe UI", 42, "bold"), bg=BG_MAIN, fg=ACCENT).pack()
        ttk.Button(content, text="PLAY AGAIN", style="Main.TButton", command=self.replay).pack(pady=10, fill="x")
        ttk.Button(content, text="LEADERBOARD", style="Secondary.TButton", command=lambda: controller.show_frame(LeaderboardPage)).pack(pady=5, fill="x")
        ttk.Button(content, text="MAIN MENU", style="Secondary.TButton", command=lambda: controller.show_frame(StartPage)).pack(pady=5, fill="x")

    def replay(self):
        self.controller.generate_puzzle()
        self.controller.start_time = time.time()
        self.controller.show_frame(GamePage)

if __name__ == "__main__":
    app = SudokuApp()
    app.mainloop()