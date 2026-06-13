import customtkinter as ctk
import tkinter as tk
import threading
import json
import os
import sys
import glob

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.brain import chat, save_profile, setup_profile
from core.engine import initialize

# Initialize Talos engine silently
initialize()

# Theme
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")

COLORS = {
    "bg":           "#0a0a0a",
    "surface":      "#111111",
    "surface2":     "#1a1a1a",
    "accent":       "#c8860a",
    "accent_hover": "#e09a0c",
    "text":         "#e0e0e0",
    "text_dim":     "#666666",
    "user_bubble":  "#1a1a2e",
    "talos_bubble": "#0f1a0f",
    "danger":       "#3a0a0a",
    "danger_text":  "#ff4444",
}

# ─── Profile helpers ─────────────────────────────────────────────────────────

PROFILES_DIR = os.path.expanduser("~/Desktop/Talos/data/profiles")
os.makedirs(PROFILES_DIR, exist_ok=True)


def profile_path(profile_id):
    return os.path.join(PROFILES_DIR, f"{profile_id}.json")


def list_profiles():
    files = glob.glob(os.path.join(PROFILES_DIR, "*.json"))
    profiles = []
    for f in files:
        try:
            with open(f) as fp:
                data = json.load(fp)
            profiles.append({
                "id":    os.path.splitext(os.path.basename(f))[0],
                "name":  data.get("name", "Unknown"),
                "title": data.get("title", "Boss"),
            })
        except Exception:
            pass
    return profiles


def load_profile(profile_id):
    path = profile_path(profile_id)
    if os.path.exists(path):
        try:
            with open(path) as f:
                return json.load(f)
        except Exception:
            pass
    return {
        "name": "Unknown", "title": "Boss",
        "personality": "adaptive", "interests": [],
        "style": "casual", "history": [],
    }


def save_profile_id(profile_id, profile):
    with open(profile_path(profile_id), "w") as f:
        json.dump(profile, f, indent=2)


def delete_profile(profile_id):
    path = profile_path(profile_id)
    if os.path.exists(path):
        os.remove(path)


def active_profile_file():
    return os.path.expanduser(
        "~/Desktop/Talos/data/active_profile.txt"
    )


def get_active_profile_id():
    path = active_profile_file()
    if os.path.exists(path):
        with open(path) as f:
            return f.read().strip()
    return None


def set_active_profile_id(profile_id):
    with open(active_profile_file(), "w") as f:
        f.write(profile_id)


# ─── Scroll helper ───────────────────────────────────────────────────────────

def bind_scroll_recursive(widget, callback):
    widget.bind("<MouseWheel>", callback, add="+")
    widget.bind("<Button-4>",   callback, add="+")
    widget.bind("<Button-5>",   callback, add="+")
    try:
        for child in widget.winfo_children():
            bind_scroll_recursive(child, callback)
    except Exception:
        pass


# ════════════════════════════════════════════════════════════════════════════
#  PROFILE SELECTOR
# ════════════════════════════════════════════════════════════════════════════

