import tkinter as tk
from tkinter import ttk, messagebox
import random
import time


class Minesweeper:
    # 난이도: 이름 = (행, 열, 지뢰 수)
    DIFFICULTIES = {
        "초급": (9, 9, 10),
        "중급": (16, 16, 40),
        "고급": (16, 30, 99)
    }

    # 숫자별 글자 색상
    NUMBER_COLORS = {
        1: "#2563EB",
        2: "#16A34A",
        3: "#DC2626",
        4: "#7C3AED",
        5: "#9F1239",
        6: "#0891B2",
        7: "#111827",
        8: "#64748B"
    }

    # UI 색상
    COLOR_BACKGROUND = "#111827"
    COLOR_PANEL = "#1F2937"
    COLOR_CELL = "#374151"
    COLOR_CELL_HOVER = "#4B5563"
    COLOR_REVEALED = "#E5E7EB"
    COLOR_TEXT = "#F9FAFB"
    COLOR_SUBTEXT = "#9CA3AF"
    COLOR_ACCENT = "#3B82F6"
    COLOR_ACCENT_HOVER = "#2563EB"
    COLOR_MINE = "#EF4444"
    COLOR_FLAG = "#F59E0B"

    def __init__(self, root):
        self.root = root
        self.root.title("Python Minesweeper")
        self.root.configure(bg=self.COLOR_BACKGROUND)
        self.root.resizable(False, False)

        # 게임 상태 변수
        self.rows = 9
        self.cols = 9
        self.mine_count = 10

        self.buttons = {}
        self.mines = set()
        self.revealed = set()
        self.flags = set()

        self.first_click = True
        self.game_finished = False
        self.timer_running = False
        self.start_time = None
        self.timer_job = None

        # 완성된 지뢰 배치가 있는지 확인
        self.board_generated = False

        self.difficulty_var = tk.StringVar(value="초급")
        self.mine_counter_var = tk.StringVar(value="지뢰 10")
        self.timer_var = tk.StringVar(value="시간 000")
        self.status_var = tk.StringVar(value="안전한 칸을 찾아보세요!")

        self.configure_styles()
        self.create_layout()
        self.new_game()

    def configure_styles(self):
        """드롭다운 메뉴 스타일 설정"""
        style = ttk.Style()
        style.theme_use("clam")

        style.configure(
            "Difficulty.TCombobox",
            fieldbackground=self.COLOR_CELL,
            background=self.COLOR_CELL,
            foreground=self.COLOR_TEXT,
            arrowcolor=self.COLOR_TEXT,
            bordercolor=self.COLOR_CELL,
            lightcolor=self.COLOR_CELL,
            darkcolor=self.COLOR_CELL,
            padding=5
        )

        style.map(
            "Difficulty.TCombobox",
            fieldbackground=[("readonly", self.COLOR_CELL)],
            foreground=[("readonly", self.COLOR_TEXT)],
            selectbackground=[("readonly", self.COLOR_CELL)],
            selectforeground=[("readonly", self.COLOR_TEXT)]
        )

    def create_layout(self):
        """전체 화면 구성"""

        # 가장 바깥쪽 여백 프레임
        self.main_frame = tk.Frame(
            self.root,
            bg=self.COLOR_BACKGROUND,
            padx=18,
            pady=16
        )
        self.main_frame.pack()

        # 제목
        title_label = tk.Label(
            self.main_frame,
            text="MINESWEEPER",
            font=("Segoe UI", 22, "bold"),
            fg=self.COLOR_TEXT,
            bg=self.COLOR_BACKGROUND
        )
        title_label.pack()

        subtitle_label = tk.Label(
            self.main_frame,
            text="Produced by Minho",
            font=("Segoe UI", 10),
            fg=self.COLOR_SUBTEXT,
            bg=self.COLOR_BACKGROUND
        )
        subtitle_label.pack(pady=(0, 14))

        # 상단 컨트롤 패널
        control_panel = tk.Frame(
            self.main_frame,
            bg=self.COLOR_PANEL,
            padx=12,
            pady=12
        )
        control_panel.pack(fill="x")

        # 난이도 영역
        difficulty_frame = tk.Frame(
            control_panel,
            bg=self.COLOR_PANEL
        )
        difficulty_frame.pack(side="left")

        difficulty_label = tk.Label(
            difficulty_frame,
            text="난이도",
            font=("Malgun Gothic", 9, "bold"),
            fg=self.COLOR_SUBTEXT,
            bg=self.COLOR_PANEL
        )
        difficulty_label.pack(anchor="w")

        self.difficulty_combo = ttk.Combobox(
            difficulty_frame,
            textvariable=self.difficulty_var,
            values=list(self.DIFFICULTIES.keys()),
            state="readonly",
            width=8,
            style="Difficulty.TCombobox",
            font=("Malgun Gothic", 10)
        )
        self.difficulty_combo.pack(pady=(3, 0))
        self.difficulty_combo.bind(
            "<<ComboboxSelected>>",
            self.change_difficulty
        )

        # 새 게임 버튼
        self.new_game_button = self.make_control_button(
            control_panel,
            text="새 게임",
            command=self.new_game,
            color=self.COLOR_ACCENT,
            hover_color=self.COLOR_ACCENT_HOVER
        )
        self.new_game_button.pack(
            side="left",
            padx=(14, 6),
            pady=(14, 0)
        )

        # 다시 시작 버튼
        self.restart_button = self.make_control_button(
            control_panel,
            text="다시 시작",
            command=self.restart_game,
            color="#4B5563",
            hover_color="#6B7280"
        )
        self.restart_button.pack(
            side="left",
            padx=6,
            pady=(14, 0)
        )

        # 정보 패널
        info_panel = tk.Frame(
            self.main_frame,
            bg=self.COLOR_PANEL,
            padx=12,
            pady=10
        )
        info_panel.pack(fill="x", pady=(8, 8))

        # 남은 지뢰 표시
        mine_box = tk.Frame(
            info_panel,
            bg="#111827",
            padx=12,
            pady=7
        )
        mine_box.pack(side="left")

        tk.Label(
            mine_box,
            textvariable=self.mine_counter_var,
            font=("Malgun Gothic", 11, "bold"),
            fg=self.COLOR_FLAG,
            bg="#111827"
        ).pack()

        # 가운데 얼굴 버튼
        self.face_button = tk.Button(
            info_panel,
            text="🙂",
            font=("Segoe UI Emoji", 16),
            width=3,
            relief="flat",
            bd=0,
            bg=self.COLOR_CELL,
            fg=self.COLOR_TEXT,
            activebackground=self.COLOR_CELL_HOVER,
            activeforeground=self.COLOR_TEXT,
            cursor="hand2",
            command=self.new_game
        )
        self.face_button.pack(side="left", expand=True)

        # 타이머 표시
        timer_box = tk.Frame(
            info_panel,
            bg="#111827",
            padx=12,
            pady=7
        )
        timer_box.pack(side="right")

        tk.Label(
            timer_box,
            textvariable=self.timer_var,
            font=("Malgun Gothic", 11, "bold"),
            fg="#60A5FA",
            bg="#111827"
        ).pack()

        # 게임판 테두리
        board_border = tk.Frame(
            self.main_frame,
            bg="#4B5563",
            padx=3,
            pady=3
        )
        board_border.pack()

        self.board_frame = tk.Frame(
            board_border,
            bg=self.COLOR_PANEL
        )
        self.board_frame.pack()

        # 상태 메시지
        self.status_label = tk.Label(
            self.main_frame,
            textvariable=self.status_var,
            font=("Malgun Gothic", 9),
            fg=self.COLOR_SUBTEXT,
            bg=self.COLOR_BACKGROUND
        )
        self.status_label.pack(pady=(10, 0))

        # 조작 방법
        help_label = tk.Label(
            self.main_frame,
            text="좌클릭: 칸 열기    |    우클릭: 깃발 표시",
            font=("Malgun Gothic", 8),
            fg="#6B7280",
            bg=self.COLOR_BACKGROUND
        )
        help_label.pack(pady=(4, 0))

    def make_control_button(
        self,
        parent,
        text,
        command,
        color,
        hover_color
    ):
        """상단 메뉴 버튼 만들기"""

        button = tk.Button(
            parent,
            text=text,
            command=command,
            font=("Malgun Gothic", 9, "bold"),
            fg="white",
            bg=color,
            activeforeground="white",
            activebackground=hover_color,
            relief="flat",
            bd=0,
            padx=13,
            pady=7,
            cursor="hand2"
        )

        button.bind(
            "<Enter>",
            lambda event: button.config(bg=hover_color)
        )

        button.bind(
            "<Leave>",
            lambda event: button.config(bg=color)
        )

        return button

    def change_difficulty(self, event=None):
        """난이도를 변경하면 새로운 게임 시작"""
        self.new_game()

    def new_game(self):
        """
        새로운 지뢰 배치로 게임 시작.
        첫 클릭 전에는 지뢰를 만들지 않는다.
        """

        self.stop_timer()

        selected_level = self.difficulty_var.get()
        self.rows, self.cols, self.mine_count = \
            self.DIFFICULTIES[selected_level]

        self.mines = set()
        self.revealed = set()
        self.flags = set()
        self.buttons = {}

        self.first_click = True
        self.game_finished = False
        self.board_generated = False

        self.timer_var.set("시간 000")
        self.mine_counter_var.set(f"지뢰 {self.mine_count}")
        self.status_var.set("첫 번째 칸은 항상 안전합니다.")
        self.face_button.config(text="🙂")

        self.clear_board()
        self.create_board()

    def restart_game(self):
        """
        현재 지뢰 배치를 그대로 유지하면서 다시 시작.
        아직 첫 클릭 전이라면 현재 빈 보드를 초기화한다.
        """

        self.stop_timer()

        self.revealed = set()
        self.flags = set()
        self.game_finished = False
        self.timer_running = False
        self.start_time = None

        # 이미 지뢰가 배치되어 있으면 같은 배치 유지
        self.first_click = not self.board_generated

        self.timer_var.set("시간 000")
        self.mine_counter_var.set(f"지뢰 {self.mine_count}")
        self.status_var.set("같은 지뢰 배치로 다시 시작했습니다.")
        self.face_button.config(text="🙂")

        self.clear_board()
        self.create_board()

    def clear_board(self):
        """기존 게임판 버튼 제거"""
        for widget in self.board_frame.winfo_children():
            widget.destroy()

    def create_board(self):
        """난이도에 맞는 버튼 게임판 생성"""

        # 고급 난이도는 버튼을 조금 작게 표시
        if self.cols >= 30:
            cell_width = 2
            cell_height = 1
            font_size = 8
            padding = 1
        elif self.cols >= 16:
            cell_width = 2
            cell_height = 1
            font_size = 9
            padding = 1
        else:
            cell_width = 3
            cell_height = 1
            font_size = 11
            padding = 2

        for row in range(self.rows):
            self.board_frame.grid_rowconfigure(row, weight=1)

            for col in range(self.cols):
                self.board_frame.grid_columnconfigure(col, weight=1)

                button = tk.Button(
                    self.board_frame,
                    text="",
                    width=cell_width,
                    height=cell_height,
                    font=("Segoe UI", font_size, "bold"),
                    fg=self.COLOR_TEXT,
                    bg=self.COLOR_CELL,
                    activebackground=self.COLOR_CELL_HOVER,
                    activeforeground=self.COLOR_TEXT,
                    relief="flat",
                    bd=0,
                    cursor="hand2"
                )

                button.grid(
                    row=row,
                    column=col,
                    padx=padding,
                    pady=padding
                )

                button.config(
                    command=lambda r=row, c=col:
                    self.left_click(r, c)
                )

                button.bind(
                    "<Button-3>",
                    lambda event, r=row, c=col:
                    self.right_click(event, r, c)
                )

                button.bind(
                    "<Enter>",
                    lambda event, r=row, c=col:
                    self.cell_hover(r, c, True)
                )

                button.bind(
                    "<Leave>",
                    lambda event, r=row, c=col:
                    self.cell_hover(r, c, False)
                )

                self.buttons[(row, col)] = button

    def cell_hover(self, row, col, hovering):
        """마우스가 칸 위에 올라왔을 때 색상 변경"""

        if self.game_finished:
            return

        if (row, col) in self.revealed:
            return

        button = self.buttons[(row, col)]

        if hovering:
            button.config(bg=self.COLOR_CELL_HOVER)
        else:
            button.config(bg=self.COLOR_CELL)

    def generate_mines(self, safe_row, safe_col):
        """
        첫 클릭 위치와 주변 8칸을 제외하고 지뢰 배치.
        첫 클릭 시 빈 구역이 열릴 가능성을 높인다.
        """

        excluded_cells = set()

        for row_offset in (-1, 0, 1):
            for col_offset in (-1, 0, 1):
                row = safe_row + row_offset
                col = safe_col + col_offset

                if 0 <= row < self.rows and 0 <= col < self.cols:
                    excluded_cells.add((row, col))

        available_cells = [
            (row, col)
            for row in range(self.rows)
            for col in range(self.cols)
            if (row, col) not in excluded_cells
        ]

        self.mines = set(
            random.sample(available_cells, self.mine_count)
        )

        self.board_generated = True

    def get_neighbors(self, row, col):
        """주변의 유효한 칸 좌표 반환"""

        neighbors = []

        for row_offset in (-1, 0, 1):
            for col_offset in (-1, 0, 1):
                if row_offset == 0 and col_offset == 0:
                    continue

                neighbor_row = row + row_offset
                neighbor_col = col + col_offset

                if (
                    0 <= neighbor_row < self.rows
                    and 0 <= neighbor_col < self.cols
                ):
                    neighbors.append(
                        (neighbor_row, neighbor_col)
                    )

        return neighbors

    def count_adjacent_mines(self, row, col):
        """주변 8칸의 지뢰 개수 계산"""

        return sum(
            1
            for position in self.get_neighbors(row, col)
            if position in self.mines
        )

    def left_click(self, row, col):
        """칸을 왼쪽 클릭했을 때"""

        if self.game_finished:
            return

        if (row, col) in self.flags:
            return

        # 첫 클릭 전에 지뢰 배치
        if self.first_click:
            self.generate_mines(row, col)
            self.first_click = False
            self.start_timer()
            self.status_var.set("게임 진행 중")

        if (row, col) in self.mines:
            self.show_game_over(row, col)
            return

        self.reveal_cell(row, col)
        self.check_win()

    def right_click(self, event, row, col):
        """우클릭으로 깃발 추가 또는 제거"""

        if self.game_finished:
            return "break"

        if (row, col) in self.revealed:
            return "break"

        button = self.buttons[(row, col)]

        if (row, col) in self.flags:
            self.flags.remove((row, col))
            button.config(
                text="",
                fg=self.COLOR_TEXT,
                bg=self.COLOR_CELL
            )
        else:
            # 실제 지뢰 수보다 깃발을 많이 만들지 않음
            if len(self.flags) >= self.mine_count:
                self.status_var.set("사용 가능한 깃발이 없습니다.")
                return "break"

            self.flags.add((row, col))
            button.config(
                text="⚑",
                fg=self.COLOR_FLAG,
                bg=self.COLOR_CELL
            )

        remaining_mines = self.mine_count - len(self.flags)
        self.mine_counter_var.set(f"지뢰 {remaining_mines}")

        return "break"

    def reveal_cell(self, row, col):
        """안전한 칸 공개 및 빈칸 자동 확장"""

        if (row, col) in self.revealed:
            return

        if (row, col) in self.flags:
            return

        if (row, col) in self.mines:
            return

        self.revealed.add((row, col))

        adjacent_mines = self.count_adjacent_mines(row, col)
        button = self.buttons[(row, col)]

        if adjacent_mines == 0:
            display_text = ""
            text_color = self.COLOR_TEXT
        else:
            display_text = str(adjacent_mines)
            text_color = self.NUMBER_COLORS[adjacent_mines]

        button.config(
            text=display_text,
            fg=text_color,
            bg=self.COLOR_REVEALED,
            activebackground=self.COLOR_REVEALED,
            relief="flat",
            cursor="arrow"
        )

        # 주변 지뢰가 없으면 주변 칸도 자동 공개
        if adjacent_mines == 0:
            for neighbor_row, neighbor_col in \
                    self.get_neighbors(row, col):

                self.reveal_cell(
                    neighbor_row,
                    neighbor_col
                )

    def show_game_over(self, clicked_row, clicked_col):
        """지뢰를 클릭했을 때 게임 종료"""

        self.game_finished = True
        self.stop_timer()
        self.face_button.config(text="😵")
        self.status_var.set("지뢰를 밟았습니다. 다시 도전해보세요!")

        for mine_row, mine_col in self.mines:
            mine_button = self.buttons[(mine_row, mine_col)]

            if (mine_row, mine_col) == \
                    (clicked_row, clicked_col):

                mine_button.config(
                    text="✹",
                    fg="white",
                    bg=self.COLOR_MINE,
                    activebackground=self.COLOR_MINE
                )
            else:
                mine_button.config(
                    text="●",
                    fg=self.COLOR_MINE,
                    bg=self.COLOR_REVEALED,
                    activebackground=self.COLOR_REVEALED
                )

        # 잘못 꽂은 깃발 표시
        for flag_position in self.flags:
            if flag_position not in self.mines:
                self.buttons[flag_position].config(
                    text="✕",
                    fg=self.COLOR_MINE,
                    bg=self.COLOR_REVEALED
                )

        messagebox.showerror(
            "게임 오버",
            "지뢰를 밟았습니다!\n\n"
            "'다시 시작'을 누르면 같은 지뢰 배치로\n"
            "한 번 더 도전할 수 있습니다."
        )

    def check_win(self):
        """모든 안전한 칸을 열었는지 확인"""

        safe_cell_count = (
            self.rows * self.cols - self.mine_count
        )

        if len(self.revealed) != safe_cell_count:
            return

        self.game_finished = True
        self.stop_timer()
        self.face_button.config(text="😎")
        self.status_var.set("축하합니다! 모든 안전 칸을 찾았습니다.")

        # 지뢰 칸에 자동으로 깃발 표시
        for mine_position in self.mines:
            self.buttons[mine_position].config(
                text="⚑",
                fg=self.COLOR_FLAG,
                bg=self.COLOR_CELL
            )

        self.flags = set(self.mines)
        self.mine_counter_var.set("지뢰 0")

        elapsed_time = self.get_elapsed_time()

        messagebox.showinfo(
            "승리",
            f"축하합니다!\n\n"
            f"난이도: {self.difficulty_var.get()}\n"
            f"기록: {elapsed_time}초"
        )

    def start_timer(self):
        """첫 클릭부터 타이머 시작"""

        self.timer_running = True
        self.start_time = time.time()
        self.update_timer()

    def update_timer(self):
        """타이머 화면 갱신"""

        if not self.timer_running:
            return

        elapsed_time = self.get_elapsed_time()
        displayed_time = min(elapsed_time, 999)

        self.timer_var.set(f"시간 {displayed_time:03d}")

        self.timer_job = self.root.after(
            1000,
            self.update_timer
        )

    def get_elapsed_time(self):
        """현재까지 흐른 시간 반환"""

        if self.start_time is None:
            return 0

        return int(time.time() - self.start_time)

    def stop_timer(self):
        """타이머 중지"""

        self.timer_running = False

        if self.timer_job is not None:
            self.root.after_cancel(self.timer_job)
            self.timer_job = None


if __name__ == "__main__":
    root = tk.Tk()
    game = Minesweeper(root)
    root.mainloop()