"""
Main GUI application for the MLB HR Catch-Probability Heatmap tool.

Layout
------
Left panel  : controls (stadium, team, player, season, section, buttons)
Right panel : matplotlib stadium heatmap
Bottom strip: status bar
"""

from __future__ import annotations

import queue
import threading
import tkinter as tk
from tkinter import messagebox, ttk
from typing import Optional

import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk

import data as mlb_data
import visualizer as viz
from stadiums import MLB_STADIUMS, STADIUM_NAMES
from sections import get_sections, get_section_ids


# ---------------------------------------------------------------------------
# Colour palette for the dark-themed controls panel
# ---------------------------------------------------------------------------
BG      = "#1e1e2e"
PANEL   = "#2a2a3e"
ACCENT  = "#7c5cbf"
FG      = "#e0e0e0"
FG_DIM  = "#888899"
BTN_BG  = "#3d3d5c"
BTN_ACT = "#5a5aaa"
ERR_FG  = "#ff6b6b"
OK_FG   = "#6bff9e"


class HRHeatmapApp(tk.Tk):
    """Top-level application window."""

    def __init__(self):
        super().__init__()
        self.title("MLB Home Run Catch Probability")
        self.configure(bg=BG)
        self.resizable(True, True)
        self.minsize(1050, 680)

        # Runtime state
        self._teams:      list[dict]         = []
        self._roster:     list[dict]         = []
        self._hr_df                          = None
        self._probs:      dict[str, float]   = {}
        self._stadium_info: Optional[dict]   = None
        self._cbar                           = None
        self._highlight_section: Optional[str] = None
        self._current_title: str             = ""
        self._current_stadium: str           = ""
        self._data_queue: queue.Queue        = queue.Queue()
        self._poll_id:    Optional[str]      = None
        self._pending_tasks: int             = 0   # in-flight background tasks

        self._build_ui()
        self._load_teams_async()

    # ------------------------------------------------------------------
    # UI construction
    # ------------------------------------------------------------------

    def _build_ui(self) -> None:
        # ── Main pane ────────────────────────────────────────────────
        pane = tk.PanedWindow(self, orient=tk.HORIZONTAL, bg=BG,
                              sashwidth=5, sashrelief=tk.GROOVE)
        pane.pack(fill=tk.BOTH, expand=True)

        # Left: control panel
        left = tk.Frame(pane, bg=PANEL, padx=10, pady=10, width=240)
        left.pack_propagate(False)
        pane.add(left, minsize=220)

        # Right: figure
        right = tk.Frame(pane, bg=BG)
        pane.add(right, minsize=600)

        self._build_controls(left)
        self._build_figure(right)

        # Status bar
        self._status_var = tk.StringVar(value="Ready. Select a stadium to begin.")
        status_bar = tk.Label(self, textvariable=self._status_var,
                              bg="#111120", fg=FG_DIM, anchor=tk.W,
                              font=("Consolas", 9), padx=8, pady=3)
        status_bar.pack(fill=tk.X, side=tk.BOTTOM)
        self._status_label = status_bar

    def _build_controls(self, parent: tk.Frame) -> None:
        row = 0

        def label(text):
            nonlocal row
            tk.Label(parent, text=text, bg=PANEL, fg=FG_DIM,
                     font=("Segoe UI", 8), anchor=tk.W).grid(
                row=row, column=0, sticky=tk.W, pady=(10, 1))
            row += 1

        def combo(values=(), state="readonly", width=26):
            nonlocal row
            c = ttk.Combobox(parent, values=values, state=state, width=width,
                             font=("Segoe UI", 9))
            c.grid(row=row, column=0, sticky=tk.EW, pady=(0, 2))
            row += 1
            return c

        # Apply custom combobox style
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure("TCombobox",
                        fieldbackground=BTN_BG, background=ACCENT,
                        foreground=FG, arrowcolor=FG,
                        selectbackground=ACCENT, selectforeground=FG)
        style.map("TCombobox",
                  fieldbackground=[("readonly", BTN_BG)],
                  foreground=[("readonly", FG)])

        parent.columnconfigure(0, weight=1)

        # ── Header ────────────────────────────────────────────────────
        tk.Label(parent, text="⚾  HR Catch Probability",
                 bg=PANEL, fg=FG, font=("Segoe UI", 11, "bold"),
                 anchor=tk.W).grid(row=row, column=0, sticky=tk.W, pady=(0, 6))
        row += 1

        tk.Frame(parent, bg=ACCENT, height=1).grid(
            row=row, column=0, sticky=tk.EW, pady=(0, 6))
        row += 1

        # ── Stadium ────────────────────────────────────────────────────
        label("Stadium")
        self._stadium_var = tk.StringVar()
        self._stadium_cb  = combo(STADIUM_NAMES)
        self._stadium_cb.configure(textvariable=self._stadium_var)
        self._stadium_cb.bind("<<ComboboxSelected>>", self._on_stadium_selected)

        # ── Team (shows home team; cannot change if stadium has one team) ──
        label("Team")
        self._team_var = tk.StringVar()
        self._team_cb  = combo()
        self._team_cb.configure(textvariable=self._team_var)
        self._team_cb.bind("<<ComboboxSelected>>", self._on_team_selected)

        # ── Player ────────────────────────────────────────────────────
        label("Player")
        self._player_var = tk.StringVar(value="All Players")
        self._player_cb  = combo(["All Players"])
        self._player_cb.configure(textvariable=self._player_var)

        # ── Season ────────────────────────────────────────────────────
        label("Season")
        self._season_var = tk.StringVar(value="2024")
        seasons = [str(y) for y in range(2025, 2018, -1)]
        self._season_cb  = combo(seasons)
        self._season_cb.set("2024")

        # ── Section lookup (optional) ──────────────────────────────────
        label("Highlight Section (optional)")
        tk.Label(parent, text="Enter a section number from\nthe selected stadium",
                 bg=PANEL, fg=FG_DIM, font=("Consolas", 7),
                 wraplength=200, justify=tk.LEFT).grid(
            row=row, column=0, sticky=tk.W)
        row += 1

        section_frame = tk.Frame(parent, bg=PANEL)
        section_frame.grid(row=row, column=0, sticky=tk.EW, pady=(0, 4))
        section_frame.columnconfigure(0, weight=1)
        row += 1

        self._section_var = tk.StringVar()
        self._section_entry = tk.Entry(section_frame,
                                       textvariable=self._section_var,
                                       bg=BTN_BG, fg=FG, insertbackground=FG,
                                       font=("Consolas", 9), relief=tk.FLAT,
                                       width=14)
        self._section_entry.grid(row=0, column=0, sticky=tk.EW, padx=(0, 4))
        tk.Button(section_frame, text="Go", command=self._highlight_section,
                  bg=ACCENT, fg=FG, relief=tk.FLAT, font=("Segoe UI", 8),
                  activebackground=BTN_ACT, cursor="hand2").grid(row=0, column=1)

        # ── Buttons ────────────────────────────────────────────────────
        tk.Frame(parent, bg=ACCENT, height=1).grid(
            row=row, column=0, sticky=tk.EW, pady=8)
        row += 1

        btn_cfg = dict(bg=ACCENT, fg=FG, relief=tk.FLAT, font=("Segoe UI", 9, "bold"),
                       activebackground=BTN_ACT, cursor="hand2", pady=5)

        self._gen_btn = tk.Button(parent, text="Generate Heatmap",
                                  command=self._generate, **btn_cfg)
        self._gen_btn.grid(row=row, column=0, sticky=tk.EW, pady=(0, 4))
        row += 1

        tk.Button(parent, text="Clear", command=self._clear, **btn_cfg).grid(
            row=row, column=0, sticky=tk.EW, pady=(0, 4))
        row += 1

        # ── Info panel ────────────────────────────────────────────────
        tk.Frame(parent, bg=ACCENT, height=1).grid(
            row=row, column=0, sticky=tk.EW, pady=8)
        row += 1

        tk.Label(parent, text="Section Info", bg=PANEL, fg=FG,
                 font=("Segoe UI", 9, "bold"), anchor=tk.W).grid(
            row=row, column=0, sticky=tk.W)
        row += 1

        self._info_text = tk.Text(parent, bg=BTN_BG, fg=FG,
                                  font=("Consolas", 8), height=14,
                                  relief=tk.FLAT, wrap=tk.WORD,
                                  state=tk.DISABLED, padx=4, pady=4)
        self._info_text.grid(row=row, column=0, sticky=tk.NSEW, pady=(2, 0))
        parent.rowconfigure(row, weight=1)
        row += 1

    def _build_figure(self, parent: tk.Frame) -> None:
        self._fig, self._ax = viz.build_figure(figsize=(8, 8))
        self._canvas = FigureCanvasTkAgg(self._fig, master=parent)
        self._canvas.draw()

        toolbar_frame = tk.Frame(parent, bg=BG)
        toolbar_frame.pack(fill=tk.X, side=tk.BOTTOM)
        toolbar = NavigationToolbar2Tk(self._canvas, toolbar_frame)
        toolbar.config(background=BG)
        for child in toolbar.winfo_children():
            try:
                child.config(background=BG)
            except tk.TclError:
                pass
        toolbar.update()

        self._canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        self._canvas.mpl_connect("button_press_event", self._on_plot_click)

    # ------------------------------------------------------------------
    # Async team loading
    # ------------------------------------------------------------------

    def _load_teams_async(self) -> None:
        self._set_status("Loading MLB teams…", dim=True)

        def worker():
            try:
                teams = mlb_data.get_teams()
                self._data_queue.put(("teams", teams))
            except Exception as exc:
                self._data_queue.put(("error", f"Failed to load teams: {exc}"))

        threading.Thread(target=worker, daemon=True).start()
        self._start_polling()

    # ------------------------------------------------------------------
    # Event handlers – dropdowns
    # ------------------------------------------------------------------

    def _on_stadium_selected(self, _event=None) -> None:
        name = self._stadium_var.get()
        info = MLB_STADIUMS.get(name)
        if not info:
            return
        self._stadium_info = info

        # Populate team dropdown using the stadium's home team.
        # If mlbstatsapi teams are loaded, match by team_id; otherwise use static name.
        home_team = info["team"]
        if self._teams:
            matched = [t for t in self._teams if t["id"] == info["team_id"]]
            team_names = [t["name"] for t in matched] if matched else [home_team]
        else:
            team_names = [home_team]

        self._team_cb["values"] = team_names
        self._team_cb.set(team_names[0])
        self._player_cb["values"] = ["All Players"]
        self._player_cb.set("All Players")

        # Show empty stadium layout immediately for visual feedback
        if self._cbar is not None:
            try:
                self._cbar.remove()
            except Exception:
                pass
            self._cbar = None
        self._hr_df  = None
        self._probs  = {}
        self._highlight_section = None
        viz.draw_empty_stadium(
            self._ax, info["lf"], info["cf"], info["rf"],
            stadium_name=name, title=name,
        )
        self._canvas.draw_idle()

        self._on_team_selected()

    def _on_team_selected(self, _event=None) -> None:
        team_name = self._team_var.get()
        if not team_name:
            return
        matched = [t for t in self._teams if t["name"] == team_name]
        if not matched:
            return
        team_id = matched[0]["id"]
        self._load_roster_async(team_id)

    # ------------------------------------------------------------------
    # Async roster loading
    # ------------------------------------------------------------------

    def _load_roster_async(self, team_id: int) -> None:
        self._set_status(f"Loading roster for team {team_id}…", dim=True)
        self._player_cb["values"] = ["Loading…"]
        self._player_cb.set("Loading…")

        def worker():
            try:
                roster = mlb_data.get_roster(team_id)
                self._data_queue.put(("roster", roster))
            except Exception as exc:
                self._data_queue.put(("error", f"Failed to load roster: {exc}"))

        threading.Thread(target=worker, daemon=True).start()
        self._start_polling()

    # ------------------------------------------------------------------
    # Generate heatmap
    # ------------------------------------------------------------------

    def _generate(self) -> None:
        if not self._stadium_info:
            messagebox.showwarning("No Stadium", "Please select a stadium first.")
            return

        stadium_name  = self._stadium_var.get()
        player_choice = self._player_var.get()
        season        = int(self._season_cb.get())

        self._gen_btn.configure(state=tk.DISABLED)
        self._set_status("Downloading HR data from Baseball Savant…", dim=True)

        info = self._stadium_info

        def worker():
            try:
                if player_choice == "All Players":
                    abbrev = info["abbrev"]
                    hr_df  = mlb_data.fetch_team_hr_data(abbrev, season)
                    label  = f"{info['team']} – {season}"
                else:
                    # Find player ID
                    pid = next(
                        (p["id"] for p in self._roster if p["full_name"] == player_choice),
                        None,
                    )
                    if pid is None:
                        raise ValueError(f"Player not found: {player_choice}")
                    hr_df = mlb_data.fetch_player_hr_data(pid, season)
                    label = f"{player_choice} – {season}"

                if hr_df.empty:
                    self._data_queue.put(("warning",
                        f"No HR data found for {label}.\n"
                        "Try a different season or player."))
                    return

                lf, cf, rf = info["lf"], info["cf"], info["rf"]
                hr_df  = mlb_data.assign_sections(hr_df, lf, cf, rf, stadium_name)
                probs  = mlb_data.compute_probabilities(hr_df, stadium_name)
                self._data_queue.put(("heatmap", {
                    "hr_df":        hr_df,
                    "probs":        probs,
                    "lf": lf, "cf": cf, "rf": rf,
                    "stadium_name": stadium_name,
                    "title":        f"{stadium_name}  –  {label}",
                    "total":        len(hr_df),
                }))
            except Exception as exc:
                self._data_queue.put(("error", str(exc)))

        threading.Thread(target=worker, daemon=True).start()
        self._start_polling()

    # ------------------------------------------------------------------
    # Section highlight
    # ------------------------------------------------------------------

    def _highlight_section(self) -> None:
        sid   = self._section_var.get().strip()
        valid = set(get_section_ids(self._stadium_var.get()))
        if sid not in valid:
            self._set_status(
                f"Unknown section '{sid}'. Valid for this stadium: {', '.join(sorted(valid))}",
                error=True,
            )
            return
        self._highlight_section_id(sid)

    def _highlight_section_id(self, sid: str) -> None:
        self._highlight_section = sid
        if self._probs:
            self._redraw()
        self._update_info_panel(sid)

    def _update_info_panel(self, sid: str) -> None:
        sections = get_sections(self._stadium_var.get())
        match    = next((s for s in sections if s[0] == sid), None)
        prob     = self._probs.get(sid, 0.0)
        count    = 0
        if self._hr_df is not None and not self._hr_df.empty:
            count = int((self._hr_df["section_id"] == sid).sum())

        if match:
            _, _, a_min, a_max, r_in, r_out = match
            lines = [
                f"Section : {sid}",
                f"Angles  : {a_min}° to {a_max}°",
                f"Depth   : {r_in}–{r_out} ft past wall",
                f"",
                f"HR Count: {count}",
                f"Prob.   : {prob*100:.2f}%",
                f"",
                f"(Click a section on the",
                f" map to inspect it.)",
            ]
        else:
            lines = [f"Section : {sid}", f"HR Count: {count}", f"Prob.   : {prob*100:.2f}%"]

        self._set_info("\n".join(lines))

    def _on_plot_click(self, event) -> None:
        if event.inaxes != self._ax:
            return
        if not self._stadium_info:
            return
        info = self._stadium_info
        sid = viz.section_at_point(
            event.xdata, event.ydata,
            info["lf"], info["cf"], info["rf"],
            stadium_name=self._stadium_var.get(),
        )
        if sid:
            self._section_var.set(sid)
            self._highlight_section_id(sid)

    # ------------------------------------------------------------------
    # Redraw
    # ------------------------------------------------------------------

    def _redraw(self) -> None:
        if not self._stadium_info:
            return
        info = self._stadium_info
        # Remove old colorbar if any
        if self._cbar is not None:
            try:
                self._cbar.remove()
            except Exception:
                pass
            self._cbar = None

        self._cbar = viz.draw_heatmap(
            self._ax,
            lf=info["lf"], cf=info["cf"], rf=info["rf"],
            stadium_name=self._current_stadium,
            probabilities=self._probs,
            hr_df=self._hr_df,
            highlight_section=self._highlight_section,
            title=self._current_title,
            total_hrs=len(self._hr_df) if self._hr_df is not None else 0,
        )
        self._canvas.draw_idle()

    def _clear(self) -> None:
        self._hr_df               = None
        self._probs               = {}
        self._highlight_section   = None
        self._current_title       = ""
        self._current_stadium     = ""
        self._section_var.set("")
        self._set_info("")
        self._set_status("Cleared.")

        if self._cbar is not None:
            try:
                self._cbar.remove()
            except Exception:
                pass
            self._cbar = None

        if self._stadium_info:
            info = self._stadium_info
            name = self._stadium_var.get()
            viz.draw_empty_stadium(
                self._ax, info["lf"], info["cf"], info["rf"],
                stadium_name=name, title=name,
            )
        else:
            self._ax.cla()
            self._ax.axis("off")
        self._canvas.draw_idle()

    # ------------------------------------------------------------------
    # Queue polling (result dispatcher)
    # ------------------------------------------------------------------

    def _start_polling(self) -> None:
        self._pending_tasks += 1
        if self._poll_id is None:
            self._poll_id = self.after(100, self._poll_queue)

    def _poll_queue(self) -> None:
        self._poll_id = None
        processed = 0
        while not self._data_queue.empty() and processed < 5:
            kind, payload = self._data_queue.get_nowait()
            processed += 1
            # Every result completes exactly one pending task
            self._pending_tasks = max(0, self._pending_tasks - 1)

            if kind == "teams":
                self._teams = payload
                self._set_status("Teams loaded. Select a stadium to begin.")
                # If stadium already selected, populate team dropdown
                if self._stadium_var.get():
                    self._on_stadium_selected()

            elif kind == "roster":
                self._roster = payload
                names = ["All Players"] + [p["full_name"] for p in payload]
                self._player_cb["values"] = names
                self._player_cb.set("All Players")
                self._set_status(f"Roster loaded ({len(payload)} players).")

            elif kind == "heatmap":
                p = payload
                self._hr_df            = p["hr_df"]
                self._probs            = p["probs"]
                self._current_title    = p["title"]
                self._current_stadium  = p["stadium_name"]
                self._gen_btn.configure(state=tk.NORMAL)
                self._redraw()
                self._set_status(
                    f"Done. {p['total']} HRs plotted for {p['title']}.", ok=True
                )
                self._set_info_table()

            elif kind == "warning":
                self._gen_btn.configure(state=tk.NORMAL)
                self._set_status(payload, error=True)
                messagebox.showwarning("No Data", payload)

            elif kind == "error":
                self._gen_btn.configure(state=tk.NORMAL)
                self._set_status(f"Error: {payload}", error=True)
                messagebox.showerror("Error", payload)

        # Keep polling as long as background tasks are still in-flight
        if self._pending_tasks > 0 or not self._data_queue.empty():
            self._poll_id = self.after(100, self._poll_queue)

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _set_status(self, msg: str, dim=False, ok=False, error=False) -> None:
        self._status_var.set(f"  {msg}")
        if error:
            self._status_label.configure(fg=ERR_FG)
        elif ok:
            self._status_label.configure(fg=OK_FG)
        else:
            self._status_label.configure(fg=FG_DIM)

    def _set_info(self, text: str) -> None:
        self._info_text.configure(state=tk.NORMAL)
        self._info_text.delete("1.0", tk.END)
        self._info_text.insert(tk.END, text)
        self._info_text.configure(state=tk.DISABLED)

    def _set_info_table(self) -> None:
        if not self._probs:
            return
        lines = [f"{'Section':<8} {'Count':>6}  {'Prob':>7}"]
        lines.append("-" * 25)
        if self._hr_df is not None and not self._hr_df.empty:
            counts = self._hr_df["section_id"].value_counts()
        else:
            counts = {}

        sections = get_sections(self._stadium_var.get())
        sorted_sections = sorted(sections, key=lambda s: self._probs.get(s[0], 0), reverse=True)
        for sid, _lbl, *_ in sorted_sections:
            prob  = self._probs.get(sid, 0.0)
            cnt   = int(counts.get(sid, 0)) if hasattr(counts, "get") else 0
            lines.append(f"{sid:<8} {cnt:>6}  {prob*100:>6.2f}%")

        self._set_info("\n".join(lines))
