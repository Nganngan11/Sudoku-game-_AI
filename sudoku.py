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
        self.title("AI Sudoku - CSP Master Edition")
        self.geometry("1200x850")
        self.configure(bg=BG_MAIN)


        self.grid_size = 9
        self.sub_rows = 3
        self.sub_cols = 3
        self.difficulty_level = 1
        self.hints_left = 3 # Giới hạn 3 lượt hint
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
        style.configure("Danger.TButton", font=("Segoe UI", 11, "bold"), background="#fee2e2", foreground=ERROR_COLOR)


    def show_frame(self, cont):
        frame = self.frames[cont]
        frame.tkraise()
        if hasattr(frame, 'on_show'):
            frame.on_show()


    # ====== AI CSP CORE LOGIC ======
    def get_domain(self, board, row, col):
        size = self.grid_size
        used = set()
        for i in range(size):
            used.add(board[row][i])
            used.add(board[i][col])
        sr, sc = (row // self.sub_rows) * self.sub_rows, (col // self.sub_cols) * self.sub_cols
        for i in range(self.sub_rows):
            for j in range(self.sub_cols):
                used.add(board[sr + i][sc + j])
        return [n for n in range(1, size + 1) if n not in used]


    def find_mrv_variable(self, board):
        best_cell = None
        min_domain_size = self.grid_size + 1
        for r in range(self.grid_size):
            for c in range(self.grid_size):
                if board[r][c] == 0:
                    domain = self.get_domain(board, r, c)
                    if len(domain) < min_domain_size:
                        min_domain_size = len(domain)
                        best_cell = (r, c, domain)
                    if min_domain_size == 1: return best_cell
        return best_cell


    def solve_csp(self, board):
        cell_info = self.find_mrv_variable(board)
        if not cell_info: return True
        r, c, domain = cell_info
        random.shuffle(domain)
        for val in domain:
            board[r][c] = val
            if self.solve_csp(board): return True
            board[r][c] = 0
        return False


    def generate_puzzle(self):
        size = self.grid_size
        board = [[0]*size for _ in range(size)]
        self.solve_csp(board)
        self.solution = copy.deepcopy(board)
        ratios = {1: 0.35, 2: 0.5, 3: 0.65, 4: 0.8}
        empty_count = int(size*size * ratios.get(self.difficulty_level, 0.5))
        pos = [(r, c) for r in range(size) for c in range(size)]
        random.shuffle(pos)
        for i in range(empty_count): board[pos[i][0]][pos[i][1]] = 0
        self.current_puzzle = board


    def load_scores(self):
        if not os.path.exists(self.scores_file): return []
        try:
            with open(self.scores_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                return data if isinstance(data, list) else []
        except: return []


    def save_score(self, completion_time):
        diff_map = {1: "Easy", 2: "Medium", 3: "Hard", 4: "Insane"}
        new_score = {
            "player": self.player_name, "grid": f"{self.grid_size}x{self.grid_size}",
            "difficulty": diff_map.get(self.difficulty_level, "Unknown"),
            "time_seconds": completion_time, "date": datetime.now().strftime("%Y-%m-%d %H:%M")
        }
        scores = self.load_scores()
        scores.append(new_score)
        with open(self.scores_file, "w", encoding="utf-8") as f: json.dump(scores, f, indent=4)


# ====== UI PAGES ======


class StartPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=BG_MAIN)
        content = tk.Frame(self, bg=BG_MAIN)
        content.place(relx=0.5, rely=0.5, anchor="center")
        tk.Label(content, text="SUDOKU AI", font=("Segoe UI", 48, "bold"), bg=BG_MAIN, fg=PRIMARY).pack()
        tk.Label(content, text="CSP & MRV ENGINE", font=("Segoe UI", 14, "italic"), bg=BG_MAIN, fg=TEXT_MUTE).pack(pady=(0, 40))
        ttk.Button(content, text="PLAY GAME", width=25, style="Main.TButton", command=lambda: controller.show_frame(DifficultyPage)).pack(pady=5)
        ttk.Button(content, text="LEADERBOARD", width=25, style="Secondary.TButton", command=lambda: controller.show_frame(LeaderboardPage)).pack(pady=5)
        ttk.Button(content, text="RULES & AI LOGIC", width=25, style="Secondary.TButton", command=lambda: controller.show_frame(RulesPage)).pack(pady=5)
        ttk.Button(content, text="EXIT", width=25, style="Secondary.TButton", command=controller.quit).pack(pady=5)


class RulesPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=BG_MAIN)
        card = tk.Frame(self, bg=BG_CARD, padx=40, pady=40, highlightthickness=1, highlightbackground=BORDER)
        card.place(relx=0.5, rely=0.5, anchor="center", width=750)
        tk.Label(card, text="📜 RULES & AI MECHANICS", font=("Segoe UI", 26, "bold"), bg=BG_CARD, fg=PRIMARY).pack(pady=(0, 20))
        rules = [
            ("1. Basic Goal:", "Fill the grid so every row, column, and sub-grid contains digits 1-N without repeats."),
            ("2. Limited Hints:", "You only have 3 hints per game. Use them wisely!"),
            ("3. MRV Heuristic:", "Hints use 'Minimum Remaining Values' to find the cell with the fewest possible legal moves."),
            ("4. Surrender Mode:", "If you give up, the AI will use CSP Backtracking to reveal the full solution."),
            ("5. Mistake Limit:", "You have 5 mistakes allowed. Over 5 results in Game Over.")
        ]
        for title, desc in rules:
            f = tk.Frame(card, bg=BG_CARD)
            f.pack(fill="x", pady=8)
            tk.Label(f, text=title, font=("Segoe UI", 11, "bold"), bg=BG_CARD, fg=TEXT_DARK).pack(anchor="w")
            tk.Label(f, text=desc, font=("Segoe UI", 10), bg=BG_CARD, fg=TEXT_MUTE, wraplength=650, justify="left").pack(anchor="w", padx=(10, 0))
        ttk.Button(card, text="BACK TO MENU", style="Main.TButton", command=lambda: controller.show_frame(StartPage)).pack(pady=(30, 0))


class DifficultyPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=BG_MAIN)
        self.controller = controller
        card = tk.Frame(self, bg=BG_CARD, padx=40, pady=40, highlightthickness=1, highlightbackground=BORDER)
        card.place(relx=0.5, rely=0.5, anchor="center")
        tk.Label(card, text="Game Settings", font=("Segoe UI", 24, "bold"), bg=BG_CARD, fg=TEXT_DARK).pack(pady=(0, 30))
        tk.Label(card, text="PLAYER NAME", font=("Segoe UI", 9, "bold"), bg=BG_CARD, fg=TEXT_MUTE).pack(anchor="w")
        self.name_ent = tk.Entry(card, font=("Segoe UI", 12), bg=BG_MAIN, bd=0, highlightthickness=1, highlightbackground=BORDER)
        self.name_ent.pack(fill="x", pady=(5, 20), ipady=8)
        self.size_var = tk.IntVar(value=9)
        size_f = tk.Frame(card, bg=BG_CARD); size_f.pack(pady=(5, 20))
        for s in [3, 6, 9]: tk.Radiobutton(size_f, text=f"{s}x{s}", variable=self.size_var, value=s, bg=BG_CARD).pack(side="left", padx=15)
        self.diff_var = tk.IntVar(value=1)
        diff_f = tk.Frame(card, bg=BG_CARD); diff_f.pack(pady=(5, 30))
        for t, v in [("Easy", 1), ("Medium", 2), ("Hard", 3), ("Insane", 4)]:
            tk.Radiobutton(diff_f, text=t, variable=self.diff_var, value=v, bg=BG_CARD).pack(side="left", padx=10)
        ttk.Button(card, text="START ENGINE", style="Main.TButton", command=self.confirm).pack(fill="x")


    def confirm(self):
        self.controller.player_name = self.name_ent.get() or "Guest"
        self.controller.grid_size = self.size_var.get()
        self.controller.difficulty_level = self.diff_var.get()
        self.controller.mistakes = 0
        self.controller.hints_left = 3 # Reset lượt hint mỗi khi bắt đầu game mới
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
        header.pack(fill="x", side="top"); header.pack_propagate(False)
        tk.Label(header, text="SUDOKU SESSION", font=("Segoe UI", 16, "bold"), bg=BG_CARD, fg=TEXT_DARK).pack(side="left", padx=30)
       
        self.main_container = tk.Frame(self, bg=BG_MAIN); self.main_container.pack(expand=True, fill="both", padx=40, pady=20)
        self.sidebar = tk.Frame(self.main_container, bg=BG_CARD, width=280, padx=25, pady=25, highlightthickness=1, highlightbackground=BORDER)
        self.sidebar.pack(side="right", fill="y", padx=(20, 0)); self.sidebar.pack_propagate(False)
       
        # --- Stats ---
        tk.Label(self.sidebar, text="TIME", font=("Segoe UI", 9, "bold"), bg=BG_CARD, fg=TEXT_MUTE).pack(anchor="w")
        self.timer_lbl = tk.Label(self.sidebar, text="00:00", font=("Consolas", 24, "bold"), bg=BG_CARD, fg=PRIMARY); self.timer_lbl.pack(anchor="w", pady=(0, 15))
       
        tk.Label(self.sidebar, text="MISTAKES", font=("Segoe UI", 9, "bold"), bg=BG_CARD, fg=TEXT_MUTE).pack(anchor="w")
        self.mistake_lbl = tk.Label(self.sidebar, text="0 / 5", font=("Segoe UI", 18, "bold"), bg=BG_CARD, fg=ERROR_COLOR); self.mistake_lbl.pack(anchor="w", pady=(0, 15))
       
        tk.Label(self.sidebar, text="HINTS LEFT", font=("Segoe UI", 9, "bold"), bg=BG_CARD, fg=TEXT_MUTE).pack(anchor="w")
        self.hint_lbl = tk.Label(self.sidebar, text="3", font=("Segoe UI", 18, "bold"), bg=BG_CARD, fg=ACCENT); self.hint_lbl.pack(anchor="w", pady=(0, 20))


        self.info_lbl = tk.Label(self.sidebar, text="", font=("Segoe UI", 10), bg=BG_CARD, justify="left"); self.info_lbl.pack(anchor="w", pady=(0, 20))
       
        # --- Buttons ---
        self.hint_btn = ttk.Button(self.sidebar, text="💡 USE HINT (MRV)", style="Main.TButton", command=self.use_hint)
        self.hint_btn.pack(fill="x", pady=5)
       
        self.giveup_btn = ttk.Button(self.sidebar, text="🏳️ GIVE UP (SHOW ALL)", style="Danger.TButton", command=self.show_full_solution)
        self.giveup_btn.pack(fill="x", pady=5)
       
        # Gán vào biến self.submit_btn để có thể ẩn đi sau này
        self.submit_btn = ttk.Button(self.sidebar, text="✅ SUBMIT", style="Secondary.TButton", command=self.check_result)
        self.submit_btn.pack(fill="x", pady=(15, 5))
       
        ttk.Button(self.sidebar, text="QUIT", style="Secondary.TButton", command=self.exit_game).pack(fill="x", pady=5)
       
        self.canvas_frame = tk.Frame(self.main_container, bg=BG_MAIN); self.canvas_frame.pack(side="left", expand=True)
        self.canvas = None


    def update_timer(self):
        if self.controller.timer_running:
            elapsed = int(time.time() - self.controller.start_time)
            mins, secs = divmod(elapsed, 60)
            self.timer_lbl.config(text=f"{mins:02d}:{secs:02d}")
            self.after(1000, self.update_timer)


    def update_info(self):
        self.mistake_lbl.config(text=f"{self.controller.mistakes} / {self.controller.max_mistakes}")
        self.hint_lbl.config(text=f"{self.controller.hints_left}")
        self.info_lbl.config(text=f"Player: {self.controller.player_name}\nSize: {self.controller.grid_size}x{self.controller.grid_size}")


    def draw_grid(self):
        if self.canvas: self.canvas.destroy()
        size = self.controller.grid_size
       
        cell_size = 600 // size
        actual_size = cell_size * size
       
        self.canvas = tk.Canvas(self.canvas_frame, width=actual_size, height=actual_size, bg="white", highlightthickness=2, highlightbackground=TEXT_DARK)
        self.canvas.pack()
       
        self.controller.player_entries = []
        puzzle = self.controller.current_puzzle
        for r in range(size):
            for c in range(size):
                x1, y1 = c * cell_size, r * cell_size
                mid_x, mid_y = x1 + cell_size/2, y1 + cell_size/2
                if puzzle[r][c] != 0:
                    self.canvas.create_rectangle(x1, y1, x1+cell_size, y1+cell_size, outline=BORDER, fill="#fdfdfd")
                    self.canvas.create_text(mid_x, mid_y, text=str(puzzle[r][c]), font=("Segoe UI", int(20*(9/size)), "bold"), fill=TEXT_DARK)
                else:
                    entry = tk.Entry(self.canvas, font=("Segoe UI", int(18*(9/size))), justify="center", bd=0, bg="#f8fafc", fg=PRIMARY)
                    self.canvas.create_window(mid_x, mid_y, window=entry, width=cell_size-4, height=cell_size-4)
                    entry.bind("<KeyRelease>", lambda e, row=r, col=c, ent=entry: self.handle_input(row, col, ent))
                    self.controller.player_entries.append((r, c, entry))
       
   
        for i in range(1, size):
            lw = 3 if i % self.controller.sub_cols == 0 else 1
            self.canvas.create_line(i * cell_size, 0, i * cell_size, actual_size, width=lw)
           
            lw = 3 if i % self.controller.sub_rows == 0 else 1
            self.canvas.create_line(0, i * cell_size, actual_size, i * cell_size, width=lw)


    def handle_input(self, r, c, ent):
        val = ent.get().strip()
        if not val: return
        if not val.isdigit() or int(val) != self.controller.solution[r][c]:
            self.controller.mistakes += 1
            ent.config(fg=ERROR_COLOR); self.update_info()
            if self.controller.mistakes >= self.controller.max_mistakes:
                messagebox.showerror("GAME OVER", "Too many mistakes!"); self.controller.show_frame(StartPage)
        else: ent.config(fg=PRIMARY)


    def update_cell(self, r, c, val, color):
        for row, col, ent in self.controller.player_entries:
            if row == r and col == c:
                ent.delete(0, tk.END); ent.insert(0, str(val)); ent.config(fg=color); break


    def use_hint(self):
        if self.controller.hints_left <= 0:
            messagebox.showwarning("Out of Hints", "You have used all 3 hints!")
            return


        # Lấy board hiện tại (kể cả số người chơi nhập)
        board = copy.deepcopy(self.controller.current_puzzle)
        for r, c, ent in self.controller.player_entries:
            val = ent.get()
            if val.isdigit():
                board[r][c] = int(val)


        # MRV
        cell = self.controller.find_mrv_variable(board)
        if not cell:
            messagebox.showinfo("Hint", "No hint available.")
            return


        r, c, domain = cell


        # Highlight ô được gợi ý
        for row, col, ent in self.controller.player_entries:
            if row == r and col == c:
                ent.config(bg="#fef08a")  
            else:
                ent.config(bg="#f8fafc")


        # Hiển thị gợi ý (KHÔNG điền số)
        self.info_lbl.config(
            text=(
                "💡 Hint (MRV):\n"
                f"Cell: ({r+1}, {c+1})\n"
                f"Possible values: {domain}"
            )
        )
       
        messagebox.showinfo(
            "MRV Hint",
            f"Suggested cell: ({r+1}, {c+1})\n"
            f"Possible values: {domain}"
        )


        self.controller.hints_left -= 1
        self.update_info()




    def show_full_solution(self):
        if not messagebox.askyesno("Give Up?", "Do you want to reveal the full solution? (Game will end)"):
            return
           
        self.controller.timer_running = False
       
        # --- CHỈNH SỬA TẠI ĐÂY ---
        self.submit_btn.pack_forget()  # Ẩn nút Submit
        self.hint_btn.config(state="disabled") # Vô hiệu hóa nút Hint
        # -------------------------


        for r, c, ent in self.controller.player_entries:
            correct_val = self.controller.solution[r][c]
            ent.delete(0, tk.END)
            ent.insert(0, str(correct_val))
            ent.config(fg=TEXT_DARK, state="readonly")
           
        messagebox.showinfo("Solution Revealed", "The CSP solver has completed the board for you.")


    def on_show(self):
        self.submit_btn.pack(fill="x", pady=(15, 5), after=self.giveup_btn)
       
        self.hint_btn.config(state="normal")
       
        self.controller.timer_running = True
        self.draw_grid()
        self.update_info()
        self.update_timer()


    def check_result(self):
        for r, c, ent in self.controller.player_entries:
            if ent.get() != str(self.controller.solution[r][c]):
                messagebox.showwarning("Incomplete", "The grid is not correct yet."); return
        self.controller.timer_running = False
        self.controller.save_score(int(time.time() - self.controller.start_time))
        self.controller.show_frame(ResultPage)


    def exit_game(self):
        self.controller.timer_running = False; self.controller.show_frame(StartPage)
       
