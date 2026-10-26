"""
Muse AI - Desktop Prototype v1
Layout copied from the user's ChatGPT screenshot, renamed for Muse:
  - Top-left: Muse AI (colourful, big)
  - Left sidebar: Home, New chat, Projects, Recents
  - Main pane: chat messages
  - Bottom input box: [+] button, text entry, Send
  - Top-right: [+] button -> opens the DEDICATED browser
  - STOP button: stops any browser automation immediately

What this prototype IS:
  - A chat window on the user's Windows PC.
  - The [+] button opens a dedicated Chromium browser (Playwright, persistent
    profile in ./muse_browser_profile). That browser is ONLY for agent work.
    The user's own Chrome stays separate and untouched.
  - Chat answers come from the brain model configured in .env
    (default: Qwen free model via OpenRouter). This is NOT the full Muse
    model inside the app - Muse's rules are loaded from RULES.md in this
    folder, so the small brain follows Muse's method for the user's work.

What this prototype is NOT (yet):
  - It does not log in anywhere by itself. The user logs in, by hand, inside
    the dedicated browser, once. The session is then saved in the profile.
  - It does not edit Shopify / Facebook by itself in v1. It only opens the
    dedicated browser and chats. Editing steps come in v2, one verified
    step at a time, after the user says START.

Run on Windows:
  pip install playwright
  playwright install chromium
  copy .env.example to .env and paste your OpenRouter key there (PC only)
  python main.py
"""

import json
import os
import threading
import tkinter as tk
from tkinter import messagebox, scrolledtext

try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    # Manual .env fallback, so python-dotenv is optional
    if os.path.exists(".env"):
        with open(".env", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, v = line.split("=", 1)
                    os.environ.setdefault(k.strip(), v.strip())

API_KEY = os.environ.get("OPENROUTER_API_KEY", "").strip()
MODEL = os.environ.get("MODEL", "qwen/qwen3-235b-a22b:free")

STOP_FLAG = {"stop": False}
BROWSER_THREAD = {"running": False}


def load_rules():
    try:
        with open("RULES.md", encoding="utf-8") as f:
            return f.read()[:4000]
    except Exception:
        return "You are a helpful assistant. Answer in Bengali script, short, action-first."


def ask_brain(user_text):
    """Chat box -> brain (OpenRouter). Returns text, never the key."""
    if not API_KEY:
        return ("Key পাওয়া যায়নি। .env ফাইলে OPENROUTER_API_KEY বসাও, "
                "তারপর আবার লিখো। Key চ্যাটে দিও না।")
    import urllib.request
    messages = [
        {"role": "system", "content": load_rules()},
        {"role": "user", "content": user_text},
    ]
    data = json.dumps({"model": MODEL, "messages": messages}).encode("utf-8")
    req = urllib.request.Request(
        "https://openrouter.ai/api/v1/chat/completions",
        data=data,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {API_KEY}",
            "HTTP-Referer": "http://localhost",
            "X-Title": "Muse AI Prototype",
        },
    )
    with urllib.request.urlopen(req, timeout=120) as resp:
        result = json.loads(resp.read().decode("utf-8"))
    return result["choices"][0]["message"]["content"]


