import tkinter as tk
from tkinter import filedialog, messagebox
import math
from collections import defaultdict

class Segment:
    def __init__(self, x1, y1, x2, y2):
        self.x1 = float(x1)
        self.y1 = float(y1)
        self.x2 = float(x2)
        self.y2 = float(y2)

    def length(self):
        return math.sqrt((self.x2 - self.x1)**2 + (self.y2 - self.y1)**2)

    def move(self, dx, dy):
        self.x1 += dx
        self.y1 += dy
        self.x2 += dx
        self.y2 += dy

class SegmentApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Анализ отрезков")
        self.root.geometry("760x640")
        self.segments = []
        self.groups = defaultdict(list)

        # Рамка для кнопок
        btn_frame = tk.Frame(root)
        btn_frame.pack(pady=8)

        btn_style = {"width": 25, "font": ("Arial", 10)}

        tk.Button(btn_frame, text="Загрузить файл", command=self.load_file, **btn_style).grid(row=0, column=0, pady=3)
        tk.Button(btn_frame, text="Сегментация по длине", command=self.segment_by_length, **btn_style).grid(row=1, column=0, pady=3)
        tk.Button(btn_frame, text="Визуализировать", command=self.visualize, **btn_style).grid(row=2, column=0, pady=3)
        tk.Button(btn_frame, text="Переместить отрезки", command=self.move_all, **btn_style).grid(row=3, column=0, pady=3)

        # Канвас для визуализации (увеличен)
        self.canvas = tk.Canvas(root, width=700, height=500, bg="white", relief="solid", borderwidth=1)
        self.canvas.pack(pady=10)

    def load_file(self):
        path = filedialog.askopenfilename(filetypes=[("Text files", "*.txt")])
        if not path:
            return
        self.segments.clear()
        self.canvas.delete("all")
        try:
            with open(path, 'r', encoding='utf-8') as f:
                for line in f:
                    parts = line.strip().split()
                    if len(parts) != 4:
                        messagebox.showerror("Ошибка", f"Неверная строка: {line.strip()}")
                        return
                    try:
                        x1, y1, x2, y2 = map(float, parts)
                        self.segments.append(Segment(x1, y1, x2, y2))
                    except ValueError:
                        messagebox.showerror("Ошибка", f"Некорректные данные: {line.strip()}")
                        return
            messagebox.showinfo("Успех", f"Загружено отрезков: {len(self.segments)}")
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))

    def segment_by_length(self):
        if not self.segments:
            messagebox.showwarning("Нет данных", "Сначала загрузите файл.")
            return
        self.groups.clear()
        for s in self.segments:
            l = s.length()
            if l < 100:
                self.groups["Короткие"].append(s)
            elif l < 200:
                self.groups["Средние"].append(s)
            else:
                self.groups["Длинные"].append(s)
        messagebox.showinfo("Готово", "Сегментация выполнена.")

    def visualize(self):
        if not self.groups:
            messagebox.showwarning("Нет данных", "Сначала выполните сегментацию.")
            return
        self.canvas.delete("all")
        colors = {"Короткие": "green", "Средние": "blue", "Длинные": "red"}
        for group, segs in self.groups.items():
            for s in segs:
                self.canvas.create_line(s.x1, s.y1, s.x2, s.y2, fill=colors[group], width=2)
        self.canvas.create_text(350, 20, text="Отрезки на плоскости", font=("Arial", 13, "bold"))

    def move_all(self):
        if not self.segments:
            messagebox.showwarning("Нет данных", "Сначала загрузите файл.")
            return
        dx = self.simple_input("Введите сдвиг по X:")
        dy = self.simple_input("Введите сдвиг по Y:")
        try:
            dx, dy = float(dx), float(dy)
        except ValueError:
            messagebox.showerror("Ошибка", "Введите числа.")
            return
        for s in self.segments:
            s.move(dx, dy)
        self.visualize()

    def simple_input(self, prompt):
        win = tk.Toplevel(self.root)
        win.title("Ввод данных")
        win.geometry("230x110")
        win.resizable(False, False)
        tk.Label(win, text=prompt, font=("Arial", 10)).pack(pady=5)
        entry = tk.Entry(win, font=("Arial", 10), justify="center")
        entry.pack(pady=5)
        value = tk.StringVar()
        def ok():
            value.set(entry.get())
            win.destroy()
        tk.Button(win, text="OK", width=10, command=ok).pack(pady=5)
        self.root.wait_window(win)
        return value.get()

if __name__ == "__main__":
    root = tk.Tk()
    app = SegmentApp(root)
    root.mainloop()
