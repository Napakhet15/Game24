# game24ui.py Game 24 Complete UI

import ast as _ast
import itertools
import math
import operator
import os
import random
import re
import sys
import time
import tkinter as tk
from tkinter import messagebox

import customtkinter as ctk

# Path setup

_HERE   = os.path.dirname(os.path.abspath(__file__))
_SRCDIR = os.path.join(_HERE, "src")
sys.path.insert(0, _SRCDIR if os.path.isdir(_SRCDIR) else _HERE)

# Backend

try:
    from auth       import AuthManager, UserStore
    from scoreboard import ScoreboardManager
    BACKEND = True
except ImportError:
    BACKEND = False

try:
    from game_session       import GameSession
    from math_engine        import MathEngine
    from expression_builder import ExpressionBuilder
    GAME_BACKEND = True
except ImportError:
    GAME_BACKEND = False

    # ExpressionBuilder
    class ExpressionBuilder:
        def __init__(self):
            self._tokens = []

        def add_token(self, t):
            self._tokens.append(t)

        def undo(self):
            if self._tokens:
                self._tokens.pop()

        def clear(self):
            self._tokens.clear()

        def get_expression(self):
            return "".join(self._tokens)

        def get_display(self):
            return " ".join(self._tokens)

        def is_empty(self):
            return not self._tokens

        def token_count(self):
            return len(self._tokens)

try:
    from game_stats import StatisticsManager
    STATS_BACKEND = True
except ImportError:
    try:
        from statistics import StatisticsManager
        STATS_BACKEND = True
    except ImportError:
        STATS_BACKEND = False

try:
    from achievements import AchievementManager
    ACH_BACKEND = True
except ImportError:
    ACH_BACKEND = False

# stack

try:
    import pandas as pd
    import numpy as np
    import matplotlib
    matplotlib.use("TkAgg")
    import matplotlib.pyplot as plt
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    import seaborn as sns
    LIBS_OK  = True
    LIBS_ERR = ""
except ImportError as _e:
    LIBS_OK  = False
    LIBS_ERR = str(_e)

# Pygame sounds
try:
    import pygame as _pg
    _pg.mixer.init()
    _PG = True
except Exception:
    _PG = False

# Theme

ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

# Colour tokens

C = {
    "primary":        "#534AB7",
    "primary_bg":     "#F4F3FC",
    "primary_light":  "#EEEDFE",
    "primary_border": "#CECBF6",
    "body_bg":        "#E8E8F0",
    "card_bg":        "#FFFFFF",
    "text_dark":      "#1a1a2e",
    "text_mid":       "#555",
    "text_muted":     "#888",
    "text_light":     "#aaa",
    "text_xlight":    "#bbb",
    "border":         "#ddd",
    "input_bg":       "#fafafa",
    "green":          "#3B6D11",
    "green_bg":       "#EAF3DE",
    "red":            "#A32D2D",
    "red_bg":         "#FFF0F0",
    "red_border":     "#FFCFCF",
    "amber":          "#854F0B",
    "amber_dark":     "#BA7517",
    "amber_bg":       "#FAEEDA",
    "blue":           "#185FA5",
    "blue_bg":        "#E6F1FB",
    "gray":           "#5F5E5A",
    "gray_bg":        "#F1EFE8",
    "tbl_hdr_bg":     "#EDE9FE",
    "tbl_hdr_text":   "#5B21B6",
    "tbl_fc_bg":      "#F4F3FC",
    "tbl_fc_text":    "#534AB7",
    "tbl_alt":        "#F9FAFB",
}

MPL = {
    "bg":       "#FFFFFF",
    "axes_bg":  "#FFFFFF",
    "grid":     "#F0F0F0",
    "spine":    "#E5E5E5",
    "tick":     "#888888",
    "label":    "#888888",
    "purple":   "#8B5CF6",
    "purple_e": "#6D28D9",
    "blue":     "#2563EB",
    "blue_lt":  "#60A5FA",
    "dot_edge": "#1E3A8A",
}

AVATARS = [
    "🐱", "🐶", "🦊", "🐻", "🐼", "🐨", "🐯", "🦁",
    "🐸", "🐙", "🦋", "🐬", "🦄", "🐲", "🦊", "🐧",
]

MODES = [
    {"key": "classic",  "icon": "🎯", "name": "Classic",  "desc": "4 numbers · target 24 · no time limit",      "badge": "Easy",   "color": C["green"],      "bg": C["green_bg"]},
    {"key": "speed",    "icon": "⚡", "name": "Speed",    "desc": "4 numbers · target 24 · 30 sec countdown",   "badge": "Medium", "color": C["red"],        "bg": C["red_bg"]},
    {"key": "hard",     "icon": "🔥", "name": "Hard",     "desc": "4 numbers · target 24 · random condition",   "badge": "Hard",   "color": C["amber_dark"], "bg": C["amber_bg"]},
    {"key": "advanced", "icon": "🧠", "name": "Advanced", "desc": "5 numbers · target 24 · ^ and √ allowed",    "badge": "Expert", "color": C["blue"],       "bg": C["blue_bg"]},
    {"key": "practice", "icon": "📖", "name": "Practice", "desc": "No score · unlimited hints · no time limit", "badge": "Free",   "color": C["gray"],       "bg": C["gray_bg"]},
]

MODE_META = {
    "classic":  {"label": "Classic",  "color": C["green"],      "bg": C["green_bg"],  "border": "#4CAF50"},
    "speed":    {"label": "Speed",    "color": C["red"],        "bg": C["red_bg"],    "border": "#E24B4A"},
    "hard":     {"label": "Hard",     "color": C["amber_dark"], "bg": C["amber_bg"],  "border": "#F5C842"},
    "advanced": {"label": "Advanced", "color": C["blue"],       "bg": C["blue_bg"],   "border": "#185FA5"},
    "practice": {"label": "Practice", "color": C["gray"],       "bg": C["gray_bg"],   "border": "#888780"},
}

MODE_CONFIGS = {
    "classic":  {"num_count": 4, "num_range": (1, 9), "target_range": (24, 24), "advanced": False},
    "speed":    {"num_count": 4, "num_range": (1, 9), "target_range": (24, 24), "advanced": False},
    "hard":     {"num_count": 4, "num_range": (1, 9), "target_range": (24, 24), "advanced": False},
    "advanced": {"num_count": 5, "num_range": (1, 9), "target_range": (24, 24), "advanced": True},
    "practice": {"num_count": 4, "num_range": (1, 9), "target_range": (24, 24), "advanced": False},
}

SPEED_LIMIT = 30

HARD_CONDITIONS = [
    {"id": "must_div",     "text": "Must use division (÷)",      "short": "Must use ÷",      "check": lambda e: "÷" in e or "/" in e},
    {"id": "no_mul",       "text": "No multiplication (×)",      "short": "No ×",            "check": lambda e: "×" not in e and "*" not in e},
    {"id": "must_sub",     "text": "Must use subtraction (−)",   "short": "Must use −",      "check": lambda e: "−" in e or "-" in e},
    {"id": "no_add",       "text": "No addition (+)",            "short": "No +",            "check": lambda e: "+" not in e},
    {"id": "must_mul",     "text": "Must use multiplication (×)", "short": "Must use ×",     "check": lambda e: "×" in e or "*" in e},
    {"id": "must_div_mul", "text": "Must use both × and ÷",      "short": "Must use × and ÷","check": lambda e: ("×" in e or "*" in e) and ("÷" in e or "/" in e)},
]

# Achievement

ACH_CATALOGUE = [
    {"id": "first_blood",       "icon": "🩸", "name": "First Blood",       "desc": "Win your first game"},
    {"id": "hot_streak",        "icon": "🔥", "name": "Hot Streak",        "desc": "3 consecutive wins"},
    {"id": "no_hint_master",    "icon": "💡", "name": "No Hint Master",    "desc": "10 wins without hints"},
    {"id": "getting_warmed_up", "icon": "🏃", "name": "Getting Warmed Up", "desc": "Play 10 total games"},
    {"id": "diamond_mind",      "icon": "💎", "name": "Diamond Mind",      "desc": "Accumulate 5,000 total score"},
    {"id": "all_rounder",       "icon": "🌀", "name": "All Rounder",       "desc": "Win in every mode at least once"},
    {"id": "marathon",          "icon": "🏅", "name": "Marathon",          "desc": "Play 50 total games"},
    {"id": "unbreakable",       "icon": "🛡", "name": "Unbreakable",       "desc": "Win rate ≥ 75% over 20+ games"},
]

# Demo data 

_SB_DEMO = [
    {"username": "mathwiz",    "score": 245, "mode": "classic"},
    {"username": "speedking",  "score": 221, "mode": "speed"},
    {"username": "puzzleace",  "score": 198, "mode": "hard"},
    {"username": "prodigy42",  "score": 185, "mode": "advanced"},
    {"username": "quickmind",  "score": 172, "mode": "classic"},
    {"username": "calcmaster", "score": 160, "mode": "speed"},
    {"username": "genius99",   "score": 148, "mode": "hard"},
    {"username": "numbernerd", "score": 133, "mode": "classic"},
    {"username": "algebrax",   "score": 121, "mode": "advanced"},
    {"username": "flashcalc",  "score": 109, "mode": "speed"},
    {"username": "thinker77",  "score":  98, "mode": "classic"},
    {"username": "riddle_fan", "score":  87, "mode": "hard"},
]

_AV_POOL = ["🦊", "🐼", "🦁", "🐯", "🦋", "🐬", "🦄", "🐧", "🐸", "🐙", "🐻", "🐱", "🐶", "🐨", "🦊", "🐲"]

_STATS_DEMO = [
    {"attempts": 2, "hints_used": 0, "won": 1, "time_used": 14.2, "mode": "classic",  "score": 142},
    {"attempts": 3, "hints_used": 1, "won": 1, "time_used": 18.5, "mode": "speed",    "score":  98},
    {"attempts": 1, "hints_used": 0, "won": 1, "time_used":  9.3, "mode": "classic",  "score": 162},
    {"attempts": 4, "hints_used": 0, "won": 0, "time_used": 22.1, "mode": "hard",     "score":   0},
    {"attempts": 3, "hints_used": 2, "won": 1, "time_used": 11.8, "mode": "classic",  "score":  98},
    {"attempts": 2, "hints_used": 0, "won": 1, "time_used": 16.4, "mode": "advanced", "score": 127},
    {"attempts": 5, "hints_used": 1, "won": 0, "time_used":  8.9, "mode": "speed",    "score":   0},
    {"attempts": 3, "hints_used": 0, "won": 1, "time_used": 13.2, "mode": "classic",  "score": 134},
    {"attempts": 2, "hints_used": 0, "won": 1, "time_used": 20.7, "mode": "hard",     "score": 109},
    {"attempts": 1, "hints_used": 0, "won": 1, "time_used": 17.3, "mode": "classic",  "score": 151},
    {"attempts": 4, "hints_used": 3, "won": 0, "time_used": 12.5, "mode": "speed",    "score":   0},
    {"attempts": 2, "hints_used": 0, "won": 1, "time_used": 15.8, "mode": "advanced", "score": 128},
    {"attempts": 3, "hints_used": 1, "won": 1, "time_used": 10.1, "mode": "classic",  "score": 117},
    {"attempts": 7, "hints_used": 0, "won": 0, "time_used": 19.6, "mode": "hard",     "score":   0},
    {"attempts": 2, "hints_used": 0, "won": 1, "time_used": 14.3, "mode": "speed",    "score": 131},
    {"attempts": 3, "hints_used": 2, "won": 1, "time_used": 11.9, "mode": "classic",  "score":  88},
    {"attempts": 2, "hints_used": 0, "won": 1, "time_used": 16.7, "mode": "advanced", "score": 126},
    {"attempts": 3, "hints_used": 1, "won": 1, "time_used": 13.4, "mode": "classic",  "score": 111},
    {"attempts": 1, "hints_used": 0, "won": 1, "time_used": 18.2, "mode": "speed",    "score": 144},
    {"attempts": 4, "hints_used": 0, "won": 0, "time_used": 12.0, "mode": "hard",     "score":   0},
]

# Sound helpers

def _beep(freq=660, dur=0.05, vol=8000):
    if not _PG:
        return
    try:
        t = np.linspace(0, dur, int(22050 * dur), False)
        w = (np.sin(2 * math.pi * freq * t) * vol * (1 - t / dur)).astype(np.int16)
        _pg.sndarray.make_sound(np.column_stack([w, w])).play()
    except Exception:
        pass


def play_hint():
    _beep(600, 0.08, 6000)


def play_timeout():
    _beep(300, 0.25, 9000)


def play_achievement():
    if not _PG:
        return
    try:
        sr     = 22050
        frames = []
        for f, d in [(784, 0.08), (1047, 0.15)]:
            t = np.linspace(0, d, int(sr * d), False)
            frames.append((np.sin(2 * math.pi * f * t) * 10000 * np.exp(-t * 8)).astype(np.int16))
        full = np.concatenate(frames)
        _pg.sndarray.make_sound(np.column_stack([full, full])).play()
    except Exception:
        pass


def play_click():
    _beep(880, 0.04, 7000)