def open_dedicated_browser():
    """[+] button: open ONLY the dedicated browser, in a background thread."""
    if BROWSER_THREAD["running"]:
        return "Dedicated browser already open."
    STOP_FLAG["stop"] = False

    def run():
        BROWSER_THREAD["running"] = True
        try:
            from playwright.sync_api import sync_playwright
            with sync_playwright() as p:
                ctx = p.chromium.launch_persistent_context(
                    "./muse_browser_profile",
                    headless=False,
                    args=["--start-maximized"],
                )
                page = ctx.new_page()
                page.goto("https://www.google.com", timeout=60000)
                # Stay open until STOP or the window is closed.
                while not STOP_FLAG["stop"]:
                    try:
                        if page.is_closed():
                            break
                    except Exception:
                        break
                    page.wait_for_timeout(500)
                try:
                    ctx.close()
                except Exception:
                    pass
        except Exception as e:
            print(f"Browser error: {e}")
        finally:
            BROWSER_THREAD["running"] = False

    threading.Thread(target=run, daemon=True).start()
    return "Dedicated browser opening... (separate window, only for agent work)"


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Muse AI")
        self.geometry("1100x700")
        self.configure(bg="#1e1e1e")

        # ---- Top bar: colourful Muse AI, like ChatGPT header in screenshot ----
        top = tk.Frame(self, bg="#1e1e1e")
        top.pack(fill="x", padx=10, pady=8)
        colours = ["#ff6b6b", "#ffa94d", "#ffd43b", "#69db7c", "#4dabf7", "#da77f2", "#ff6b6b"]
        title_text = "Muse AI"
        for i, ch in enumerate(title_text):
            tk.Label(top, text=ch, font=("Segoe UI", 22, "bold"),
                     fg=colours[i % len(colours)], bg="#1e1e1e").pack(side="left")
        tk.Label(top, text="  ▼", font=("Segoe UI", 12), fg="white", bg="#1e1e1e").pack(side="left")
        # Top-right [+] : same job as ChatGPT screenshot's top-right [+]
        tk.Button(top, text="+  Browser", font=("Segoe UI", 11, "bold"),
                  bg="#2f2f2f", fg="white", command=self.on_plus).pack(side="right", padx=4)
        tk.Button(top, text="■ STOP", font=("Segoe UI", 11, "bold"),
                  bg="#c92a2a", fg="white", command=self.on_stop).pack(side="right", padx=4)

        # ---- Body: sidebar + main chat ----
        body = tk.Frame(self, bg="#1e1e1e")
        body.pack(fill="both", expand=True)

        sidebar = tk.Frame(body, bg="#252525", width=200)
        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False)
        for label in ["🏠  Home", "✎  New chat", "📁  Projects", "🕐  Recents"]:
            tk.Button(sidebar, text=label, font=("Segoe UI", 11), anchor="w",
                      bg="#252525", fg="white", relief="flat",
                      command=lambda l=label: self.show(f"{l} — coming in v2")).pack(fill="x", padx=8, pady=4)
        tk.Label(sidebar, text="\nRecents\n• Shopify audit\n• Qwen test\n• Thread art video",
                 font=("Segoe UI", 10), fg="#cccccc", bg="#252525", justify="left").pack(anchor="w", padx=10)

        main = tk.Frame(body, bg="#1e1e1e")
        main.pack(side="left", fill="both", expand=True, padx=10, pady=5)

        self.chat = scrolledtext.ScrolledText(main, font=("Segoe UI", 11),
                                              bg="#1e1e1e", fg="white", wrap="word")
        self.chat.pack(fill="both", expand=True)
        self.show("Muse AI — স্বাগতম!\n\nবামে + Browser চাপলে ডেডিকেটেড ব্রাউজার খুলবে।\nচ্যাটে লিখলে মাথা (Qwen, OpenRouter দিয়ে) উত্তর দেবে।\nSTOP চাপলে ব্রাউজারের কাজ থেমে যাবে।")

        # ---- Bottom input box: [+] + entry + Send, like the screenshot ----
        bottom = tk.Frame(main, bg="#2f2f2f")
        bottom.pack(fill="x", pady=8)
        tk.Button(bottom, text="+", font=("Segoe UI", 14, "bold"),
                  bg="#2f2f2f", fg="white", command=self.on_plus).pack(side="left", padx=6)
        self.entry = tk.Entry(bottom, font=("Segoe UI", 12), bg="#2f2f2f", fg="white", insertbackground="white")
        self.entry.pack(side="left", fill="x", expand=True, padx=4, pady=8)
        self.entry.bind("<Return>", lambda e: self.on_send())
        tk.Button(bottom, text="↑  Send", font=("Segoe UI", 11, "bold"),
                  bg="#4dabf7", fg="white", command=self.on_send).pack(side="right", padx=6)

    def show(self, text):
        self.chat.insert("end", text + "\n\n")
        self.chat.see("end")

    def on_plus(self):
        self.show(open_dedicated_browser())

    def on_stop(self):
        STOP_FLAG["stop"] = True
        self.show("STOP — Dedicated browser work stopped. START করতে আবার + Browser চাপো।")

    def on_send(self):
        text = self.entry.get().strip()
        if not text:
            return
        self.entry.delete(0, "end")
        self.show(f"তুমি: {text}")
        self.show("Muse AI ভাবছে...")
        def work():
            try:
                ans = ask_brain(text)
            except Exception as e:
                ans = f"Brain error: {e}\nKey / internet / model চেক করো।"
            self.after(0, lambda: self.show(f"Muse AI: {ans}"))
        threading.Thread(target=work, daemon=True).start()


if __name__ == "__main__":
    App().mainloop()