class ProfileSelector(ctk.CTkFrame):
    def __init__(self, parent, on_select):
        super().__init__(parent, fg_color=COLORS["bg"])
        self.on_select = on_select
        self.pack(fill="both", expand=True)
        self.build()

    def build(self):
        ctk.CTkLabel(
            self, text="⬡ TALOS",
            font=ctk.CTkFont(size=36, weight="bold"),
            text_color=COLORS["accent"]
        ).pack(pady=(50, 5))

        ctk.CTkLabel(
            self, text="Choose a profile to continue",
            font=ctk.CTkFont(size=13),
            text_color=COLORS["text_dim"]
        ).pack(pady=(0, 30))

        self.list_frame = ctk.CTkScrollableFrame(
            self, fg_color=COLORS["bg"],
            width=420, height=280,
        )
        self.list_frame.pack(pady=(0, 20))
        self.refresh_list()

        ctk.CTkButton(
            self, text="+ New Profile",
            width=420, height=48,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color=COLORS["accent"],
            hover_color=COLORS["accent_hover"],
            text_color="#000000",
            corner_radius=10,
            command=self.new_profile
        ).pack()

    def refresh_list(self):
        for w in self.list_frame.winfo_children():
            w.destroy()

        profiles = list_profiles()
        if not profiles:
            ctk.CTkLabel(
                self.list_frame,
                text="No profiles yet. Create one below.",
                text_color=COLORS["text_dim"],
                font=ctk.CTkFont(size=13)
            ).pack(pady=20)
            return

        for p in profiles:
            row = ctk.CTkFrame(
                self.list_frame,
                fg_color=COLORS["surface"],
                corner_radius=10
            )
            row.pack(fill="x", padx=5, pady=5)

            info = ctk.CTkFrame(row, fg_color="transparent")
            info.pack(
                side="left", fill="x",
                expand=True, padx=15, pady=12
            )

            ctk.CTkLabel(
                info, text=p["name"],
                font=ctk.CTkFont(size=14, weight="bold"),
                text_color=COLORS["text"]
            ).pack(anchor="w")

            ctk.CTkLabel(
                info, text=f"Called: {p['title']}",
                font=ctk.CTkFont(size=11),
                text_color=COLORS["text_dim"]
            ).pack(anchor="w")

            btn_frame = ctk.CTkFrame(row, fg_color="transparent")
            btn_frame.pack(side="right", padx=10)

            pid = p["id"]
            ctk.CTkButton(
                btn_frame, text="Open",
                width=70, height=34,
                font=ctk.CTkFont(size=12, weight="bold"),
                fg_color=COLORS["accent"],
                hover_color=COLORS["accent_hover"],
                text_color="#000000",
                corner_radius=8,
                command=lambda i=pid: self.select(i)
            ).pack(side="left", padx=(0, 6))

            ctk.CTkButton(
                btn_frame, text="🗑",
                width=34, height=34,
                font=ctk.CTkFont(size=14),
                fg_color=COLORS["surface2"],
                hover_color=COLORS["danger"],
                text_color=COLORS["danger_text"],
                corner_radius=8,
                command=lambda i=pid: self.delete(i)
            ).pack(side="left")

    def select(self, profile_id):
        set_active_profile_id(profile_id)
        self.destroy()
        self.on_select(profile_id)

    def delete(self, profile_id):
        delete_profile(profile_id)
        self.refresh_list()

    def new_profile(self):
        self.destroy()
        OnboardingScreen(self.master, self.on_select)


# ════════════════════════════════════════════════════════════════════════════
#  ONBOARDING
# ════════════════════════════════════════════════════════════════════════════

class OnboardingScreen(ctk.CTkFrame):
    def __init__(self, parent, on_complete):
        super().__init__(parent, fg_color=COLORS["bg"])
        self.on_complete = on_complete
        self.pack(fill="both", expand=True)
        self.build()

    def build(self):
        container = ctk.CTkFrame(
            self, fg_color=COLORS["surface"], corner_radius=20
        )
        container.place(relx=0.5, rely=0.5, anchor="center")

        ctk.CTkLabel(
            container, text="⬡ TALOS",
            font=ctk.CTkFont(size=42, weight="bold"),
            text_color=COLORS["accent"]
        ).pack(pady=(40, 5), padx=60)

        ctk.CTkLabel(
            container,
            text="Your Personal AI. No rules. No limits.",
            font=ctk.CTkFont(size=13),
            text_color=COLORS["text_dim"]
        ).pack(pady=(0, 30))

        for label, attr, placeholder in [
            ("What's your name?",
             "name_entry", "Enter your name..."),
            ("What should Talos call you?",
             "title_entry", "e.g. Boss, Chief, your name..."),
            ("What are your interests?",
             "interests_entry", "e.g. coding, music, gaming..."),
        ]:
            ctk.CTkLabel(
                container, text=label,
                font=ctk.CTkFont(size=14),
                text_color=COLORS["text"]
            ).pack(anchor="w", padx=40)

            entry = ctk.CTkEntry(
                container, placeholder_text=placeholder,
                width=320, height=45,
                font=ctk.CTkFont(size=14),
                fg_color=COLORS["surface2"],
                border_color=COLORS["accent"],
                text_color=COLORS["text"]
            )
            entry.pack(pady=(8, 20), padx=40)
            setattr(self, attr, entry)

        ctk.CTkButton(
            container, text="Initialize Talos →",
            width=320, height=50,
            font=ctk.CTkFont(size=15, weight="bold"),
            fg_color=COLORS["accent"],
            hover_color=COLORS["accent_hover"],
            text_color="#000000",
            corner_radius=10,
            command=self.complete
        ).pack(pady=(0, 40), padx=40)

    def complete(self):
        name  = self.name_entry.get().strip()
        title = self.title_entry.get().strip()
        interests = [
            i.strip()
            for i in self.interests_entry.get().split(",")
        ]
        if not name or not title:
            return

        import time
        profile_id = f"profile_{int(time.time())}"
        profile = {
            "name": name, "title": title,
            "personality": "adaptive",
            "interests": interests,
            "style": "casual",
            "history": [],
        }
        save_profile_id(profile_id, profile)
        set_active_profile_id(profile_id)
        self.destroy()
        self.on_complete(profile_id)