def play_success():
    if not _PG:
        return
    try:
        sr     = 22050
        frames = []
        for f, d in [(523, 0.09), (659, 0.09), (784, 0.14)]:
            t = np.linspace(0, d, int(sr * d), False)
            frames.append((np.sin(2 * math.pi * f * t) * 11000 * np.exp(-t * 9)).astype(np.int16))
        full = np.concatenate(frames)
        _pg.sndarray.make_sound(np.column_stack([full, full])).play()
    except Exception:
        pass


def play_tap():
    _beep(800, 0.04, 7000)


def play_correct():
    play_success()


def play_wrong():
    _beep(220, 0.12, 9000)


def play_tick():
    _beep(1100, 0.025, 4000)

# widget helpers

class RoundedCard(ctk.CTkFrame):
    def __init__(self, p, **kw):
        kw.setdefault("fg_color", C["card_bg"])
        kw.setdefault("corner_radius", 20)
        super().__init__(p, **kw)


def _lbl(p, text, size=13, bold=False, color=None, **kw):
    return ctk.CTkLabel(
        p,
        text=text,
        font=ctk.CTkFont("Segoe UI", size, weight="bold" if bold else "normal"),
        text_color=color or C["text_dark"],
        **kw,
    )


def _field_label(p, text):
    return ctk.CTkLabel(
        p,
        text=text.upper(),
        font=ctk.CTkFont("Segoe UI", 11, weight="bold"),
        text_color=C["text_muted"],
        anchor="w",
    )


def _entry(p, **kw):
    kw.setdefault("fg_color", C["input_bg"])
    kw.setdefault("border_color", C["border"])
    kw.setdefault("text_color", C["text_dark"])
    kw.setdefault("font", ctk.CTkFont("Segoe UI", 14))
    kw.setdefault("height", 42)
    kw.setdefault("corner_radius", 8)
    return ctk.CTkEntry(p, **kw)


def _btn_primary(p, text, cmd=None, **kw):
    kw.setdefault("fg_color", C["primary"])
    kw.setdefault("hover_color", "#3f37a0")
    kw.setdefault("text_color", "#fff")
    kw.setdefault("font", ctk.CTkFont("Segoe UI", 15, weight="bold"))
    kw.setdefault("height", 46)
    kw.setdefault("corner_radius", 10)
    return ctk.CTkButton(p, text=text, command=cmd, **kw)


def _btn_secondary(p, text, cmd=None, **kw):
    kw.setdefault("fg_color", "transparent")
    kw.setdefault("hover_color", C["primary_bg"])
    kw.setdefault("text_color", C["primary"])
    kw.setdefault("border_color", C["primary"])
    kw.setdefault("border_width", 2)
    kw.setdefault("font", ctk.CTkFont("Segoe UI", 14, weight="bold"))
    kw.setdefault("height", 42)
    kw.setdefault("corner_radius", 10)
    return ctk.CTkButton(p, text=text, command=cmd, **kw)


def _btn_ghost(p, text, cmd=None, **kw):
    kw.setdefault("fg_color", "transparent")
    kw.setdefault("hover_color", "#f5f5f5")
    kw.setdefault("text_color", C["text_muted"])
    kw.setdefault("border_color", C["border"])
    kw.setdefault("border_width", 1)
    kw.setdefault("font", ctk.CTkFont("Segoe UI", 13))
    kw.setdefault("height", 38)
    kw.setdefault("corner_radius", 9)
    return ctk.CTkButton(p, text=text, command=cmd, **kw)


def _btn_back(p, cmd=None):
    return ctk.CTkButton(
        p,
        text="← Back",
        command=cmd,
        font=ctk.CTkFont("Segoe UI", 13, weight="bold"),
        fg_color=C["primary_bg"],
        hover_color=C["primary_light"],
        text_color=C["primary"],
        border_width=0,
        height=34,
        width=90,
        corner_radius=8,
    )


def _scrollable(p):
    return ctk.CTkScrollableFrame(
        p,
        fg_color="transparent",
        scrollbar_button_color=C["primary_border"],
        scrollbar_button_hover_color=C["primary"],
    )


def _section_lbl(p, text):
    ctk.CTkLabel(
        p,
        text=text,
        font=ctk.CTkFont("Segoe UI", 10, weight="bold"),
        text_color=C["text_light"],
        anchor="w",
    ).pack(fill="x", padx=20, pady=(6, 3))


def _divider(p, padx=20, pady=4):
    ctk.CTkFrame(p, fg_color=C["border"], height=1).pack(fill="x", padx=padx, pady=pady)


def _spacer(p, h=6):
    ctk.CTkFrame(p, fg_color="transparent", height=h).pack()


def _get_username(app):
    try:
        if app.auth and app.auth.current_user:
            return app.auth.current_user.username
    except Exception:
        pass
    if hasattr(app, "demo_user") and app.demo_user:
        return app.demo_user.get("username", "")
    return ""

# math engine

class _MathEngine:
    def __init__(self, advanced=False):
        self.advanced = advanced

    def evaluate(self, expr):
        import ast as A
        import operator as O

        expr = expr.replace("^", "**")
        try:
            tree = A.parse(expr, mode="eval")
        except SyntaxError:
            raise ValueError(f"Invalid syntax: {expr}")
        return self._ev(tree.body)

    def _ev(self, n):
        import ast as A
        import operator as O

        if isinstance(n, A.Constant) and isinstance(n.value, (int, float)):
            return float(n.value)

        if isinstance(n, A.BinOp):
            ops = {
                A.Add:  O.add,
                A.Sub:  O.sub,
                A.Mult: O.mul,
                A.Div:  O.truediv,
                A.Pow:  O.pow,
            }
            t = type(n.op)
            if t not in ops:
                raise ValueError(f"Unsupported op {t}")
            left  = self._ev(n.left)
            right = self._ev(n.right)
            if t == A.Div and abs(right) < 1e-9:
                raise ValueError("Division by zero")
            return ops[t](left, right)

        if isinstance(n, A.UnaryOp):
            if isinstance(n.op, A.USub):
                return -self._ev(n.operand)
            if isinstance(n.op, A.UAdd):
                return self._ev(n.operand)

        if isinstance(n, A.Call) and self.advanced:
            if isinstance(n.func, A.Name) and n.func.id == "sqrt":
                a = self._ev(n.args[0])
                if a < 0:
                    raise ValueError("sqrt of negative")
                return math.sqrt(a)

        raise ValueError(f"Unsupported node {type(n)}")

    def equals_target(self, expr, target):
        try:
            return abs(self.evaluate(expr) - target) < 1e-6
        except Exception:
            return False

# PAGE 1 Register 

