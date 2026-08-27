#!/usr/bin/env python3
import json
import random
import sys
import time
import tkinter as tk
from pathlib import Path
from tkinter import messagebox

APP_DIR = Path(__file__).resolve().parent
ASSET_DIR = APP_DIR / "assets" / "frames"
SAVE_PATH = APP_DIR / "cat_state.json"
TRANSPARENT = "#00ffcc"


class DesktopCat:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("得意桌宠")
        self.root.overrideredirect(True)
        self.safe_attr("-topmost", True)
        self.root.configure(bg=TRANSPARENT)
        self.safe_attr("-transparent", True)
        self.safe_attr("-transparentcolor", TRANSPARENT)

        self.state = self.load_state()
        self.mode = "idle"
        self.frame_index = 0
        self.drag_start = None
        self.last_tick = time.time()
        self.direction = random.choice([-1, 1])
        self.speed = 2
        self.next_walk_change = time.time() + random.uniform(4, 9)
        self.bubble_until = 0
        self.action_until = 0

        self.images = self.load_images()
        self.cat_label = tk.Label(self.root, bg=TRANSPARENT, borderwidth=0, highlightthickness=0)
        self.cat_label.pack()
        self.bubble = tk.Label(
            self.root,
            bg="#fff7ec",
            fg="#31414a",
            padx=10,
            pady=6,
            font=("PingFang SC", 12),
            borderwidth=1,
            relief="solid",
        )

        self.menu = tk.Menu(self.root, tearoff=0)
        self.menu.add_command(label="喂饭 (+30 饱腹)", command=self.feed)
        self.menu.add_command(label="摸摸 (+18 心情)", command=self.pet)
        self.menu.add_command(label="逗猫 (+12 心情, -8 体力)", command=self.play)
        self.menu.add_command(label="睡觉 (+25 体力)", command=self.sleep)
        self.menu.add_separator()
        self.menu.add_command(label="状态", command=self.show_status)
        self.menu.add_command(label="退出", command=self.quit)

        self.cat_label.bind("<ButtonPress-1>", self.start_drag)
        self.cat_label.bind("<B1-Motion>", self.drag)
        self.cat_label.bind("<ButtonRelease-1>", self.end_drag)
        self.cat_label.bind("<Double-Button-1>", lambda _e: self.pet())
        self.cat_label.bind("<Button-2>", self.popup)
        self.cat_label.bind("<Button-3>", self.popup)
        self.root.bind("<Escape>", lambda _e: self.quit())

        self.place_initially()
        self.say("我在桌面巡逻。右键可以喂饭。", 2600)
        self.animate()
        self.tick()

    def safe_attr(self, key, value):
        try:
            self.root.wm_attributes(key, value)
        except tk.TclError:
            pass

    def load_images(self):
        if not ASSET_DIR.exists():
            messagebox.showerror("缺少素材", "请先运行 slice_assets.py 切出桌宠动画帧。")
            sys.exit(1)
        images = {}
        for state_dir in ASSET_DIR.iterdir():
            if state_dir.is_dir():
                frames = []
                for path in sorted(state_dir.glob("*.png")):
                    frames.append(tk.PhotoImage(file=str(path)).subsample(1, 1))
                if frames:
                    images[state_dir.name] = frames
        if "idle" not in images:
            messagebox.showerror("素材错误", "没有找到 idle 动画帧。")
            sys.exit(1)
        return images

    def load_state(self):
        default = {
            "hunger": 72,
            "mood": 78,
            "energy": 70,
            "last_saved": time.time(),
            "name": "得意",
        }
        if SAVE_PATH.exists():
            try:
                loaded = json.loads(SAVE_PATH.read_text(encoding="utf-8"))
                default.update({k: loaded[k] for k in default.keys() if k in loaded})
            except Exception:
                pass
        return default

    def save_state(self):
        self.state["last_saved"] = time.time()
        SAVE_PATH.write_text(json.dumps(self.state, ensure_ascii=False, indent=2), encoding="utf-8")

    def place_initially(self):
        screen_w = self.root.winfo_screenwidth()
        screen_h = self.root.winfo_screenheight()
        self.root.geometry(f"+{screen_w - 260}+{screen_h - 310}")

    def start_drag(self, event):
        self.drag_start = (event.x_root, event.y_root, self.root.winfo_x(), self.root.winfo_y())
        self.mode = "happy"

    def drag(self, event):
        if not self.drag_start:
            return
        sx, sy, wx, wy = self.drag_start
        self.root.geometry(f"+{wx + event.x_root - sx}+{wy + event.y_root - sy}")

    def end_drag(self, _event):
        self.drag_start = None
        self.mode = "idle"
        self.say("放这里也不错。", 1800)

    def popup(self, event):
        self.menu.tk_popup(event.x_root, event.y_root)

    def clamp(self, key, delta):
        self.state[key] = max(0, min(100, self.state[key] + delta))

    def feed(self):
        self.clamp("hunger", 30)
        self.clamp("mood", 8)
        self.mode = "eat"
        self.action_until = time.time() + 2.2
        self.say(random.choice(["好吃。", "饭碗已清空。", "这口可以。"]), 2200)
        self.save_state()

    def pet(self):
        self.clamp("mood", 18)
        self.clamp("energy", -3)
        self.mode = "happy"
        self.action_until = time.time() + 2.2
        self.say(random.choice(["呼噜呼噜。", "可以再摸一下。", "今天批准你上班。"]), 2200)
        self.save_state()

    def play(self):
        self.clamp("mood", 12)
        self.clamp("energy", -8)
        self.clamp("hunger", -5)
        self.mode = "jump"
        self.action_until = time.time() + 2.2
        self.say("抓到了不存在的小玩具。", 2200)
        self.save_state()

    def sleep(self):
        self.clamp("energy", 25)
        self.clamp("hunger", -4)
        self.mode = "sleepy"
        self.action_until = time.time() + 2.4
        self.say("咪，眯一会儿。", 2400)
        self.save_state()

    def show_status(self):
        self.say(f"饱腹 {self.state['hunger']}  心情 {self.state['mood']}  体力 {self.state['energy']}", 3600)

    def choose_mode(self):
        if self.drag_start:
            return
        if time.time() < self.action_until:
            return
        if self.state["hunger"] < 20:
            self.mode = "sad"
            return
        if self.state["energy"] < 18:
            self.mode = "sleepy"
            return
        if time.time() > self.next_walk_change:
            self.direction = random.choice([-1, 1, 0])
            self.speed = random.choice([1, 2, 2, 3])
            self.next_walk_change = time.time() + random.uniform(3, 8)
        if self.direction > 0:
            self.mode = "walk_right"
        elif self.direction < 0:
            self.mode = "walk_left"
        elif self.mode not in {"eat", "happy", "jump"}:
            self.mode = "idle"

    def move_if_needed(self):
        if self.drag_start or self.mode not in {"walk_right", "walk_left"}:
            return
        x = self.root.winfo_x()
        y = self.root.winfo_y()
        screen_w = self.root.winfo_screenwidth()
        width = max(190, self.root.winfo_width())
        if x < 8:
            self.direction = 1
        if x > screen_w - width - 8:
            self.direction = -1
        self.root.geometry(f"+{x + self.direction * self.speed}+{y}")

    def animate(self):
        frames = self.images.get(self.mode) or self.images["idle"]
        self.frame_index = (self.frame_index + 1) % len(frames)
        self.cat_label.configure(image=frames[self.frame_index])
        if time.time() > self.bubble_until:
            self.bubble.place_forget()
        self.move_if_needed()
        self.root.after(130, self.animate)

    def tick(self):
        now = time.time()
        elapsed = max(1, now - self.last_tick)
        self.last_tick = now
        self.clamp("hunger", -0.06 * elapsed)
        self.clamp("energy", -0.025 * elapsed)
        if self.state["hunger"] < 35:
            self.clamp("mood", -0.035 * elapsed)
        else:
            self.clamp("mood", 0.01 * elapsed)
        self.state["hunger"] = round(self.state["hunger"], 1)
        self.state["mood"] = round(self.state["mood"], 1)
        self.state["energy"] = round(self.state["energy"], 1)
        self.choose_mode()
        if self.state["hunger"] < 25 and random.random() < .08:
            self.say("有点饿了。", 1800)
        self.save_state()
        self.root.after(1000, self.tick)

    def say(self, text, ms=2000):
        self.bubble.configure(text=text)
        self.bubble.place(x=10, y=4)
        self.bubble_until = time.time() + ms / 1000

    def quit(self):
        self.save_state()
        self.root.destroy()

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    DesktopCat().run()