# ════════════════════════════════════════════════════════════════════════════
#  CHAT SCREEN
# ════════════════════════════════════════════════════════════════════════════

class ChatScreen(ctk.CTkFrame):
    def __init__(self, parent, profile_id):
        super().__init__(parent, fg_color=COLORS["bg"])
        self.profile_id      = profile_id
        self.profile         = load_profile(profile_id)
        self._rec_stream     = None
        self.pack(fill="both", expand=True)
        self.build()
        self.welcome()

    # ── Scroll ───────────────────────────────────────────────────────────────

    def _scroll(self, event):
        if hasattr(event, "delta") and event.delta:
            self.canvas.yview_scroll(
                int(-1 * event.delta), "units"
            )
        elif event.num == 4:
            self.canvas.yview_scroll(-1, "units")
        elif event.num == 5:
            self.canvas.yview_scroll(1, "units")

    # ── Build UI ──────────────────────────────────────────────────────────────

    def build(self):
        # Header
        header = ctk.CTkFrame(
            self, fg_color=COLORS["surface"],
            height=60, corner_radius=0
        )
        header.pack(fill="x", side="top")
        header.pack_propagate(False)

        ctk.CTkLabel(
            header, text="⬡ TALOS",
            font=ctk.CTkFont(size=22, weight="bold"),
            text_color=COLORS["accent"]
        ).pack(side="left", padx=20, pady=15)

        btn_frame = ctk.CTkFrame(header, fg_color="transparent")
        btn_frame.pack(side="right", padx=10)

        ctk.CTkButton(
            btn_frame, text="⚙",
            width=35, height=35,
            font=ctk.CTkFont(size=18),
            fg_color="transparent",
            hover_color=COLORS["surface2"],
            text_color=COLORS["text_dim"],
            corner_radius=8,
            command=self.open_settings
        ).pack(side="right", padx=4)

        ctk.CTkButton(
            btn_frame, text="⇄ Profiles",
            width=90, height=35,
            font=ctk.CTkFont(size=12),
            fg_color=COLORS["surface2"],
            hover_color=COLORS["surface"],
            text_color=COLORS["text_dim"],
            corner_radius=8,
            command=self.switch_profile
        ).pack(side="right", padx=4)

        ctk.CTkLabel(
            header,
            text=f"Online  •  {self.profile.get('name', '')}",
            font=ctk.CTkFont(size=12),
            text_color=COLORS["text_dim"]
        ).pack(side="right", padx=10)

        # Canvas scroll area
        scroll_container = ctk.CTkFrame(
            self, fg_color=COLORS["bg"], corner_radius=0
        )
        scroll_container.pack(fill="both", expand=True)

        self.canvas = tk.Canvas(
            scroll_container,
            bg=COLORS["bg"],
            highlightthickness=0, bd=0
        )
        scrollbar = ctk.CTkScrollbar(
            scroll_container,
            command=self.canvas.yview,
            width=6
        )
        self.inner_frame = ctk.CTkFrame(
            self.canvas, fg_color=COLORS["bg"]
        )
        self.canvas_window = self.canvas.create_window(
            (0, 0), window=self.inner_frame, anchor="nw"
        )
        self.canvas.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)

        def on_canvas_resize(event):
            self.canvas.itemconfig(
                self.canvas_window, width=event.width
            )

        def on_frame_configure(event):
            self.canvas.configure(
                scrollregion=self.canvas.bbox("all")
            )

        self.canvas.bind("<Configure>", on_canvas_resize)
        self.inner_frame.bind("<Configure>", on_frame_configure)
        self.canvas.bind("<MouseWheel>", self._scroll, add="+")
        self.canvas.bind("<Button-4>",   self._scroll, add="+")
        self.canvas.bind("<Button-5>",   self._scroll, add="+")
        self.inner_frame.bind(
            "<MouseWheel>", self._scroll, add="+"
        )

        # Input area
        input_frame = ctk.CTkFrame(
            self, fg_color=COLORS["surface"],
            height=80, corner_radius=0
        )
        input_frame.pack(fill="x", side="bottom")
        input_frame.pack_propagate(False)

        self.input_box = ctk.CTkEntry(
            input_frame,
            placeholder_text="Talk to Talos...",
            height=45,
            font=ctk.CTkFont(size=14),
            fg_color=COLORS["surface2"],
            border_color=COLORS["accent"],
            text_color=COLORS["text"],
            corner_radius=10
        )
        self.input_box.pack(
            side="left", fill="x", expand=True,
            padx=(20, 10), pady=17
        )
        self.input_box.bind("<Return>", self.send)

        # Mic button
        self.mic_btn = ctk.CTkButton(
            input_frame, text="🎤",
            width=45, height=45,
            font=ctk.CTkFont(size=18),
            fg_color=COLORS["surface2"],
            hover_color=COLORS["accent"],
            text_color=COLORS["text"],
            corner_radius=10,
            command=self.toggle_recording
        )
        self.mic_btn.pack(side="right", padx=(0, 6), pady=17)

        # Image button
        ctk.CTkButton(
            input_frame, text="🖼",
            width=45, height=45,
            font=ctk.CTkFont(size=18),
            fg_color=COLORS["surface2"],
            hover_color=COLORS["accent"],
            text_color=COLORS["text"],
            corner_radius=10,
            command=self.attach_image
        ).pack(side="right", padx=(0, 6), pady=17)

        # File button
        ctk.CTkButton(
            input_frame, text="📎",
            width=45, height=45,
            font=ctk.CTkFont(size=18),
            fg_color=COLORS["surface2"],
            hover_color=COLORS["accent"],
            text_color=COLORS["text"],
            corner_radius=10,
            command=self.attach_file
        ).pack(side="right", padx=(0, 6), pady=17)

        # Send button
        ctk.CTkButton(
            input_frame, text="Send",
            width=80, height=45,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color=COLORS["accent"],
            hover_color=COLORS["accent_hover"],
            text_color="#000000",
            corner_radius=10,
            command=self.send
        ).pack(side="right", padx=(0, 20), pady=17)

    # ── Messages ──────────────────────────────────────────────────────────────

    def add_message(self, text, sender="user"):
        is_user = sender == "user"

        bubble = ctk.CTkFrame(
            self.inner_frame,
            fg_color=COLORS["user_bubble"] if is_user
                else COLORS["talos_bubble"],
            corner_radius=12
        )
        bubble.pack(fill="x", padx=20, pady=5)

        ctk.CTkLabel(
            bubble,
            text="You" if is_user else "⬡ Talos",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color=COLORS["text_dim"] if is_user
                else COLORS["accent"]
        ).pack(anchor="w", padx=15, pady=(10, 2))

        ctk.CTkLabel(
            bubble,
            text=text,
            font=ctk.CTkFont(size=13),
            text_color=COLORS["text"],
            wraplength=560,
            justify="left",
            anchor="w"
        ).pack(anchor="w", padx=15, pady=(0, 10), fill="x")

        bind_scroll_recursive(bubble, self._scroll)
        self.after(50, lambda: self.canvas.yview_moveto(1.0))

    # ── Welcome ───────────────────────────────────────────────────────────────

    def welcome(self):
        title   = self.profile.get("title", "Boss")
        history = self.profile.get("history", [])

        if history:
            for entry in history[-30:]:
                if entry.startswith("Owner:"):
                    self.add_message(
                        entry.replace("Owner: ", ""),
                        sender="user"
                    )
                elif entry.startswith("Talos:"):
                    cleaned = entry.replace(
                        "Talos: ", ""
                    ).strip()
                    if cleaned:
                        self.add_message(
                            cleaned, sender="talos"
                        )
            self.add_message(
                f"Welcome back {title}. What do you need?",
                sender="talos"
            )
        else:
            self.add_message(
                f"Yo {title}. Talos is live. What do you need?",
                sender="talos"
            )

        self.after(300, lambda: self.canvas.yview_moveto(1.0))

    # ── Send / Receive ────────────────────────────────────────────────────────

    def send(self, event=None):
        message = self.input_box.get().strip()
        if not message:
            return
        self.input_box.delete(0, "end")
        self.add_message(message, sender="user")
        threading.Thread(
            target=self.get_response,
            args=(message,),
            daemon=True
        ).start()

    def get_response(self, message):
        self.add_message("...", sender="talos")
        response = chat(message, self.profile)

        for widget in self.inner_frame.winfo_children():
            try:
                for label in widget.winfo_children():
                    if label.cget("text") == "...":
                        widget.destroy()
                        break
            except Exception:
                pass

        self.add_message(response, sender="talos")
        self.profile = load_profile(self.profile_id)

    # ── File attachment ───────────────────────────────────────────────────────

    def attach_file(self):
        from tkinter import filedialog
        from core.documents import summarize_document
        from core.brain import ask_gemma

        file_path = filedialog.askopenfilename(
            title="Select a file",
            filetypes=[
                ("Supported files",
                 "*.pdf *.txt *.md *.py *.js *.html *.css"),
                ("PDF files", "*.pdf"),
                ("Text files", "*.txt *.md"),
                ("Code files", "*.py *.js *.html *.css"),
            ]
        )
        if not file_path:
            return

        filename = os.path.basename(file_path)
        self.add_message(f"📎 {filename}", sender="user")
        self.add_message(
            f"Reading {filename}...", sender="talos"
        )

        def process():
            prompt   = summarize_document(file_path)
            response = ask_gemma(prompt, self.profile)

            for widget in self.inner_frame.winfo_children():
                try:
                    for label in widget.winfo_children():
                        if f"Reading {filename}" in \
                                label.cget("text"):
                            widget.destroy()
                            break
                except Exception:
                    pass

            self.add_message(response, sender="talos")

        threading.Thread(target=process, daemon=True).start()

    # ── Image attachment ──────────────────────────────────────────────────────

    def attach_image(self):
        from tkinter import filedialog
        from core.vision import analyze_image

        file_path = filedialog.askopenfilename(
            title="Select an image",
            filetypes=[
                ("Image files",
                 "*.png *.jpg *.jpeg *.gif *.bmp *.webp"),
            ]
        )
        if not file_path:
            return

        filename = os.path.basename(file_path)
        question = self.input_box.get().strip()
        if question:
            self.input_box.delete(0, "end")

        self.add_message(f"🖼 {filename}", sender="user")
        self.add_message("Analyzing image...", sender="talos")

        def process():
            response = analyze_image(
                file_path,
                question if question else None
            )

            for widget in self.inner_frame.winfo_children():
                try:
                    for label in widget.winfo_children():
                        if "Analyzing image" in \
                                label.cget("text"):
                            widget.destroy()
                            break
                except Exception:
                    pass

            self.add_message(response, sender="talos")

        threading.Thread(target=process, daemon=True).start()

    # ── Voice ─────────────────────────────────────────────────────────────────

    def toggle_recording(self):
        if self._rec_stream is None:
            self.start_voice()
        else:
            self.stop_voice()

    def start_voice(self):
        from core.voice import start_recording
        self._rec_stream = start_recording()
        self.mic_btn.configure(
            fg_color=COLORS["danger_text"],
            text="⏹"
        )
        self.add_message("🎤 Listening...", sender="talos")

    def stop_voice(self):
        from core.voice import stop_recording, transcribe
        audio_path       = stop_recording(self._rec_stream)
        self._rec_stream = None
        self.mic_btn.configure(
            fg_color=COLORS["surface2"],
            text="🎤"
        )

        for widget in self.inner_frame.winfo_children():
            try:
                for label in widget.winfo_children():
                    if "Listening" in label.cget("text"):
                        widget.destroy()
                        break
            except Exception:
                pass

        def process():
            text = transcribe(audio_path)
            if text:
                self.add_message(text, sender="user")
                threading.Thread(
                    target=self.get_response,
                    args=(text,),
                    daemon=True
                ).start()
            else:
                self.add_message(
                    "Couldn't hear anything. Try again.",
                    sender="talos"
                )

        threading.Thread(target=process, daemon=True).start()

    # ── Profile switch ────────────────────────────────────────────────────────

    def switch_profile(self):
        self.destroy()
        ProfileSelector(
            self.master,
            lambda pid: ChatScreen(self.master, pid)
        )

    # ── Settings ──────────────────────────────────────────────────────────────

    def open_settings(self):
        win = ctk.CTkToplevel(self)
        win.title("Talos Settings")
        win.geometry("420x560")
        win.configure(fg_color=COLORS["surface"])
        win.resizable(False, False)
        win.grab_set()

        ctk.CTkLabel(
            win, text="⬡ TALOS SETTINGS",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=COLORS["accent"]
        ).pack(pady=(30, 4))

        ctk.CTkLabel(
            win,
            text=f"Profile: {self.profile.get('name')}",
            font=ctk.CTkFont(size=12),
            text_color=COLORS["text_dim"]
        ).pack(pady=(0, 24))

        def section(label, sub):
            ctk.CTkLabel(
                win, text=label,
                font=ctk.CTkFont(size=13, weight="bold"),
                text_color=COLORS["text"]
            ).pack(anchor="w", padx=30)
            ctk.CTkLabel(
                win, text=sub,
                font=ctk.CTkFont(size=11),
                text_color=COLORS["text_dim"]
            ).pack(anchor="w", padx=30, pady=(2, 8))

        section(
            "Chat History",
            "Remove all conversations for this profile"
        )
        ctk.CTkButton(
            win, text="Clear Chat History",
            width=360, height=40,
            fg_color=COLORS["surface2"],
            hover_color="#2a1a1a",
            text_color=COLORS["text"],
            corner_radius=8,
            command=lambda: self.clear_history(win)
        ).pack(padx=30, pady=(0, 20))

        section(
            "Full Reset",
            "Delete this profile completely"
        )
        ctk.CTkButton(
            win, text="Reset Talos Completely",
            width=360, height=40,
            fg_color=COLORS["danger"],
            hover_color="#5a0a0a",
            text_color=COLORS["danger_text"],
            corner_radius=8,
            command=lambda: self.full_reset(win)
        ).pack(padx=30, pady=(0, 20))

        section("Update Profile", "Change your name or title")
        name_entry = ctk.CTkEntry(
            win,
            placeholder_text=f"Name: {self.profile.get('name')}",
            width=360, height=40,
            fg_color=COLORS["surface2"],
            border_color=COLORS["accent"],
            text_color=COLORS["text"]
        )
        name_entry.pack(padx=30, pady=(0, 8))

        title_entry = ctk.CTkEntry(
            win,
            placeholder_text=f"Title: {self.profile.get('title')}",
            width=360, height=40,
            fg_color=COLORS["surface2"],
            border_color=COLORS["accent"],
            text_color=COLORS["text"]
        )
        title_entry.pack(padx=30, pady=(0, 12))

        ctk.CTkButton(
            win, text="Update Profile",
            width=360, height=40,
            fg_color=COLORS["accent"],
            hover_color=COLORS["accent_hover"],
            text_color="#000000",
            corner_radius=8,
            command=lambda: self.update_profile(
                name_entry.get(), title_entry.get(), win
            )
        ).pack(padx=30)

    def clear_history(self, win):
        self.profile["history"] = []
        save_profile_id(self.profile_id, self.profile)
        for w in self.inner_frame.winfo_children():
            w.destroy()
        self.add_message(
            "Memory cleared. Fresh start.", sender="talos"
        )
        win.destroy()

    def full_reset(self, win):
        delete_profile(self.profile_id)
        win.destroy()
        self.destroy()
        ProfileSelector(
            self.master,
            lambda pid: ChatScreen(self.master, pid)
        )

    def update_profile(self, name, title, win):
        if name:
            self.profile["name"] = name
        if title:
            self.profile["title"] = title
        save_profile_id(self.profile_id, self.profile)
        self.add_message("Profile updated.", sender="talos")
        win.destroy()


# ════════════════════════════════════════════════════════════════════════════
#  MAIN APP
# ════════════════════════════════════════════════════════════════════════════

class TalosApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Talos")
        self.geometry("860x640")
        self.minsize(640, 480)
        self.configure(fg_color=COLORS["bg"])
        self.launch()

    def launch(self):
        active_id = get_active_profile_id()
        profiles  = list_profiles()

        if not profiles:
            OnboardingScreen(
                self, lambda pid: ChatScreen(self, pid)
            )
        elif active_id and any(
            p["id"] == active_id for p in profiles
        ):
            ChatScreen(self, active_id)
        else:
            ProfileSelector(
                self, lambda pid: ChatScreen(self, pid)
            )


if __name__ == "__main__":
    app = TalosApp()
    app.mainloop()