class RegisterPage(RoundedCard):
    def __init__(self, p, app, **kw):
        super().__init__(p, **kw)
        self.app      = app
        self._av_btns = []
        self._av      = "🐱"
        self._build()

    def _build(self):
        _lbl(self, "Create account", 22, True).pack(pady=(28, 2))
        _lbl(self, "Join the puzzle", 13, color=C["text_light"]).pack(pady=(0, 20))

        _field_label(self, "username").pack(fill="x", padx=28)
        self._u = _entry(self, placeholder_text="Choose a username")
        self._u.pack(fill="x", padx=28, pady=(4, 12))

        _field_label(self, "password").pack(fill="x", padx=28)
        self._p = _entry(self, placeholder_text="Choose a password", show="•")
        self._p.pack(fill="x", padx=28, pady=(4, 14))

        _field_label(self, "pick avatar").pack(fill="x", padx=28)
        g = ctk.CTkFrame(self, fg_color="transparent")
        g.pack(fill="x", padx=28, pady=(6, 0))
        for i in range(8):
            g.columnconfigure(i, weight=1)

        for i, em in enumerate(AVATARS):
            b = ctk.CTkButton(
                g,
                text=em,
                width=38,
                height=38,
                font=ctk.CTkFont("Segoe UI", 18),
                fg_color="transparent",
                hover_color=C["primary_light"],
                border_color=C["card_bg"],
                border_width=2,
                corner_radius=8,
                text_color=C["text_dark"],
                command=lambda e=em, idx=i: self._sel(e, idx),
            )
            b.grid(row=i // 8, column=i % 8, padx=2, pady=2)
            self._av_btns.append(b)

        self._av_lbl = _lbl(self, f"Selected: {self._av}", 13, color=C["text_light"])
        self._av_lbl.pack(pady=(8, 16))
        self._sel("🐱", 0)

        self._err = ctk.CTkLabel(self, text="", font=ctk.CTkFont("Segoe UI", 12), text_color=C["red"])
        self._err.pack(pady=(0, 4))

        _btn_primary(self, "Create account", self._go).pack(fill="x", padx=28, pady=(0, 10))

        fr = ctk.CTkFrame(self, fg_color="transparent")
        fr.pack(pady=(0, 22))
        _lbl(fr, "Have account? ", 13, color=C["text_light"]).pack(side="left")
        lk = _lbl(fr, "Login", 13, True, color=C["primary"])
        lk.pack(side="left")
        lk.configure(cursor="hand2")
        lk.bind("<Button-1>", lambda e: self.app.show_page("login"))

    def _sel(self, em, idx):
        self._av = em
        self._av_lbl.configure(text=f"Selected: {em}")
        for i, b in enumerate(self._av_btns):
            b.configure(
                fg_color=C["primary_light"] if i == idx else C["card_bg"],
                border_color=C["primary"] if i == idx else C["card_bg"],
            )

    def _go(self):
        u  = self._u.get().strip()
        pw = self._p.get().strip()

        if len(u) < 3:
            self._err.configure(text="⚠ Username must be ≥ 3 chars")
            return
        if len(pw) < 4:
            self._err.configure(text="⚠ Password must be ≥ 4 chars")
            return

        self._err.configure(text="")

        if BACKEND:
            try:
                self.app.auth.register(u, pw)
                self.app.auth.login(u, pw)
                self.app.current_user_avatar = self._av
                play_success()
                self.app.show_page("mode_select")
            except ValueError as e:
                self._err.configure(text=f"⚠ {e}")
        else:
            self.app.demo_user = {"username": u, "avatar": self._av, "score": 0}
            self.app.current_user_avatar = self._av
            play_success()
            self.app.show_page("mode_select")

# PAGE 2 Login

class LoginPage(RoundedCard):
    def __init__(self, p, app, **kw):
        super().__init__(p, **kw)
        self.app = app
        self._build()

    def _build(self):
        _lbl(self, "Welcome back", 22, True).pack(pady=(28, 2))
        _lbl(self, "Enter your credentials to continue", 13, color=C["text_light"]).pack(pady=(0, 22))

        _field_label(self, "username").pack(fill="x", padx=28)
        self._u = _entry(self, placeholder_text="Your username")
        self._u.pack(fill="x", padx=28, pady=(4, 14))

        _field_label(self, "password").pack(fill="x", padx=28)
        self._p = _entry(self, placeholder_text="Your password", show="•")
        self._p.pack(fill="x", padx=28, pady=(4, 16))

        self._err = ctk.CTkLabel(self, text="", font=ctk.CTkFont("Segoe UI", 12), text_color=C["red"])
        self._err.pack(pady=(0, 4))

        _btn_primary(self, "Login", self._go).pack(fill="x", padx=28, pady=(0, 10))

        fr = ctk.CTkFrame(self, fg_color="transparent")
        fr.pack(pady=(0, 22))
        _lbl(fr, "No account? ", 13, color=C["text_light"]).pack(side="left")
        lk = _lbl(fr, "Create one", 13, True, color=C["primary"])
        lk.pack(side="left")
        lk.configure(cursor="hand2")
        lk.bind("<Button-1>", lambda e: self.app.show_page("register"))

        self._u.bind("<Return>", lambda e: self._p.focus())
        self._p.bind("<Return>", lambda e: self._go())

    def refresh(self):
        try:
            self._u.delete(0, "end")
            self._p.delete(0, "end")
            self._err.configure(text="")
        except Exception:
            pass

    def _go(self):
        u  = self._u.get().strip()
        pw = self._p.get().strip()

        if not u or not pw:
            self._err.configure(text="⚠ Fill in all fields")
            return

        self._err.configure(text="")

        if BACKEND:
            if self.app.auth.login(u, pw):
                play_success()
                self.app.show_page("mode_select")
            else:
                self._err.configure(text="⚠ Invalid username or password")
        else:
            self.app.demo_user = {"username": u, "avatar": "🐱", "score": 842}
            self.app.current_user_avatar = "🐱"
            play_success()
            self.app.show_page("mode_select")

# PAGE 3 Mode Select

class ModeSelectPage(RoundedCard):
    def __init__(self, p, app, **kw):
        super().__init__(p, **kw)
        self.app = app
        self._build()

    def _build(self):
        f = ctk.CTkFrame(self, fg_color="transparent")
        f.pack(fill="both", expand=True, padx=4, pady=4)

        # user info row
        ur = ctk.CTkFrame(f, fg_color="transparent")
        ur.pack(fill="x", padx=20, pady=(10, 8))

        self._av = ctk.CTkLabel(
            ur,
            text=self.app.current_user_avatar or "🐱",
            font=ctk.CTkFont("Segoe UI", 22),
            width=44,
            height=44,
            fg_color=C["primary_bg"],
            corner_radius=22,
            text_color=C["text_dark"],
        )
        self._av.pack(side="left", padx=(0, 10))

        inf = ctk.CTkFrame(ur, fg_color="transparent")
        inf.pack(side="left", fill="x", expand=True)
        self._un     = _lbl(inf, _get_username(self.app), 15, True, anchor="w")
        self._un.pack(fill="x")
        self._sc_lbl = _lbl(inf, "Total score: 0", 12, color=C["text_light"], anchor="w")
        self._sc_lbl.pack(fill="x")

        _lbl(f, "SELECT MODE", 11, True, color=C["text_light"], anchor="w").pack(fill="x", padx=22, pady=(0, 4))

        for m in MODES:
            if m["key"] == "practice":
                _divider(f, 22, (4, 10))
            self._mode_card(f, m)

        # nav buttons row
        nr = ctk.CTkFrame(f, fg_color="transparent")
        nr.pack(fill="x", padx=20, pady=(6, 0))
        for i in range(3):
            nr.columnconfigure(i, weight=1)

        nav_items = [
            ("🏆 Scoreboard",   "scoreboard"),
            ("📊 Statistics",   "statistics"),
            ("🎖 Achievements", "achievements"),
        ]
        for ci, (lbl, key) in enumerate(nav_items):
            ctk.CTkButton(
                nr,
                text=lbl,
                font=ctk.CTkFont("Segoe UI", 11, weight="bold"),
                fg_color="transparent",
                hover_color=C["primary_bg"],
                text_color=C["primary"],
                border_color=C["primary_border"],
                border_width=1,
                height=38,
                corner_radius=10,
                command=lambda k=key: self.app.show_page(k),
            ).grid(row=0, column=ci, padx=3, sticky="ew")

        # util row
        uf = ctk.CTkFrame(f, fg_color="transparent")
        uf.pack(fill="x", padx=20, pady=(4, 10))
        uf.columnconfigure((0, 1), weight=1)

        ctk.CTkButton(
            uf,
            text="📖 Guide",
            font=ctk.CTkFont("Segoe UI", 11, weight="bold"),
            fg_color=C["primary_bg"],
            hover_color=C["primary_light"],
            text_color=C["primary"],
            border_width=0,
            height=38,
            corner_radius=10,
            command=lambda: self.app.show_page("guide"),
        ).grid(row=0, column=0, padx=(0, 4), sticky="ew")

        ctk.CTkButton(
            uf,
            text="🚪 Exit",
            font=ctk.CTkFont("Segoe UI", 11, weight="bold"),
            fg_color=C["red_bg"],
            hover_color="#ffe0e0",
            text_color=C["red"],
            border_width=0,
            height=38,
            corner_radius=10,
            command=self.app._logout,
        ).grid(row=0, column=1, padx=(4, 0), sticky="ew")

    def _mode_card(self, p, m):
        card = ctk.CTkFrame(p, fg_color=C["card_bg"], border_color="#eee", border_width=2, corner_radius=14)
        card.pack(fill="x", padx=20, pady=2)

        inn = ctk.CTkFrame(card, fg_color="transparent")
        inn.pack(fill="both", expand=True, padx=14, pady=8)
        inn.columnconfigure(1, weight=1)

        icon = ctk.CTkLabel(
            inn,
            text=m["icon"],
            font=ctk.CTkFont("Segoe UI", 24),
            width=48,
            height=48,
            fg_color=m["bg"],
            corner_radius=12,
            text_color=m["color"],
        )
        icon.grid(row=0, column=0, rowspan=2, padx=(0, 14), sticky="ns")

        nm = _lbl(inn, m["name"], 15, True, color=m["color"], anchor="w")
        nm.grid(row=0, column=1, sticky="sw", pady=(2, 0))

        dc = _lbl(inn, m["desc"], 11, color=C["text_muted"], anchor="w")
        dc.grid(row=1, column=1, sticky="nw", pady=(0, 2))

        bf = ctk.CTkFrame(inn, fg_color="transparent")
        bf.grid(row=0, column=2, rowspan=2, padx=(10, 0), sticky="e")
        ctk.CTkLabel(
            bf,
            text=m["badge"],
            font=ctk.CTkFont("Segoe UI", 10, weight="bold"),
            fg_color=m["bg"],
            text_color=m["color"],
            corner_radius=20,
            width=60,
            height=22,
        ).pack()

        for w in [card, inn, icon, nm, dc]:
            w.bind("<Button-1>", lambda e, k=m["key"]: self._pick(k))
            w.bind("<Enter>",    lambda e, c=card: c.configure(border_color=C["primary_border"]))
            w.bind("<Leave>",    lambda e, c=card: c.configure(border_color="#eee"))

    def _pick(self, k):
        play_click()
        self.app.selected_mode = k
        self.app.show_page("game")

    def refresh(self):
        try:
            self._av.configure(text=self.app.current_user_avatar or "🐱")
            self._un.configure(text=_get_username(self.app))
            total = 0
            if BACKEND:
                try:
                    uname = _get_username(self.app)
                    raw   = ScoreboardManager()._load() or []
                    total = sum(e.get("score", 0) for e in raw if e.get("username", "") == uname)
                except Exception:
                    pass
            self._sc_lbl.configure(text=f"Total score: {total}")
        except Exception:
            pass

# PAGE 4 Guide

class GuidePage(RoundedCard):
    def __init__(self, p, app, **kw):
        super().__init__(p, **kw)
        self.app = app
        self._build()

    def _build(self):
        sc = _scrollable(self)
        sc.pack(fill="both", expand=True, padx=4, pady=4)
        f = sc

        _btn_back(f, lambda: self.app.show_page("mode_select")).pack(anchor="w", padx=20, pady=(14, 10))
        _lbl(f, "📖", 36).pack(pady=(0, 4))
        _lbl(f, "How to play", 20, True).pack()
        _lbl(f, "Master the 24 game", 13, color=C["text_light"]).pack(pady=(2, 18))

        steps = [
            ("You get 4 numbers",      "Four random numbers between 1-9 are shown on tiles."),
            ("Build a math expression", "Tap numbers and operators to build your equation."),
            ("Hit the target",          "Your expression must equal exactly 24."),
            ("Score more points",       "Be fast, fewer attempts, skip hints to maximize score!"),
        ]
        for i, (t, d) in enumerate(steps, 1):
            sf = ctk.CTkFrame(f, fg_color="transparent")
            sf.pack(fill="x", padx=20, pady=4)
            ctk.CTkLabel(
                sf,
                text=str(i),
                font=ctk.CTkFont("Segoe UI", 13, weight="bold"),
                width=28,
                height=28,
                fg_color=C["primary"],
                text_color="#fff",
                corner_radius=14,
            ).pack(side="left", anchor="n", pady=2)
            tf = ctk.CTkFrame(sf, fg_color="transparent")
            tf.pack(side="left", fill="x", expand=True, padx=(12, 0))
            _lbl(tf, t, 14, True, anchor="w").pack(fill="x")
            _lbl(tf, d, 12, color=C["text_muted"], anchor="w").pack(fill="x")

        # example box
        eb = ctk.CTkFrame(f, fg_color=C["primary_bg"], corner_radius=12)
        eb.pack(fill="x", padx=20, pady=(16, 8))
        _lbl(eb, "EXAMPLE", 10, True, color=C["primary"]).pack(pady=(12, 8))
        tf2 = ctk.CTkFrame(eb, fg_color="transparent")
        tf2.pack(pady=(0, 10))
        for n in ["8", "3", "6", "1"]:
            wrap = ctk.CTkFrame(tf2, fg_color="#fff", border_color=C["primary_border"], border_width=2, corner_radius=10, width=44, height=44)
            wrap.pack(side="left", padx=4)
            wrap.pack_propagate(False)
            ctk.CTkLabel(wrap, text=n, font=ctk.CTkFont("Segoe UI", 18, weight="bold"), text_color=C["primary"]).place(relx=0.5, rely=0.5, anchor="center")
        _lbl(eb, "(8 − 6 + 1) × 3 = 24  ✓", 14, True, color=C["primary"]).pack(pady=(4, 14))

        # scoring 
        sb = ctk.CTkFrame(f, fg_color=C["primary_light"], corner_radius=10)
        sb.pack(fill="x", padx=20, pady=(4, 8))
        _lbl(sb, "SCORING FORMULA", 10, True, color=C["primary"]).pack(pady=(12, 8))
        formula_rows = [
            ("Base score",       "100 pts"),
            ("Time bonus",       "max(0,30−time)×2"),
            ("Submit penalty",   "−5 pts per extra submit"),
            ("Hint penalty",     "−10 pts per hint"),
            ("Loss / Practice",  "0 pts always"),
        ]
        for i, (k, v) in enumerate(formula_rows):
            rw = ctk.CTkFrame(sb, fg_color="transparent")
            rw.pack(fill="x", padx=14)
            if i < 4:
                ctk.CTkFrame(sb, fg_color=C["primary_border"], height=1).pack(fill="x", padx=14)
            _lbl(rw, k, 12, True, color=C["primary"], anchor="w").pack(side="left", pady=5)
            _lbl(rw, v, 12, color=C["text_muted"], anchor="e").pack(side="right", pady=5)

        # mode tips
        _lbl(f, "MODE TIPS", 11, True, color=C["text_light"]).pack(pady=(16, 8), padx=20, anchor="w")
        tips = [
            ("Classic",  C["green"],      C["green_bg"],  "No time limit — perfect for learning."),
            ("Speed",    C["red"],        C["red_bg"],    "Only 30 seconds! Move fast."),
            ("Hard",     C["amber_dark"], C["amber_bg"],  "Target is always 24, but each puzzle has a random condition — e.g. must use ÷, no ×, must use −."),
            ("Advanced", C["blue"],       C["blue_bg"],   "5 numbers + power ^ and square root √."),
            ("Practice", C["gray"],       C["gray_bg"],   "No score, unlimited hints. Great for exploring!"),
        ]
        for lbl, col, bg, tip in tips:
            tf3 = ctk.CTkFrame(f, fg_color=bg, corner_radius=10, border_color="#eee", border_width=1)
            tf3.pack(fill="x", padx=20, pady=4)
            inn = ctk.CTkFrame(tf3, fg_color="transparent")
            inn.pack(fill="x", padx=12, pady=8)
            ctk.CTkLabel(inn, text=lbl, font=ctk.CTkFont("Segoe UI", 10, weight="bold"), fg_color=bg, text_color=col, corner_radius=10, width=60, height=20).pack(side="left", anchor="n", pady=2)
            _lbl(inn, tip, 12, color="#666", anchor="w", wraplength=260, justify="left").pack(side="left", fill="x", expand=True, padx=(10, 0))

        _spacer(f, 20)

# PAGE 5 Game

class _CountdownRing(tk.Canvas):
    SZ = 72
    TH = 7
    BG = "#FFCFCF"
    FG = "#E24B4A"

    def __init__(self, p, total=30, **kw):
        kw.setdefault("width",  self.SZ)
        kw.setdefault("height", self.SZ)
        kw.setdefault("bg",     C["card_bg"])
        kw.setdefault("highlightthickness", 0)
        super().__init__(p, **kw)
        self.total = total
        self._init_draw(total)

    def set_time(self, rem):
        self.delete("all")
        r   = self.SZ // 2
        pad = self.TH + 2
        x0, y0, x1, y1 = pad, pad, self.SZ - pad, self.SZ - pad
        self.create_arc(x0, y0, x1, y1, start=90, extent=360, outline=self.BG, width=self.TH, style="arc")
        frac = max(0, rem / self.total)
        ext  = 360 * frac
        if ext > 0:
            self.create_arc(x0, y0, x1, y1, start=90, extent=-ext, outline=self.FG, width=self.TH, style="arc")
        col = "#E24B4A" if rem <= 10 else C["text_mid"]
        self.create_text(r, r, text=str(int(rem)), font=("Segoe UI", 18, "bold"), fill=col)

    def _init_draw(self, t):
        self.set_time(t)


class GamePage(ctk.CTkFrame):
    def __init__(self, p, app, **kw):
        kw.setdefault("fg_color",     C["card_bg"])
        kw.setdefault("corner_radius", 20)
        super().__init__(p, **kw)
        self.app = app

        # game state
        self._mode       = "classic"
        self._numbers    = []
        self._target     = 24
        self._used       = set()
        self._builder    = ExpressionBuilder()
        self._attempts   = 0
        self._hints_used = 0
        self._hints_left = 2
        self._start_time = None
        self._elapsed    = 0.0
        self._active     = False
        self._timer_job  = None
        self._condition  = None
        self._session    = None
        self._engine     = None
        self._tile_btns  = []
        self._err_job    = None
        self._last_tick_sec = None

        self._build()

    def start_game(self, mode):
        self._mode      = mode
        self._stop_timer()
        self._active    = False
        self._used.clear()
        self._builder.clear()
        self._attempts      = 0
        self._hints_used    = 0
        self._elapsed       = 0.0
        self._condition     = None
        self._err_job       = None
        self._last_tick_sec = None

        self.app.bind("<Key>", self._on_key)

        meta = MODE_META[mode]
        self._top_border.configure(fg_color=meta["border"])
        self._ring_frame.pack_forget()
        self._prac_bar.pack_forget()
        self._hard_banner.pack_forget()

        if mode == "speed":
            self._ring_frame.pack(after=self._topbar, pady=(0, 6))
            self._ring.set_time(SPEED_LIMIT)

        if mode == "hard":
            self._condition = getattr(self, "_pending_condition", None) or random.choice(HARD_CONDITIONS)
            self._cond_lbl.configure(text=self._condition["text"])
            self._hard_banner.pack(after=self._topbar, fill="x", padx=20, pady=(0, 8))

        if mode == "practice":
            self._prac_bar.pack(after=self._topbar, fill="x", padx=20, pady=(0, 8))

        self._ops2.pack_forget()
        if mode == "advanced":
            self._ops2.pack(after=self._ops1, pady=(0, 6))

        if mode == "speed":
            self._hint_btn.configure(
                text="💡 No hints in Speed mode",
                state="disabled",
                text_color=C["text_xlight"],
                border_color="#eee",
            )
            self._hints_left = 0
        elif mode == "practice":
            self._hint_btn.configure(
                text="💡 Use hint (unlimited)",
                state="normal",
                text_color=C["text_muted"],
                border_color=C["border"],
            )
            self._hints_left = 999
        else:
            self._hints_left = 2
            self._hint_btn.configure(
                text=f"💡 Use hint ({self._hints_left} left)",
                state="normal",
                text_color=C["text_muted"],
                border_color=C["border"],
            )

        self._mode_badge.configure(text=meta["label"], text_color=meta["color"], fg_color=meta["bg"])
        self._timer_lbl.configure(text="—" if mode == "practice" else "0:00", text_color=C["text_light"])

        self._gen_puzzle(mode)
        self._rebuild_tiles()
        self._target_lbl.configure(text=str(self._target))
        self._upd_expr()
        self._clear_err()

        # set up 
        if GAME_BACKEND:
            try:
                cfg = dict(MODE_CONFIGS[mode])
                s   = GameSession(_get_username(self.app), mode, cfg)
                s.numbers      = list(self._numbers)
                s.target       = self._target
                self._start_time = time.time()
                s._start_time  = self._start_time
                s._active      = True
                self._session  = s
                eng = MathEngine(advanced_mode=(mode == "advanced"))
            except Exception:
                eng           = _MathEngine(mode == "advanced")
                self._session = None
        else:
            eng           = _MathEngine(mode == "advanced")
            self._session = None

        if self._start_time is None:
            self._start_time = time.time()

        self._engine = eng
        self._active = True
        self._run_timer()

    def _gen_puzzle(self, mode):
        cfg     = MODE_CONFIGS[mode]
        lo, hi  = cfg["num_range"]
        cnt     = cfg["num_count"]
        adv     = cfg.get("advanced", False)

        if mode == "hard":
            condition = random.choice(HARD_CONDITIONS)
            for _ in range(2000):
                nums = [random.randint(lo, hi) for _ in range(cnt)]
                if self._solvable_with_condition(nums, 24, condition):
                    self._numbers           = nums
                    self._target            = 24
                    self._pending_condition = condition
                    return
            # any solvable puzzle
            for _ in range(500):
                nums = [random.randint(lo, hi) for _ in range(cnt)]
                if self._solvable(nums, 24, adv):
                    self._numbers           = nums
                    self._target            = 24
                    self._pending_condition = condition
                    return
        else:
            self._pending_condition = None
            for _ in range(500):
                nums = [random.randint(lo, hi) for _ in range(cnt)]
                if self._solvable(nums, 24, adv):
                    self._numbers = nums
                    self._target  = 24
                    return

        # absolute
        self._numbers = [2, 3, 4, 1]
        self._target  = 24

    def _solvable_with_condition(self, nums, target, condition):
        ops         = ["+", "-", "*", "/"]
        display_map = {"*": "×", "/": "÷", "-": "−"}

        for perm in itertools.permutations(nums):
            a, b, c, d = perm
            for o1, o2, o3 in itertools.product(ops, repeat=3):
                candidates = [
                    f"(({a}{o1}{b}){o2}{c}){o3}{d}",
                    f"({a}{o1}({b}{o2}{c})){o3}{d}",
                    f"({a}{o1}{b}){o2}({c}{o3}{d})",
                    f"{a}{o1}(({b}{o2}{c}){o3}{d})",
                ]
                for raw_expr in candidates:
                    try:
                        result = self._engine_eval(raw_expr)
                        if result is None or abs(result - target) >= 1e-6:
                            continue
                    except Exception:
                        continue

                    disp_expr = raw_expr
                    for raw, disp in display_map.items():
                        disp_expr = disp_expr.replace(raw, disp)

                    if condition["check"](raw_expr) or condition["check"](disp_expr):
                        return True

        return False

    def _engine_eval(self, expr):
        try:
            import ast as A
            import operator as O

            def ev(n):
                if isinstance(n, A.Constant):
                    return float(n.value)
                if isinstance(n, A.BinOp):
                    d = {A.Add: O.add, A.Sub: O.sub, A.Mult: O.mul, A.Div: O.truediv}
                    left  = ev(n.left)
                    right = ev(n.right)
                    if type(n.op) == A.Div and abs(right) < 1e-9:
                        return None
                    return d[type(n.op)](left, right)
                if isinstance(n, A.UnaryOp) and isinstance(n.op, A.USub):
                    return -ev(n.operand)
                return None

            return ev(A.parse(expr, mode="eval").body)
        except Exception:
            return None

    def _solvable(self, nums, target, adv=False):
        return self._solve([float(n) for n in nums], float(target), adv, set())

    def _solve(self, nums, target, adv, vis):
        if len(nums) == 1:
            return abs(nums[0] - target) < 1e-6

        state = tuple(sorted(round(n, 6) for n in nums))
        if state in vis:
            return False
        vis.add(state)

        for i in range(len(nums)):
            for j in range(i + 1, len(nums)):
                a    = nums[i]
                b    = nums[j]
                rest = [nums[k] for k in range(len(nums)) if k != i and k != j]

                for op in ["+", "-", "*", "/"]:
                    pairs = [(a, b)] if op in ("+", "*") else [(a, b), (b, a)]
                    for x, y in pairs:
                        try:
                            if op == "+":
                                r = x + y
                            elif op == "-":
                                r = x - y
                            elif op == "*":
                                r = x * y
                            elif op == "/":
                                if abs(y) < 1e-9:
                                    continue
                                r = x / y
                            if self._solve(rest + [r], target, adv, vis):
                                return True
                        except Exception:
                            pass

        return False

    def _build(self):
        self._top_border = ctk.CTkFrame(self, fg_color="#4CAF50", height=5, corner_radius=0)
        self._top_border.pack(fill="x")

        sc = _scrollable(self)
        sc.pack(fill="both", expand=True)
        f = sc

        # topbar
        self._topbar = ctk.CTkFrame(f, fg_color="transparent")
        self._topbar.pack(fill="x", padx=20, pady=(14, 0))

        ctk.CTkButton(
            self._topbar,
            text="← Home",
            font=ctk.CTkFont("Segoe UI", 12),
            fg_color="transparent",
            hover_color="#f0f0f0",
            text_color=C["text_muted"],
            border_width=0,
            width=70,
            height=28,
            command=self._home,
        ).pack(side="left")

        self._mode_badge = ctk.CTkLabel(
            self._topbar,
            text="Classic",
            font=ctk.CTkFont("Segoe UI", 12, weight="bold"),
            fg_color=C["green_bg"],
            text_color=C["green"],
            corner_radius=20,
            width=72,
            height=26,
        )
        self._mode_badge.pack(side="left", padx=6)

        self._timer_lbl = _lbl(self._topbar, "0:00", 13, color=C["text_light"])
        self._timer_lbl.pack(side="right")

        # speed countdown ring
        self._ring_frame = ctk.CTkFrame(f, fg_color="transparent")
        self._ring       = _CountdownRing(self._ring_frame, total=SPEED_LIMIT)
        self._ring.pack()

        # hard mode condition banner
        self._hard_banner = ctk.CTkFrame(f, fg_color=C["amber_bg"], border_color="#F5C842", border_width=2, corner_radius=10)
        inn = ctk.CTkFrame(self._hard_banner, fg_color="transparent")
        inn.pack(fill="x", padx=14, pady=8)
        _lbl(inn, "⚠ CONDITION", 10, True, color=C["amber_dark"]).pack(anchor="w")
        self._cond_lbl = _lbl(inn, "", 14, True, color="#7A4F00")
        self._cond_lbl.pack(anchor="w")

        # practice mode banner
        self._prac_bar = ctk.CTkFrame(f, fg_color=C["green_bg"], corner_radius=9)
        _lbl(self._prac_bar, "Practice mode — no score recorded, take your time!", 12, color=C["green"]).pack(padx=12, pady=7)

        # target display
        ta = ctk.CTkFrame(f, fg_color="transparent")
        ta.pack(pady=(10, 0))
        _lbl(ta, "TARGET", 11, color=C["text_light"]).pack()
        self._target_lbl = ctk.CTkLabel(ta, text="24", font=ctk.CTkFont("Segoe UI", 52, weight="bold"), text_color="#2D2A6E")
        self._target_lbl.pack()

        # number tiles area
        self._tiles_frame = ctk.CTkFrame(f, fg_color="transparent")
        self._tiles_frame.pack(pady=(8, 8))

        # expression display
        self._expr_box = ctk.CTkLabel(
            f,
            text="",
            font=ctk.CTkFont("Segoe UI", 18, weight="bold"),
            fg_color=C["primary_bg"],
            text_color=C["primary"],
            corner_radius=10,
            height=46,
            anchor="center",
        )
        self._expr_box.pack(fill="x", padx=20, pady=(0, 4))

        # error message
        self._err_frame = ctk.CTkFrame(f, fg_color=C["red_bg"], border_color=C["red_border"], border_width=1, corner_radius=10)
        self._err_lbl   = ctk.CTkLabel(self._err_frame, text="", font=ctk.CTkFont("Segoe UI", 13, weight="bold"), text_color=C["red"])
        self._err_lbl.pack(padx=14, pady=8)

        _lbl(f, "Tap tiles and operators to build an expression", 11, color=C["text_xlight"]).pack(pady=(2, 8))

        # operator buttons
        self._ops1 = ctk.CTkFrame(f, fg_color="transparent")
        self._ops1.pack(pady=(0, 6))
        for txt, tok in [("+", "+"), ("−", "-"), ("×", "*"), ("÷", "/"), ("(", "("), (")", ")")]:
            ctk.CTkButton(
                self._ops1,
                text=txt,
                font=ctk.CTkFont("Segoe UI", 17, weight="bold"),
                fg_color="#fff",
                hover_color=C["primary_bg"],
                text_color=C["primary"],
                border_color=C["primary_border"],
                border_width=1,
                width=46,
                height=38,
                corner_radius=8,
                command=lambda t=tok: self._op(t),
            ).pack(side="left", padx=3)

        # advanced
        self._ops2 = ctk.CTkFrame(f, fg_color="transparent")
        for txt, tok in [("^", "^"), ("√(", "sqrt(")]:
            ctk.CTkButton(
                self._ops2,
                text=txt,
                font=ctk.CTkFont("Segoe UI", 14, weight="bold"),
                fg_color="#fff",
                hover_color=C["primary_bg"],
                text_color=C["primary"],
                border_color=C["primary_border"],
                border_width=1,
                width=58,
                height=38,
                corner_radius=8,
                command=lambda t=tok: self._op(t),
            ).pack(side="left", padx=3)

        # Undo, Clear, Skip
        ar = ctk.CTkFrame(f, fg_color="transparent")
        ar.pack(fill="x", padx=20, pady=(0, 6))
        ar.columnconfigure(0, weight=1)
        ar.columnconfigure(1, weight=1)
        ar.columnconfigure(2, weight=1)

        ctk.CTkButton(
            ar,
            text="↩ Undo",
            font=ctk.CTkFont("Segoe UI", 13, weight="bold"),
            fg_color=C["primary_bg"],
            hover_color=C["primary_light"],
            text_color=C["primary"],
            border_width=0,
            height=38,
            corner_radius=9,
            command=self._undo,
        ).grid(row=0, column=0, padx=(0, 3), sticky="ew")

        ctk.CTkButton(
            ar,
            text="Clear",
            font=ctk.CTkFont("Segoe UI", 13, weight="bold"),
            fg_color=C["red_bg"],
            hover_color="#ffe0e0",
            text_color=C["red"],
            border_width=0,
            height=38,
            corner_radius=9,
            command=self._clear,
        ).grid(row=0, column=1, padx=3, sticky="ew")

        ctk.CTkButton(
            ar,
            text="Skip",
            font=ctk.CTkFont("Segoe UI", 13),
            fg_color="transparent",
            hover_color="#f5f5f5",
            text_color=C["text_light"],
            border_color="#eee",
            border_width=1,
            height=38,
            corner_radius=9,
            command=self._skip,
        ).grid(row=0, column=2, padx=(3, 0), sticky="ew")

        # submit button
        self._submit_btn = ctk.CTkButton(
            f,
            text="Submit",
            font=ctk.CTkFont("Segoe UI", 16, weight="bold"),
            fg_color=C["primary"],
            hover_color="#3f37a0",
            text_color="#fff",
            height=48,
            corner_radius=12,
            command=self._submit,
        )
        self._submit_btn.pack(fill="x", padx=20, pady=(0, 8))

        # hint button
        self._hint_btn = ctk.CTkButton(
            f,
            text="💡 Use hint (2 left)",
            font=ctk.CTkFont("Segoe UI", 12),
            fg_color="transparent",
            hover_color="#f5f5f5",
            text_color=C["text_muted"],
            border_color=C["border"],
            border_width=1,
            height=32,
            corner_radius=8,
            command=self._hint,
        )
        self._hint_btn.pack(padx=60, pady=(0, 20))

    def _rebuild_tiles(self):
        for w in self._tiles_frame.winfo_children():
            w.destroy()

        adv = (self._mode == "advanced")
        sz  = 50 if adv else 60
        fs  = 18 if adv else 22
        gap = 6  if adv else 9

        self._tile_btns = []
        for i, n in enumerate(self._numbers):
            used = (i in self._used)
            b = ctk.CTkButton(
                self._tiles_frame,
                text=str(n),
                font=ctk.CTkFont("Segoe UI", fs, weight="bold"),
                width=sz,
                height=sz,
                fg_color="#eee" if used else C["primary_bg"],
                hover_color=C["primary_light"] if not used else "#eee",
                text_color="#bbb" if used else C["primary"],
                border_color="#ddd" if used else C["primary_border"],
                border_width=2,
                corner_radius=12,
                state="disabled" if used else "normal",
                command=lambda idx=i: self._tile(idx),
            )
            b.pack(side="left", padx=gap // 2)
            self._tile_btns.append(b)

    def _refresh_tiles(self):
        for i, b in enumerate(self._tile_btns):
            used = (i in self._used)
            b.configure(
                fg_color=    "#eee" if used else C["primary_bg"],
                hover_color= C["primary_light"] if not used else "#eee",
                text_color=  "#bbb" if used else C["primary"],
                border_color="#ddd" if used else C["primary_border"],
                state=       "disabled" if used else "normal",
            )

    def _upd_expr(self):
        text = self._builder.get_display() if not self._builder.is_empty() else "Tap to start…"
        self._expr_box.configure(text=text)

    def _show_err(self, msg):
        if hasattr(self, "_err_job") and self._err_job:
            try:
                self.after_cancel(self._err_job)
            except Exception:
                pass
        self._err_lbl.configure(text=msg)
        self._err_frame.pack(fill="x", padx=20, pady=(0, 6))
        self._err_job = self.after(5000, self._clear_err)

    def _clear_err(self):
        if hasattr(self, "_err_job") and self._err_job:
            try:
                self.after_cancel(self._err_job)
            except Exception:
                pass
            self._err_job = None
        self._err_frame.pack_forget()

    def _tile(self, idx):
        if idx in self._used or not self._active:
            return
        self._used.add(idx)
        self._builder.add_token(str(self._numbers[idx]))
        self._upd_expr()
        self._refresh_tiles()
        self._clear_err()

    def _op(self, tok):
        if not self._active:
            return
        self._builder.add_token(tok)
        self._upd_expr()
        self._clear_err()

    def _undo(self):
        if self._builder.is_empty() or not self._active:
            return

        # sqrt
        tokens = self._builder._tokens
        last   = tokens[-1] if tokens else ""
        self._builder.undo()

        if last.lstrip("-").isdigit():
            v = int(last)
            for idx in sorted(self._used, reverse=True):
                if self._numbers[idx] == v:
                    self._used.discard(idx)
                    break

        self._upd_expr()
        self._refresh_tiles()
        self._clear_err()

    def _clear(self):
        if not self._active:
            return
        self._builder.clear()
        self._used.clear()
        self._upd_expr()
        self._refresh_tiles()
        self._clear_err()

    def _skip(self):
        if not self._active:
            return
        self._active = False
        self._stop_timer()
        self._unbind_keys()
        self._end(False, gave_up=True)

    def _submit(self):
        if not self._active:
            return

        expr = self._builder.get_expression()
        if not expr.strip():
            self._show_err("⚠ Build an expression first")
            return

        self._attempts += 1

        # hard mode condition check
        if self._mode == "hard" and self._condition:
            disp   = self._builder.get_display()
            disp_n = disp.replace(" ", "")
            expr_n = expr.replace(" ", "")
            if not self._condition["check"](disp_n) and not self._condition["check"](expr_n):
                play_wrong()
                self._show_err(f"✕ Condition not met: {self._condition['short']}")
                return

        # number validation
        try:
            found = [int(float(n)) for n in re.findall(r"\d+(?:\.\d+)?", expr)]
        except Exception:
            found = []

        if sorted(found) != sorted(self._numbers):
            play_wrong()
            self._show_err(f"✕ Use exactly: {self._numbers}")
            return

        # evaluate
        try:
            result = self._engine.evaluate(expr)
            if abs(result - 24) < 1e-6:
                play_correct()
                self._active = False
                self._stop_timer()
                self._end(True)
            else:
                play_wrong()
                d = int(result) if result == int(result) else round(result, 3)
                self._show_err(f"✕ Got {d}, not 24 — try again")
                self._shake()
        except ValueError as e:
            play_wrong()
            self._show_err(f"✕ {e}")
        except Exception:
            play_wrong()
            self._show_err("✕ Invalid expression")

    def _hint(self):
        if not self._active or self._hints_left == 0:
            return

        play_hint()
        self._hints_used += 1

        if self._hints_left != 999:
            self._hints_left -= 1

        if self._hints_left == 0:
            self._hint_btn.configure(
                text="💡 No hints left",
                state="disabled",
                text_color=C["text_xlight"],
                border_color="#eee",
            )
        elif self._hints_left != 999:
            self._hint_btn.configure(text=f"💡 Use hint ({self._hints_left} left)")

        # hint
        hint_idx = None
        hint_val = None
        for i, n in enumerate(self._numbers):
            if i not in self._used:
                hint_idx = i
                hint_val = n
                break

        if hint_idx is None:
            hint_idx = 0
            hint_val = self._numbers[0]

        self._clear_err()
        self._flash(hint_idx)
        self.after(100, lambda v=hint_val: self._show_err(f"💡 Hint: try using {v}"))

    def _home(self):
        self._stop_timer()
        self._active = False
        self._unbind_keys()
        self.app.show_page("mode_select")

    def _timeout(self):
        self._active = False
        self._stop_timer()
        play_timeout()
        self._end(False, timed_out=True)

    def _unbind_keys(self):
        try:
            self.app.unbind("<Key>")
        except Exception:
            pass

    def _on_key(self, event):
        if not self._active:
            return

        k  = event.keysym
        ch = event.char

        if ch in "123456789":
            val = int(ch)
            for idx, n in enumerate(self._numbers):
                if n == val and idx not in self._used:
                    self._tile(idx)
                    return

        op_map = {"+": "+", "-": "-", "*": "*", "/": "/", "(": "(", ")": ")"}
        if ch in op_map:
            self._op(op_map[ch])
            return

        if ch == "^" and self._mode == "advanced":
            self._op("^")
            return

        if k in ("Return", "KP_Enter"):
            self._submit()
            return
        if k == "BackSpace":
            self._undo()
            return
        if k in ("Delete", "Escape"):
            self._clear()
            return

    def _shake(self):
        def step(n, d):
            if n <= 0:
                self._expr_box.pack_configure(padx=20)
                return
            self._expr_box.pack_configure(padx=(20 + 6 * d, 20 - 6 * d))
            self.after(40, lambda: step(n - 1, -d))
        step(5, 1)

    def _flash(self, idx):
        if idx >= len(self._tile_btns):
            return
        b = self._tile_btns[idx]

        def f(n, on):
            if n <= 0:
                b.configure(fg_color=C["primary_bg"], border_color=C["primary_border"])
                return
            b.configure(
                fg_color=    C["primary_light"] if on else C["primary_bg"],
                border_color=C["primary"]       if on else C["primary_border"],
            )
            self.after(150, lambda: f(n - 1, not on))

        f(6, True)

    def _run_timer(self):
        if not self._active:
            return

        self._elapsed = time.time() - self._start_time

        if self._mode == "speed":
            rem  = max(0.0, SPEED_LIMIT - self._elapsed)
            secs = int(rem)
            self._timer_lbl.configure(
                text=       f"0:{secs:02d}",
                text_color= "#E24B4A" if secs <= 10 else C["text_light"],
            )
            self._ring.set_time(rem)

            # tick sound 
            if secs <= 5 and secs != self._last_tick_sec:
                self._last_tick_sec = secs
                play_tick()

            if rem <= 0:
                self._timeout()
                return

        elif self._mode != "practice":
            tot = int(self._elapsed)
            self._timer_lbl.configure(text=f"{tot // 60}:{tot % 60:02d}")

        self._timer_job = self.after(200, self._run_timer)

    def _stop_timer(self):
        if self._timer_job:
            self.after_cancel(self._timer_job)
            self._timer_job = None

    def _end(self, won, timed_out=False, gave_up=False):
        self._elapsed = time.time() - self._start_time

        if self._session and GAME_BACKEND:
            try:
                self._session.hints_used = self._hints_used
                self._session.attempts   = self._attempts
                self._session.end_game(won=won)
                score = self._session.score
            except Exception:
                score = self._calc_score(won)
        else:
            score = self._calc_score(won)

        # evaluate achievements
        new_ach = []
        if ACH_BACKEND and BACKEND:
            try:
                user = self.app.auth.current_user
                if user:
                    am      = AchievementManager(self.app._store)
                    new_ach = am.evaluate(user)
                    if new_ach:
                        play_achievement()
            except Exception:
                pass

        self._unbind_keys()

        if BACKEND and score > 0:
            try:
                sb = ScoreboardManager()
                sb.add_score(_get_username(self.app), score, self._mode)
            except Exception:
                pass

        self.app.last_result = {
            "won":              won,
            "timed_out":        timed_out,
            "gave_up":          gave_up,
            "mode":             self._mode,
            "score":            score,
            "time_used":        round(self._elapsed, 1),
            "attempts":         self._attempts,
            "hints":            self._hints_used,
            "numbers":          list(self._numbers),
            "target":           self._target,
            "new_achievements": new_ach,
        }
        self.app.show_page("result")

    def _calc_score(self, won):
        if not won or self._mode == "practice":
            return 0
        time_bonus      = max(0, 30 - self._elapsed) * 2
        attempt_penalty = max(0, self._attempts - 1) * 5
        hint_penalty    = self._hints_used * 10
        return max(0, int(100 + time_bonus - attempt_penalty - hint_penalty))

# PAGE 6 Result

class ResultPage(RoundedCard):
    def __init__(self, p, app, **kw):
        super().__init__(p, **kw)
        self.app       = app
        self._score_job = None
        self._sc        = _scrollable(self)
        self._sc.pack(fill="both", expand=True, padx=4, pady=4)

    def _animate_score(self, label, target, duration_ms=1000):
        if not self.winfo_exists():
            return
        t0 = [self.winfo_toplevel().tk.call("clock", "milliseconds")]

        def _tick():
            try:
                now      = self.winfo_toplevel().tk.call("clock", "milliseconds")
                elapsed  = int(now) - int(t0[0])
                progress = min(elapsed / duration_ms, 1.0)
                eased    = 1 - (1 - progress) ** 3
                current  = int(eased * target)
                label.configure(text=str(current))
                if progress < 1.0:
                    self._score_job = self.after(16, _tick)
                else:
                    label.configure(text=str(target))
            except Exception:
                label.configure(text=str(target))

        _tick()

    def _slide_in_solution(self, frame):
        frame.configure(height=0)
        frame.pack_propagate(False)
        steps    = [0]
        target_h = 62

        def _grow():
            steps[0] += 1
            h = int(target_h * (steps[0] / 12))
            try:
                frame.configure(height=min(h, target_h))
                if steps[0] < 12:
                    self.after(20, _grow)
                else:
                    frame.pack_propagate(True)
            except Exception:
                pass

        self.after(300, _grow)

    def refresh(self):
        if self._score_job:
            try:
                self.after_cancel(self._score_job)
            except Exception:
                pass
        self._score_job = None

        for w in self._sc.winfo_children():
            w.destroy()

        r = getattr(self.app, "last_result", None)
        if not r:
            return

        f         = self._sc
        won       = r["won"]
        timed_out = r.get("timed_out")
        gave_up   = r.get("gave_up")

        self.configure(fg_color=C["card_bg"])
        self._sc.configure(fg_color=C["card_bg"])

        # top accent bar
        accent = "#3B6D11" if won else ("#E24B4A" if timed_out else "#534AB7")
        ctk.CTkFrame(f, fg_color=accent, height=7, corner_radius=0).pack(fill="x", pady=(0, 18))

        # result icon
        if won:
            icon, title, tc = "🏆", "You solved it!", "#3B6D11"
        elif timed_out:
            icon, title, tc = "⏰", "Time's up!", C["red"]
        else:
            icon, title, tc = "😔", "You gave up", "#534AB7"

        icon_bg     = "#EAF3DE" if won else (C["red_bg"] if timed_out else "#EEEDFE")
        icon_border = "#639922" if won else ("#E24B4A" if timed_out else "#534AB7")

        icon_frame = ctk.CTkFrame(f, fg_color=icon_bg, corner_radius=40, border_color=icon_border, border_width=2, width=72, height=72)
        icon_frame.pack(pady=(0, 10))
        icon_frame.pack_propagate(False)
        ctk.CTkLabel(icon_frame, text=icon, font=ctk.CTkFont("Segoe UI", 32), fg_color="transparent", text_color=C["text_dark"]).place(relx=0.5, rely=0.5, anchor="center")

        _lbl(f, title, 22, True, color=tc).pack(pady=(0, 2))
        _lbl(f, f"{r['mode'].capitalize()} mode · Target: {r['target']}", 12, color=C["text_muted"]).pack(pady=(0, 14))

        # score card
        sb = ctk.CTkFrame(f, fg_color=C["card_bg"], corner_radius=12, border_color=icon_border, border_width=2)
        sb.pack(fill="x", padx=24, pady=(0, 12))
        _lbl(sb, "SCORE", 11, True, color=icon_border).pack(pady=(10, 0))
        score_tc  = "#3B6D11" if won else C["text_xlight"]
        score_lbl = ctk.CTkLabel(sb, text="0", font=ctk.CTkFont("Segoe UI", 48, weight="bold"), text_color=score_tc)
        score_lbl.pack(pady=(0, 10))

        # stats row
        dg = ctk.CTkFrame(f, fg_color="transparent")
        dg.pack(fill="x", padx=24, pady=(0, 14))
        dg.columnconfigure((0, 1, 2), weight=1)
        stat_items = [
            ("TIME",    f"{r['time_used']}s"),
            ("SUBMITS", str(r["attempts"])),
            ("HINTS",   str(r["hints"])),
        ]
        for ci, (lb, vl) in enumerate(stat_items):
            bx = ctk.CTkFrame(dg, fg_color="#fafafa", corner_radius=9, border_color="#eee", border_width=1)
            bx.grid(row=0, column=ci, padx=3, sticky="ew")
            _lbl(bx, lb, 10, color=C["text_light"]).pack(pady=(7, 0))
            _lbl(bx, vl, 16, True).pack(pady=(0, 7))

        # new achievement banners
        for ach in r.get("new_achievements", []):
            pl = ctk.CTkFrame(f, fg_color=C["amber_bg"], corner_radius=30)
            pl.pack(fill="x", padx=24, pady=2)
            _lbl(pl, f"★ {ach.replace('_', ' ').title()}", 12, color=C["amber_dark"]).pack(padx=13, pady=6)

        # solution hint
        if not won:
            sx = ctk.CTkFrame(f, fg_color=C["red_bg"], corner_radius=9, border_color=C["red_border"], border_width=1)
            sx.pack(fill="x", padx=24, pady=(4, 14))
            _lbl(sx, "ONE POSSIBLE SOLUTION", 10, True, color=C["red"]).pack(pady=(8, 2))
            _lbl(sx, self._find_sol(r["numbers"], r["target"]), 14, True, color="#333").pack(pady=(0, 8))
            self._slide_in_solution(sx)

        # action buttons
        bf = ctk.CTkFrame(f, fg_color="transparent")
        bf.pack(fill="x", padx=24, pady=(4, 24))
        if won:
            ctk.CTkButton(
                bf,
                text="Play again",
                font=ctk.CTkFont("Segoe UI", 15, weight="bold"),
                fg_color="#3B6D11",
                hover_color="#27500A",
                text_color="#fff",
                height=46,
                corner_radius=10,
                command=self._again,
            ).pack(fill="x", pady=(0, 6))
        else:
            _btn_primary(bf, "Try again", self._again).pack(fill="x", pady=(0, 6))

        _btn_ghost(bf, "🏠 Home", lambda: self.app.show_page("mode_select")).pack(fill="x", pady=(0, 6))

        # score animation
        if won:
            self.after(150, lambda: self._animate_score(score_lbl, r["score"]))
        else:
            score_lbl.configure(text_color="#ddd")
            self.after(300, lambda: self._animate_score(score_lbl, 0, 400))
            self.after(300, lambda: score_lbl.configure(text_color=C["text_xlight"]))

    def _again(self):
        self.app.selected_mode = getattr(self.app, "last_result", {}).get("mode", "classic")
        self.app.show_page("game")

    def _find_sol(self, nums, target):
        ops = ["+", "-", "*", "/"]

        def chk(ex):
            try:
                import ast as A
                import operator as O

                def ev(n):
                    if isinstance(n, A.Constant):
                        return float(n.value)
                    if isinstance(n, A.BinOp):
                        d = {A.Add: O.add, A.Sub: O.sub, A.Mult: O.mul, A.Div: O.truediv}
                        left  = ev(n.left)
                        right = ev(n.right)
                        t     = type(n.op)
                        if t == A.Div and abs(right) < 1e-9:
                            raise ZeroDivisionError
                        return d[t](left, right)
                    if isinstance(n, A.UnaryOp) and isinstance(n.op, A.USub):
                        return -ev(n.operand)
                    raise ValueError

                return abs(ev(A.parse(ex, mode="eval").body) - float(target)) < 1e-6
            except Exception:
                return False

        def _search(ns):
            if len(ns) == 1:
                return str(int(ns[0])) if abs(ns[0] - target) < 1e-6 else None

            for i in range(len(ns)):
                for j in range(len(ns)):
                    if i == j:
                        continue
                    a    = ns[i]
                    b    = ns[j]
                    rest = [ns[k] for k in range(len(ns)) if k != i and k != j]

                    for op in ops:
                        try:
                            a_str = str(int(a) if a == int(a) else a)
                            b_str = str(int(b) if b == int(b) else b)
                            if op == "+":
                                r    = a + b
                                expr = f"({a_str}+{b_str})"
                            elif op == "-":
                                r    = a - b
                                expr = f"({a_str}-{b_str})"
                            elif op == "*":
                                r    = a * b
                                expr = f"({a_str}*{b_str})"
                            elif op == "/":
                                if abs(b) < 1e-9:
                                    continue
                                r    = a / b
                                expr = f"({a_str}/{b_str})"
                            else:
                                continue
                        except Exception:
                            continue

                        sub = _search(rest + [r])
                        if sub is not None:
                            rv = str(int(r)) if abs(r - int(r)) < 1e-9 else str(round(r, 6))
                            return sub.replace(rv, expr, 1) if rv in sub else expr

            return None

        n = len(nums)

        if n == 4:
            # fast brute-force
            for perm in itertools.permutations(nums):
                a, b, c, d = perm
                for o1, o2, o3 in itertools.product(ops, repeat=3):
                    candidates = [
                        f"(({a}{o1}{b}){o2}{c}){o3}{d}",
                        f"({a}{o1}({b}{o2}{c})){o3}{d}",
                        f"({a}{o1}{b}){o2}({c}{o3}{d})",
                        f"{a}{o1}(({b}{o2}{c}){o3}{d})",
                        f"{a}{o1}({b}{o2}({c}{o3}{d}))",
                    ]
                    for ex in candidates:
                        if chk(ex):
                            return ex.replace("*", "×").replace("/", "÷") + f" = {target}"
        else:
            # advanced mode
            for perm in itertools.permutations(nums):
                sol = _search(list(float(x) for x in perm))
                if sol is not None:
                    return sol.replace("*", "×").replace("/", "÷") + f" = {target}"

        return "(solution not found)"

# PAGE 7 Scoreboard

class ScoreboardPage(ctk.CTkFrame):
    RANK_STYLE = {
        1: ("#FAEEDA", "#7A4F00", "#F0C060"),
        2: ("#F1EFE8", "#4A4A4A", "#C0C0C0"),
        3: ("#FAECE7", "#7A3010", "#D4956A"),
    }
    MEDALS = {1: "🥇", 2: "🥈", 3: "🥉"}

    def __init__(self, p, app, **kw):
        kw.setdefault("fg_color",     C["card_bg"])
        kw.setdefault("corner_radius", 20)
        super().__init__(p, **kw)
        self.app  = app
        self._mgr = ScoreboardManager() if BACKEND else None
        self._build()
        self.refresh()

    def _build(self):
        bar = ctk.CTkFrame(self, fg_color="transparent")
        bar.pack(fill="x", padx=20, pady=(16, 0))

        _btn_back(bar, lambda: self.app.show_page("mode_select")).pack(side="left")
        ctk.CTkButton(
            bar,
            text="↻",
            font=ctk.CTkFont("Segoe UI", 16, weight="bold"),
            fg_color="transparent",
            hover_color=C["primary_bg"],
            text_color=C["primary"],
            border_width=0,
            width=34,
            height=34,
            corner_radius=8,
            command=self.refresh,
        ).pack(side="right")

        _lbl(self, "Scoreboard", 22, True).pack(pady=(10, 2))
        _lbl(self, "Total score per player (all modes combined)", 13, color=C["text_light"]).pack(pady=(0, 10))
        _divider(self, 20, (0, 4))
        self._scroll = _scrollable(self)
        self._scroll.pack(fill="both", expand=True)

    def refresh(self):
        for w in self._scroll.winfo_children():
            w.destroy()
        entries = self._load_entries()
        self._draw_entries(entries)

    def _load_entries(self):
        raw = []
        if self._mgr:
            try:
                raw = self._mgr._load() or _SB_DEMO
            except Exception:
                raw = _SB_DEMO
        else:
            raw = _SB_DEMO

        totals = {}
        for e in raw:
            un          = e.get("username", "—")
            totals[un]  = totals.get(un, 0) + int(e.get("score", 0))

        grouped = [{"username": un, "score": sc} for un, sc in totals.items()]
        return sorted(grouped, key=lambda e: e["score"], reverse=True)[:20]

    def _draw_entries(self, entries):
        f  = self._scroll
        me = _get_username(self.app)

        if not entries:
            _lbl(f, "No scores yet — play a game! 🎮", 14, color=C["text_light"], justify="center").pack(pady=40)
            return

        # column headers
        hdr = ctk.CTkFrame(f, fg_color="transparent")
        hdr.pack(fill="x", padx=14, pady=(4, 2))
        for txt, w in [("#", 28), ("Player", 200), ("Total Score", 80)]:
            _lbl(hdr, txt, 10, True, color=C["text_light"], width=w, anchor="center").pack(side="left")

        _divider(f, 14, (2, 4))

        my_rank  = None
        my_score = 0
        in_top   = False

        for rank, e in enumerate(entries, 1):
            un    = e.get("username", "—")
            sc    = int(e.get("score", 0))
            is_me = (un == me)
            if is_me:
                my_rank  = rank
                my_score = sc
                in_top   = True
            self._row(f, rank, un, sc, is_me)

        self._you_section(f, my_rank, my_score, in_top)

    def _row(self, p, rank, un, sc, is_me):
        if is_me:
            bg, tc, bc = C["primary_light"], C["primary"], C["primary_border"]
        elif rank in self.RANK_STYLE:
            bg, tc, bc = self.RANK_STYLE[rank]
        elif rank % 2 == 0:
            bg, tc, bc = "#fafafa", C["text_dark"], "#f0f0f0"
        else:
            bg, tc, bc = C["card_bg"], C["text_dark"], "#f0f0f0"

        row = ctk.CTkFrame(p, fg_color=bg, corner_radius=9, border_color=bc, border_width=1)
        row.pack(fill="x", padx=14, pady=2)

        inn = ctk.CTkFrame(row, fg_color="transparent")
        inn.pack(fill="x", padx=10, pady=7)

        rt = self.MEDALS.get(rank, str(rank))
        fs = 16 if rank <= 3 else 13
        _lbl(inn, rt, fs, bold=rank <= 3, color=tc, width=28, anchor="center").pack(side="left")

        av = getattr(self.app, "current_user_avatar", "🐱") if is_me else _AV_POOL[hash(un) % len(_AV_POOL)]
        ctk.CTkLabel(
            inn,
            text=av,
            font=ctk.CTkFont("Segoe UI", 16),
            width=30,
            height=30,
            fg_color=C["primary_bg"] if is_me else "#f0f0f0",
            corner_radius=15,
            text_color=C["text_dark"],
        ).pack(side="left", padx=(4, 6))

        _lbl(inn, un, 13, bold=is_me, color=tc, anchor="w").pack(side="left", fill="x", expand=True)
        _lbl(inn, str(sc), 14, True, color=C["primary"] if is_me else C["text_dark"], width=80, anchor="e").pack(side="right")

    def _you_section(self, p, my_rank, my_score, in_top):
        me = _get_username(self.app)
        if not me or me in ("player", ""):
            return

        _divider(p, 14, (8, 0))
        rk = my_rank or "—"

        yc = ctk.CTkFrame(p, fg_color=C["primary_light"], corner_radius=9, border_color=C["primary_border"], border_width=1)
        yc.pack(fill="x", padx=14, pady=(6, 16))

        inn = ctk.CTkFrame(yc, fg_color="transparent")
        inn.pack(fill="x", padx=10, pady=8)

        _lbl(inn, str(rk), 13, True, color=C["primary"], width=28, anchor="center").pack(side="left")

        av = getattr(self.app, "current_user_avatar", "🐱") or "🐱"
        ctk.CTkLabel(inn, text=av, font=ctk.CTkFont("Segoe UI", 16), width=30, height=30, fg_color=C["primary_bg"], corner_radius=15, text_color=C["text_dark"]).pack(side="left", padx=(4, 6))

        nr = ctk.CTkFrame(inn, fg_color="transparent")
        nr.pack(side="left", fill="x", expand=True)
        _lbl(nr, me, 13, True, color=C["primary"], anchor="w").pack(side="left")
        ctk.CTkLabel(nr, text=" YOU", font=ctk.CTkFont("Segoe UI", 9, weight="bold"), fg_color=C["primary"], text_color="#fff", corner_radius=6, width=32, height=16).pack(side="left", padx=4)

        _lbl(inn, str(my_score), 14, True, color=C["primary"], width=80, anchor="e").pack(side="right")

# PAGE 8 Statistics

class StatisticsPage(ctk.CTkFrame):
    def __init__(self, p, app, **kw):
        kw.setdefault("fg_color",     C["card_bg"])
        kw.setdefault("corner_radius", 20)
        super().__init__(p, **kw)
        self.app  = app
        self._mgr = StatisticsManager() if STATS_BACKEND else None
        self._cvs = []
        self._build()
        self.refresh()

    def _build(self):
        bar = ctk.CTkFrame(self, fg_color="transparent")
        bar.pack(fill="x", padx=20, pady=(16, 0))

        _btn_back(bar, lambda: self.app.show_page("mode_select")).pack(side="left")
        ctk.CTkButton(
            bar,
            text="↻",
            font=ctk.CTkFont("Segoe UI", 16, weight="bold"),
            fg_color="transparent",
            hover_color=C["primary_bg"],
            text_color=C["primary"],
            border_width=0,
            width=34,
            height=34,
            corner_radius=8,
            command=self.refresh,
        ).pack(side="right")

        _lbl(self, "📊  Statistics", 22, True).pack(pady=(10, 2))
        _lbl(self, "Your game performance at a glance", 13, color=C["text_light"]).pack(pady=(0, 10))
        _divider(self, 20, (0, 4))
        self._sc = _scrollable(self)
        self._sc.pack(fill="both", expand=True)

    def refresh(self):
        plt.close("all")
        self._cvs.clear()
        for w in self._sc.winfo_children():
            w.destroy()
        if not LIBS_OK:
            self._no_libs()
            return
        df = self._load_data()
        self._render(df)

    def _load_data(self):
        un = _get_username(self.app)
        if self._mgr and un:
            try:
                logs = self._mgr._get_logs(un)
                if logs:
                    df = pd.DataFrame(logs)
                    for col in ["attempts", "hints_used", "won", "score"]:
                        if col in df.columns:
                            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0).astype(int)
                    if "time_used" in df.columns:
                        df["time_used"] = pd.to_numeric(df["time_used"], errors="coerce").fillna(0.0)
                    df           = df.reset_index(drop=True)
                    df["session"] = df.index + 1
                    return df
            except Exception:
                pass

        df            = pd.DataFrame(_STATS_DEMO)
        df["session"] = df.index + 1
        return df

    def _render(self, df):
        f = self._sc
        _section_lbl(f, "SUMMARY STATS")
        self._tbl_stats(f, df)
        _spacer(f)
        _section_lbl(f, "WIN / LOSS RATIO")
        self._tbl_ratio(f, df)
        _spacer(f)
        _section_lbl(f, "WIN / LOSS TABLE")
        self._tbl_won(f, df)
        _spacer(f)
        _section_lbl(f, "ATTEMPTS DISTRIBUTION")
        self._embed(f, self._fig_hist(df))
        _spacer(f)
        _section_lbl(f, "TIME PER SESSION  (s)")
        self._embed(f, self._fig_line(df))
        _spacer(f)
        _section_lbl(f, "ATTEMPTS  vs  TIME  (scatter)")
        self._embed(f, self._fig_scatter(df))
        _spacer(f)
        _section_lbl(f, "WIN RATE")
        self._embed(f, self._fig_donut(df))
        _spacer(f)
        _section_lbl(f, "HINTS USED PER SESSION")
        self._embed(f, self._fig_hints(df))
        _spacer(f, 20)

    def _card(self, p):
        c = ctk.CTkFrame(p, fg_color=C["card_bg"], corner_radius=12, border_color=C["border"], border_width=1)
        c.pack(fill="x", padx=20, pady=2)
        return c

    def _embed(self, p, fig):
        card = self._card(p)
        cv   = FigureCanvasTkAgg(fig, master=card)
        cv.draw()
        cv.get_tk_widget().pack(fill="both", expand=True, padx=4, pady=4)
        self._cvs.append(cv)

    def _ax(self, ax):
        ax.set_facecolor(MPL["bg"])
        ax.figure.patch.set_facecolor(MPL["bg"])
        ax.grid(True, color=MPL["grid"], linewidth=0.8, zorder=0)
        ax.set_axisbelow(True)
        for s in ax.spines.values():
            s.set_color(MPL["spine"])
            s.set_linewidth(0.8)
        ax.tick_params(colors=MPL["tick"], labelsize=8)
        ax.xaxis.label.set_color(MPL["label"])
        ax.xaxis.label.set_fontsize(9)
        ax.yaxis.label.set_color(MPL["label"])
        ax.yaxis.label.set_fontsize(9)

    def _fig(self, h=2.4):
        return plt.Figure(figsize=(3.7, h), dpi=100, facecolor=MPL["bg"], tight_layout=True)

    def _tbl_stats(self, p, df):
        wanted = [c for c in ["attempts", "hints_used"] if c in df.columns]
        if not wanted:
            return

        desc = df[wanted].describe()
        desc.loc["median"] = df[wanted].median()

        card = self._card(p)
        inn  = ctk.CTkFrame(card, fg_color="transparent")
        inn.pack(fill="x", padx=14, pady=10)

        hdrs = ["Feature", "Mean", "Median", "Min", "Max", "Std Dev"]
        cws  = [2, 1, 1, 1, 1, 1]
        for i, w in enumerate(cws):
            inn.columnconfigure(i, weight=w)

        for ci, h in enumerate(hdrs):
            ctk.CTkLabel(
                inn,
                text=h,
                font=ctk.CTkFont("Segoe UI", 10, weight="bold"),
                fg_color=C["tbl_hdr_bg"],
                text_color=C["tbl_hdr_text"],
                corner_radius=0,
                height=26,
                anchor="center",
            ).grid(row=0, column=ci, sticky="nsew", padx=1, pady=(0, 1))

        lbs = {"attempts": "Attempts", "hints_used": "Hints Used"}

        for ri, col in enumerate(wanted, 1):
            s       = desc[col]
            rb      = C["tbl_alt"] if ri % 2 == 0 else C["card_bg"]
            std_val = df[col].std()
            std_str = "—" if (std_val != std_val) else f"{float(std_val):.2f}"

            cells = [
                lbs.get(col, col),
                f"{float(s.get('mean', df[col].mean())):.1f}",
                f"{float(df[col].median()):.1f}",
                f"{int(s.get('min', df[col].min()))}",
                f"{int(s.get('max', df[col].max()))}",
                std_str,
            ]

            for ci, cell in enumerate(cells):
                fi = (ci == 0)
                ctk.CTkLabel(
                    inn,
                    text=cell,
                    font=ctk.CTkFont("Segoe UI", 10, weight="bold" if fi else "normal"),
                    fg_color=C["tbl_fc_bg"] if fi else rb,
                    text_color=C["tbl_fc_text"] if fi else C["text_dark"],
                    corner_radius=0,
                    height=26,
                    anchor="center",
                ).grid(row=ri, column=ci, sticky="nsew", padx=1, pady=1)

    def _tbl_ratio(self, p, df):
        if "won" not in df.columns or df.empty:
            return

        ct  = df["won"].value_counts()
        w   = int(ct.get(1, 0))
        l   = int(ct.get(0, 0))
        tot = w + l
        wp  = round(w / tot * 100, 1) if tot else 0
        lp  = round(100 - wp, 1)

        card = self._card(p)
        inn  = ctk.CTkFrame(card, fg_color="transparent")
        inn.pack(fill="x", padx=14, pady=10)

        hdrs = ["Feature", "Wins", "Losses", "Win%", "Loss%"]
        for i, h in enumerate(hdrs):
            inn.columnconfigure(i, weight=2 if i == 0 else 1)
            ctk.CTkLabel(
                inn,
                text=h,
                font=ctk.CTkFont("Segoe UI", 10, weight="bold"),
                fg_color=C["tbl_hdr_bg"],
                text_color=C["tbl_hdr_text"],
                corner_radius=0,
                height=26,
                anchor="center",
            ).grid(row=0, column=i, sticky="nsew", padx=1, pady=(0, 1))

        for ci, cell in enumerate(["Win / Loss", str(w), str(l), f"{wp}%", f"{lp}%"]):
            fi = (ci == 0)
            ctk.CTkLabel(
                inn,
                text=cell,
                font=ctk.CTkFont("Segoe UI", 10, weight="bold" if fi else "normal"),
                fg_color=C["tbl_fc_bg"] if fi else C["card_bg"],
                text_color=C["tbl_fc_text"] if fi else C["text_dark"],
                corner_radius=0,
                height=26,
                anchor="center",
            ).grid(row=1, column=ci, sticky="nsew", padx=1, pady=1)

    def _tbl_won(self, p, df):
        if "won" not in df.columns or df.empty:
            return

        ct   = df["won"].value_counts()
        wins   = int(ct.get(1, 0))
        losses = int(ct.get(0, 0))
        tot    = wins + losses
        wp     = round(wins / tot * 100, 1) if tot else 0.0
        lp     = round(100 - wp, 1)         if tot else 0.0

        card = self._card(p)
        inn  = ctk.CTkFrame(card, fg_color="transparent")
        inn.pack(fill="x", padx=14, pady=10)

        hdrs = ["Feature", "Wins", "Losses", "Win%", "Loss%"]
        for i, h in enumerate(hdrs):
            inn.columnconfigure(i, weight=2 if i == 0 else 1)
            ctk.CTkLabel(
                inn,
                text=h,
                font=ctk.CTkFont("Segoe UI", 10, weight="bold"),
                fg_color=C["tbl_hdr_bg"],
                text_color=C["tbl_hdr_text"],
                corner_radius=0,
                height=26,
                anchor="center",
            ).grid(row=0, column=i, sticky="nsew", padx=1, pady=(0, 1))

        rows = [["Total Games", str(wins), str(losses), f"{wp}%", f"{lp}%"]]
        for ri, cells in enumerate(rows, 1):
            rb = C["tbl_alt"] if ri % 2 == 0 else C["card_bg"]
            for ci, cell in enumerate(cells):
                fi = (ci == 0)
                ctk.CTkLabel(
                    inn,
                    text=cell,
                    font=ctk.CTkFont("Segoe UI", 10, weight="bold" if fi else "normal"),
                    fg_color=C["tbl_fc_bg"] if fi else rb,
                    text_color=C["tbl_fc_text"] if fi else C["text_dark"],
                    corner_radius=0,
                    height=26,
                    anchor="center",
                ).grid(row=ri, column=ci, sticky="nsew", padx=1, pady=1)

    def _fig_hist(self, df):
        fig = self._fig(2.5)
        ax  = fig.add_subplot(111)

        if "attempts" in df.columns and not df["attempts"].empty:
            sns.histplot(
                data=df,
                x="attempts",
                bins=range(int(df["attempts"].min()), int(df["attempts"].max()) + 2),
                color=MPL["purple"],
                edgecolor="#fff",
                linewidth=0.9,
                alpha=0.85,
                discrete=True,
                stat="count",
                ax=ax,
            )
            for p in ax.patches:
                h = int(p.get_height())
                if h > 0:
                    ax.text(
                        p.get_x() + p.get_width() / 2,
                        h + 0.05,
                        str(h),
                        ha="center",
                        va="bottom",
                        fontsize=7,
                        color=MPL["purple_e"],
                        fontweight="bold",
                    )

        ax.set_xlabel("Attempts per session", fontsize=9)
        ax.set_ylabel("Frequency", fontsize=9)
        ax.xaxis.set_major_locator(plt.MaxNLocator(integer=True))
        ax.yaxis.set_major_locator(plt.MaxNLocator(integer=True))
        self._ax(ax)
        return fig

    def _fig_line(self, df):
        fig = self._fig(2.5)
        ax  = fig.add_subplot(111)

        if "time_used" in df.columns and not df.empty:
            ss = df["session"].tolist()
            tv = df["time_used"].tolist()
            sns.lineplot(data=df, x="session", y="time_used", color=MPL["blue"], linewidth=2, markers=True, dashes=False, ax=ax)
            ax.fill_between(ss, tv, alpha=0.15, color=MPL["blue_lt"])
            if len(df) >= 3:
                roll = df["time_used"].rolling(window=3, center=True).mean()
                ax.plot(ss, roll, color=MPL["purple"], linewidth=1.5, linestyle="--", alpha=0.8, label="3-session avg")
                ax.legend(fontsize=8, framealpha=0.7, edgecolor=C["border"])

        ax.set_xlabel("Session #", fontsize=9)
        ax.set_ylabel("Time (s)", fontsize=9)
        ax.xaxis.set_major_locator(plt.MaxNLocator(integer=True))
        self._ax(ax)
        return fig

    def _fig_scatter(self, df):
        fig = self._fig(2.6)
        ax  = fig.add_subplot(111)

        if "attempts" in df.columns and "time_used" in df.columns and not df.empty:
            pf = df.copy()
            if "won" in pf.columns:
                pf["outcome"] = pf["won"].map({1: "Win", 0: "Loss"})
                sns.scatterplot(
                    data=pf,
                    x="attempts",
                    y="time_used",
                    hue="outcome",
                    hue_order=["Win", "Loss"],
                    palette={"Win": MPL["blue"], "Loss": "#F87171"},
                    edgecolor=MPL["dot_edge"],
                    linewidth=0.8,
                    alpha=0.75,
                    s=55,
                    ax=ax,
                )
                ax.legend(fontsize=8, framealpha=0.8, edgecolor=C["border"], title=None)
            else:
                sns.scatterplot(data=pf, x="attempts", y="time_used", color=MPL["purple"], edgecolor=MPL["dot_edge"], linewidth=0.8, alpha=0.75, s=55, ax=ax)

            x = df["attempts"].values.astype(float)
            y = df["time_used"].values.astype(float)
            if len(x) >= 2:
                m, b = np.polyfit(x, y, 1)
                xr   = np.linspace(x.min(), x.max(), 100)
                ax.plot(xr, m * xr + b, color=MPL["blue_lt"], linewidth=1.5, linestyle="--", alpha=0.7)
                r = float(np.corrcoef(x, y)[0, 1])
                ax.annotate(f"r = {r:.2f}", xy=(0.97, 0.06), xycoords="axes fraction", ha="right", fontsize=8, color=MPL["dot_edge"])

        ax.set_xlabel("Attempts", fontsize=9)
        ax.set_ylabel("Time (s)", fontsize=9)
        ax.xaxis.set_major_locator(plt.MaxNLocator(integer=True))
        self._ax(ax)
        return fig

    def _fig_donut(self, df):
        fig = self._fig(2.6)
        ax  = fig.add_subplot(111)
        ax.set_facecolor(MPL["bg"])
        fig.patch.set_facecolor(MPL["bg"])

        if "won" in df.columns and not df.empty:
            ct   = df["won"].value_counts()
            w    = int(ct.get(1, 0))
            l    = int(ct.get(0, 0))
        else:
            w, l = 14, 5

        tot = w + l
        wp  = round(w / tot * 100, 1) if tot else 0

        _, _, ats = ax.pie(
            [w, l] if tot > 0 else [1, 1],
            labels=[f"Win  ({w})", f"Loss  ({l})"],
            colors=[MPL["blue"], MPL["blue_lt"]],
            autopct="%1.1f%%",
            startangle=90,
            counterclock=False,
            wedgeprops={"width": 0.52, "edgecolor": "white", "linewidth": 2},
            textprops={"fontsize": 9, "color": C["text_dark"]},
            pctdistance=0.78,
        )
        for at in ats:
            at.set_fontsize(8)
            at.set_color("white")
            at.set_fontweight("bold")

        ax.text(0,  0.10, f"{wp:.0f}%", ha="center", va="center", fontsize=20, fontweight="bold", color="#1E3A8A")
        ax.text(0, -0.20, "Win Rate",   ha="center", va="center", fontsize=9,  color=C["text_muted"])
        ax.set_aspect("equal")
        return fig

    def _fig_hints(self, df):
        fig = self._fig(2.4)
        ax  = fig.add_subplot(111)

        if "hints_used" in df.columns and not df.empty:
            pf = df[["session", "hints_used"]].copy()
            pf["hint_level"] = pf["hints_used"].apply(lambda v: "≥ 2 hints" if int(v) >= 2 else "0–1 hints")
            sns.barplot(
                data=pf,
                x="session",
                y="hints_used",
                hue="hint_level",
                palette={"0–1 hints": MPL["blue"], "≥ 2 hints": MPL["purple"]},
                dodge=False,
                edgecolor="white",
                linewidth=0.5,
                ax=ax,
            )
            ax.legend(title=None, fontsize=8, framealpha=0.8, edgecolor=C["border"])
            n    = len(pf)
            step = max(1, n // 6)
            ax.set_xticks(range(0, n, step))
            ax.set_xticklabels([str(i + 1) for i in range(0, n, step)], fontsize=8)

        ax.set_xlabel("Session #", fontsize=9)
        ax.set_ylabel("Hints used", fontsize=9)
        ax.yaxis.set_major_locator(plt.MaxNLocator(integer=True))
        self._ax(ax)
        return fig

    def _no_libs(self):
        c = ctk.CTkFrame(self._sc, fg_color="#FFF5F5", corner_radius=12, border_color="#FFCFCF", border_width=1)
        c.pack(fill="x", padx=20, pady=20)
        _lbl(c, "⚠  Missing libraries", 15, True, color=C["red"]).pack(pady=(14, 4))
        _lbl(c, "pip install pandas numpy matplotlib seaborn", 12, color="#555").pack(pady=(0, 6))
        if LIBS_ERR:
            _lbl(c, f"Error: {LIBS_ERR}", 10, color="#aaa").pack(pady=(0, 14))

# PAGE 9 Achievements

class AchievementsPage(ctk.CTkFrame):
    def __init__(self, p, app, **kw):
        kw.setdefault("fg_color",     C["card_bg"])
        kw.setdefault("corner_radius", 20)
        super().__init__(p, **kw)
        self.app = app
        self._build()
        self.refresh()

    def _build(self):
        bar = ctk.CTkFrame(self, fg_color="transparent")
        bar.pack(fill="x", padx=20, pady=(16, 0))

        _btn_back(bar, lambda: self.app.show_page("mode_select")).pack(side="left")
        ctk.CTkButton(
            bar,
            text="↻",
            font=ctk.CTkFont("Segoe UI", 16, weight="bold"),
            fg_color="transparent",
            hover_color=C["primary_bg"],
            text_color=C["primary"],
            border_width=0,
            width=34,
            height=34,
            corner_radius=8,
            command=self.refresh,
        ).pack(side="right")

        _lbl(self, "Achievements", 22, True).pack(pady=(10, 2))
        self._subtitle = _lbl(self, "0 / 8 unlocked", 13, color=C["text_light"])
        self._subtitle.pack(pady=(0, 6))

        # progress bar
        self._prog_frame = ctk.CTkFrame(self, fg_color=C["border"], height=6, corner_radius=3)
        self._prog_frame.pack(fill="x", padx=30, pady=(0, 10))
        self._prog_bar = ctk.CTkFrame(self._prog_frame, fg_color=C["primary"], height=6, corner_radius=3)
        self._prog_bar.place(relx=0, rely=0, relheight=1, relwidth=0)

        _divider(self, 20, (0, 4))
        self._sc = _scrollable(self)
        self._sc.pack(fill="both", expand=True)

    def refresh(self):
        for w in self._sc.winfo_children():
            w.destroy()

        unlocked   = self._get_unlocked()
        total      = len(ACH_CATALOGUE)
        n_unlocked = sum(1 for a in ACH_CATALOGUE if a["id"] in unlocked)

        self._subtitle.configure(text=f"{n_unlocked} / {total} unlocked")
        frac = n_unlocked / total if total else 0
        self._prog_bar.place(relwidth=frac)

        f      = self._sc
        done   = [a for a in ACH_CATALOGUE if a["id"] in unlocked]
        locked = [a for a in ACH_CATALOGUE if a["id"] not in unlocked]

        if done:
            _section_lbl(f, f"UNLOCKED  ✓  ({len(done)})")
            for a in done:
                self._ach_card(f, a, unlocked=True)

        if locked:
            _spacer(f, 4)
            _section_lbl(f, f"LOCKED  🔒  ({len(locked)})")
            for a in locked:
                self._ach_card(f, a, unlocked=False)

        _spacer(f, 20)

    def _ach_card(self, p, ach, unlocked):
        card = ctk.CTkFrame(
            p,
            fg_color=C["card_bg"],
            corner_radius=12,
            border_color=C["primary_border"] if unlocked else C["border"],
            border_width=1,
        )
        card.pack(fill="x", padx=20, pady=2)

        if not unlocked:
            card.configure(fg_color="#fafafa")

        inn = ctk.CTkFrame(card, fg_color="transparent")
        inn.pack(fill="x", padx=14, pady=12)

        ic_bg = "#E1F5EE" if unlocked else "#f0f0f0"
        ic_tc = C["green"] if unlocked else C["text_xlight"]
        ctk.CTkLabel(
            inn,
            text=ach["icon"],
            font=ctk.CTkFont("Segoe UI", 20),
            width=42,
            height=42,
            fg_color=ic_bg,
            corner_radius=21,
            text_color=ic_tc,
        ).pack(side="left", padx=(0, 12))

        tf         = ctk.CTkFrame(inn, fg_color="transparent")
        tf.pack(side="left", fill="x", expand=True)
        name_color = C["text_dark"] if unlocked else C["text_light"]
        _lbl(tf, ach["name"], 13, True, color=name_color, anchor="w").pack(fill="x")
        _lbl(tf, ach["desc"], 11, color=C["text_muted"] if unlocked else C["text_xlight"], anchor="w").pack(fill="x")

        if unlocked:
            ctk.CTkLabel(
                inn,
                text="✓",
                font=ctk.CTkFont("Segoe UI", 16, weight="bold"),
                fg_color="#E1F5EE",
                text_color="#0F6E56",
                width=32,
                height=32,
                corner_radius=16,
            ).pack(side="right")
        else:
            ctk.CTkLabel(
                inn,
                text="🔒",
                font=ctk.CTkFont("Segoe UI", 14),
                fg_color="#f0f0f0",
                text_color=C["text_xlight"],
                width=32,
                height=32,
                corner_radius=16,
            ).pack(side="right")
            for widget in [inn, tf]:
                widget.configure(fg_color="transparent")
            card.configure(fg_color="#f8f8f8")

    def _get_unlocked(self):
        if BACKEND and ACH_BACKEND:
            try:
                user = self.app.auth.current_user
                if user:
                    return set(user.achievements)
            except Exception:
                pass

        if hasattr(self.app, "demo_user") and self.app.demo_user:
            return self.app.demo_user.get("achievements", set())
        return {a["id"] for a in ACH_CATALOGUE[:5]}

# Main App

class Game24App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Game 24")
        self.geometry("460x720")
        self.minsize(400, 600)
        self.configure(fg_color=C["body_bg"])
        self.resizable(True, True)
        self.update_idletasks()

        x = (self.winfo_screenwidth()  - 460) // 2
        y = (self.winfo_screenheight() - 720) // 2
        self.geometry(f"460x720+{x}+{y}")

        self.current_user_avatar = "🐱"
        self.selected_mode       = "classic"
        self.demo_user           = None
        self.last_result         = None

        if BACKEND:
            self._store = UserStore()
            self.auth   = AuthManager(self._store)
        else:
            self.auth = None

        self._build_header()
        self._build_pages()
        self.show_page("login")

    def _build_header(self):
        self.grid_rowconfigure(0, weight=0)
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self._header = ctk.CTkFrame(self, fg_color="transparent")
        self._header.grid(row=0, column=0, pady=(20, 0))
        _lbl(self._header, "Game 24",                32, True, color="#2D2A6E").pack()
        _lbl(self._header, "Make 24 with 4 numbers", 13,       color="#888").pack()

    def _build_pages(self):
        con = ctk.CTkFrame(self, fg_color="transparent")
        con.grid(row=1, column=0, sticky="nsew", padx=20, pady=(14, 20))

        self.pages = {}
        self.pages["register"]     = RegisterPage(con,    self, width=420)
        self.pages["login"]        = LoginPage(con,       self, width=420)
        self.pages["mode_select"]  = ModeSelectPage(con,  self, width=420)
        self.pages["guide"]        = GuidePage(con,       self, width=420)
        self.pages["game"]         = GamePage(con,        self, width=420)
        self.pages["result"]       = ResultPage(con,      self, width=420)
        self.pages["scoreboard"]   = ScoreboardPage(con,  self, width=420)
        self.pages["statistics"]   = StatisticsPage(con,  self, width=420)
        self.pages["achievements"] = AchievementsPage(con, self, width=420)

        for pg in self.pages.values():
            pg.grid(row=0, column=0, sticky="nsew")

        con.grid_rowconfigure(0, weight=1)
        con.grid_columnconfigure(0, weight=1)

    def show_page(self, name):
        if name not in self.pages:
            print(f"[UI] Unknown page: {name}")
            return

        pg = self.pages[name]

        if name in ("login", "register"):
            self._header.grid(row=0, column=0, pady=(20, 0))
        else:
            self._header.grid_remove()

        if name == "game":
            pg.start_game(self.selected_mode)

        pages_with_refresh = ("login", "result", "mode_select", "scoreboard", "statistics", "achievements")
        if name in pages_with_refresh and hasattr(pg, "refresh"):
            pg.refresh()

        pg.tkraise()

    def _logout(self):
        if BACKEND and self.auth:
            try:
                self.auth.logout()
            except Exception:
                pass
        self.current_user_avatar = "🐱"
        self.selected_mode       = "classic"
        self.last_result         = None
        self.show_page("login")

    def quit_app(self):
        if messagebox.askyesno("Exit", "Are you sure you want to exit?"):
            self.destroy()

# start

if __name__ == "__main__":
    app = Game24App()
    app.mainloop()