# Các class LeaderboardPage, ResultPage giữ nguyên như cũ...
class LeaderboardPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=BG_MAIN)
        self.controller = controller
        card = tk.Frame(self, bg=BG_CARD, padx=30, pady=30, highlightthickness=1, highlightbackground=BORDER)
        card.place(relx=0.5, rely=0.5, anchor="center", width=850, height=650)
        tk.Label(card, text="🏆 GLOBAL RANKINGS", font=("Segoe UI", 28, "bold"), bg=BG_CARD, fg=PRIMARY).pack(pady=(0, 20))
        self.tree = ttk.Treeview(card, columns=("Name", "Grid", "Difficulty", "Time"), show="headings", height=12)
        for col, text in [("Name", "PLAYER"), ("Grid", "SIZE"), ("Difficulty", "LEVEL"), ("Time", "TIME")]:
            self.tree.heading(col, text=text); self.tree.column(col, anchor="center")
        self.tree.pack(fill="both", expand=True)
        ttk.Button(card, text="BACK TO MENU", style="Secondary.TButton", command=lambda: controller.show_frame(StartPage)).pack(pady=20)


    def on_show(self):
        for item in self.tree.get_children(): self.tree.delete(item)
        raw_scores = self.controller.load_scores()
        clean_scores = [s for s in raw_scores if isinstance(s, dict)]
        scores = sorted(clean_scores, key=lambda x: x.get("time_seconds", 999))
        for s in scores[:10]:
            m, sec = divmod(s.get('time_seconds', 0), 60)
            self.tree.insert("", "end", values=(s.get('player', 'Guest'), s.get('grid', 'N/A'), s.get('difficulty', 'N/A'), f"{m:02d}:{sec:02d}"))


class ResultPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=BG_MAIN)
        content = tk.Frame(self, bg=BG_MAIN); content.place(relx=0.5, rely=0.5, anchor="center")
        tk.Label(content, text="CONGRATULATIONS!", font=("Segoe UI", 32, "bold"), bg=BG_MAIN, fg=ACCENT).pack(pady=20)
        tk.Label(content, text="You have solved the puzzle.", font=("Segoe UI", 14), bg=BG_MAIN, fg=TEXT_MUTE).pack(pady=(0, 30))
        ttk.Button(content, text="PLAY AGAIN", style="Main.TButton", command=lambda: controller.show_frame(DifficultyPage)).pack(fill="x", pady=5)
        ttk.Button(content, text="MAIN MENU", style="Secondary.TButton", command=lambda: controller.show_frame(StartPage)).pack(fill="x")


if __name__ == "__main__":
    app = SudokuApp(); app.mainloop()

