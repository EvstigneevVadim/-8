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
        return math.sqrt((self.x2 - self.x1) ** 2 + (self.y2 - self.y1) ** 2)

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

        btn_frame = tk.Frame(root)
        btn_frame.pack(pady=8)

        btn_style = {"width": 25, "font": ("Arial", 10)}
        tk.Button(btn_frame, text="Загрузить файл (products.txt)", command=self.load_file, **btn_style).grid(row=0, column=0, pady=3)
        tk.Button(btn_frame, text="Сегментация по длине", command=self.segment_by_length, **btn_style).grid(row=1,column=0,pady=3)
        tk.Button(btn_frame, text="Визуализировать", command=self.visualize, **btn_style).grid(row=2, column=0, pady=3)
        tk.Button(btn_frame, text="Переместить отрезки", command=self.move_all, **btn_style).grid(row=3, column=0,pady=3)

        display_frame = tk.Frame(root)
        display_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        self.canvas = tk.Canvas(display_frame, width=500, height=400, bg="white", relief="solid", borderwidth=1)
        self.canvas.pack(side=tk.LEFT, padx=(0, 10))
        self.chart_canvas = tk.Canvas(display_frame, width=180, height=400, bg="white", relief="solid", borderwidth=1)
        self.chart_canvas.pack(side=tk.LEFT)
        self.info_text = tk.Text(root, height=8, wrap=tk.WORD, font=("Arial", 9))
        self.info_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        scrollbar = tk.Scrollbar(self.info_text)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.info_text.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.info_text.yview)

    def update_info(self):
        self.info_text.delete(1.0, tk.END)
        if not self.segments:
            self.info_text.insert(tk.END, "Нет загруженных отрезков. Используйте 'Загрузить файл'.")
            return
        info = f"Всего отрезков: {len(self.segments)}\n\n"

        if self.groups:
            info += "ГРУППЫ ОТРЕЗКОВ:\n"
            info += "─" * 40 + "\n"
            for group_name in ["Короткие", "Средние", "Длинные"]:
                if group_name in self.groups:
                    count = len(self.groups[group_name])
                    info += f"• {group_name}: {count} отрезков\n"
        else:
            info += "Сегментация не выполнена. Используйте 'Сегментация по длине'.\n"
        self.info_text.insert(tk.END, info)

    def draw_chart(self):
        self.chart_canvas.delete("all")

        if not self.groups:
            self.chart_canvas.create_text(90, 200, text="Нет данных\nдля диаграммы",
                                          font=("Arial", 10), justify=tk.CENTER)
            return

        colors = {"Короткие": "green", "Средние": "blue", "Длинные": "red"}
        groups_data = []
        for group_name in ["Короткие", "Средние", "Длинные"]:
            if group_name in self.groups:
                count = len(self.groups[group_name])
                groups_data.append((group_name, count, colors[group_name]))

        if not groups_data:
            return

        chart_width = 160
        chart_height = 300
        start_x = 10
        start_y = 50
        bar_width = 40
        spacing = 20

        self.chart_canvas.create_text(90, 20, text="Диаграмма\nраспределения",font=("Arial", 10, "bold"), justify=tk.CENTER)

        max_count = max(count for _, count, _ in groups_data)
        scale = (chart_height - 20) / max_count if max_count > 0 else 1

        for i, (group_name, count, color) in enumerate(groups_data):
            x = start_x + i * (bar_width + spacing)
            bar_height = count * scale

            self.chart_canvas.create_rectangle(
                x, start_y + chart_height - bar_height,
                   x + bar_width, start_y + chart_height,
                fill=color, outline="black"
            )
            self.chart_canvas.create_text(
                x + bar_width / 2, start_y + chart_height - bar_height - 10,
                text=str(count), font=("Arial", 9, "bold")
            )
            self.chart_canvas.create_text(
                x + bar_width / 2, start_y + chart_height + 15,
                text=group_name, font=("Arial", 8), angle=45
            )

    def get_segment_color(self, segment):
        length = segment.length()
        if length < 100:
            return "green"
        elif length < 200:
            return "blue"
        else:
            return "red"

    def load_file(self):
        path = filedialog.askopenfilename(filetypes=[("Text files", "*.txt")])
        if not path:
            return
        self.segments.clear()
        self.groups.clear()
        self.canvas.delete("all")
        self.chart_canvas.delete("all")
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
            self.update_info()
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

        self.canvas.delete("all")
        colors = {"Короткие": "green", "Средние": "blue", "Длинные": "red"}
        for group, segs in self.groups.items():
            for s in segs:
                self.canvas.create_line(s.x1, s.y1, s.x2, s.y2, fill=colors[group], width=2)
        self.update_info()
        self.draw_chart()
        messagebox.showinfo("Готово", "Сегментация выполнена и отображена на экране.")

    def visualize(self):
        if not self.segments:
            messagebox.showwarning("Нет данных", "Сначала загрузите файл.")
            return
        self.canvas.delete("all")

        if self.groups:
            colors = {"Короткие": "green", "Средние": "blue", "Длинные": "red"}
            for group, segs in self.groups.items():
                for s in segs:
                    self.canvas.create_line(s.x1, s.y1, s.x2, s.y2, fill=colors[group], width=2)
        else:
            for s in self.segments:
                color = self.get_segment_color(s)
                self.canvas.create_line(s.x1, s.y1, s.x2, s.y2, fill=color, width=2)

        self.canvas.create_text(250, 20, text="Отрезки на плоскости", font=("Arial", 13, "bold"))

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
        self.update_info()

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
