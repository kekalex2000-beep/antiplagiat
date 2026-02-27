import os
import hashlib
import re
import tkinter as tk
from tkinter import scrolledtext, messagebox, filedialog

def clr(t):
    t = re.sub(r'[^\w\s]', ' ', t)
    t = t.lower()
    return t.split()

def sh(w, n=3):
    r = []
    if len(w) < n:
        return r
    for i in range(len(w) - n + 1):
        s = w[i:i + n]
        r.append(' '.join(s))
    return r

def hsh(s):
    return hashlib.md5(s.encode('utf-8')).hexdigest()

def cmp(w1, w2, n):
    s1 = sh(w1, n)
    s2 = sh(w2, n)
    if not s1 or not s2:
        return 100.0
    h1 = [hsh(x) for x in s1]
    h2 = set([hsh(x) for x in s2])
    c = 0
    for x in h1:
        if x in h2:
            c += 1
    return round(((len(h1) - c) / len(h1)) * 100, 2)

def load(p="library"):
    lib = {}
    if not os.path.exists(p):
        os.makedirs(p)
        return lib
    for f in os.listdir(p):
        if f.endswith(".txt"):
            fp = os.path.join(p, f)
            try:
                with open(fp, 'r', encoding='utf-8') as file:
                    txt = file.read()
                lib[f] = clr(txt)
                print(f"Загружен: {f} ({len(lib[f])} слов)")
            except Exception as e:
                print(f"Ошибка {f}: {e}")
    return lib

def chk(w, lib, n):
    if not lib:
        return 100.0, "Пусто"
    m = 100.0
    src = "Нет"
    for name, words in lib.items():
        u = cmp(w, words, n)
        print(f"  {name}: {u}%")
        if u < m:
            m = u
            src = name
    return m, src

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Антиплагиат.СШ")
        self.root.geometry("750x600")
        self.lib = load("library")
        self.st = f"Файлов: {len(self.lib)}"
        self.ui()

    def ui(self):
        tk.Label(self.root, text=self.st).pack(pady=5)
        tk.Button(self.root, text="Обновить", command=self.ref).pack()
        f = tk.Frame(self.root)
        f.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        tk.Label(f, text="Текст:").pack(anchor=tk.W)
        self.t_in = scrolledtext.ScrolledText(f, height=8)
        self.t_in.pack(fill=tk.BOTH, expand=True)
        tk.Button(f, text="Загрузить", command=self.get).pack(pady=2)
        s = tk.Frame(self.root)
        s.pack(pady=5)
        tk.Label(s, text="Шингл:").pack(side=tk.LEFT)
        self.n_in = tk.Entry(s, width=5)
        self.n_in.insert(0, "3")
        self.n_in.pack(side=tk.LEFT, padx=5)
        tk.Button(s, text="Проверить", command=self.run).pack(side=tk.LEFT, padx=10)
        r = tk.Frame(self.root)
        r.pack(fill=tk.X, padx=10, pady=5)
        self.r1 = tk.Label(r, text="Уникальность: --%", font=("Arial", 14, "bold"))
        self.r1.pack()
        self.r2 = tk.Label(r, text="Источник: --")
        self.r2.pack()
        l = tk.Frame(self.root)
        l.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        tk.Label(l, text="Отчёт о проверке:").pack(anchor=tk.W)
        self.log = scrolledtext.ScrolledText(l, height=6, state=tk.DISABLED)
        self.log.pack(fill=tk.BOTH, expand=True)

    def wr(self, msg):
        self.log.config(state=tk.NORMAL)
        self.log.insert(tk.END, msg + "\n")
        self.log.see(tk.END)
        self.log.config(state=tk.DISABLED)
        self.root.update()

    def ref(self):
        self.lib = load("library")
        self.st = f"Файлов: {len(self.lib)}"
        self.wr(f"Обновлено. Загружено: {len(self.lib)}")

    def get(self):
        p = filedialog.askopenfilename(filetypes=[("Text files", "*.txt")])
        if p:
            try:
                with open(p, 'r', encoding='utf-8') as f:
                    data = f.read()
                self.t_in.delete(1.0, tk.END)
                self.t_in.insert(1.0, data)
                self.wr(f"Загружен: {p}")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось: {e}")

    def run(self):
        raw = self.t_in.get("1.0", tk.END).strip()
        if not raw:
            messagebox.showwarning("Внимание", "Введите текст!")
            return
        try:
            n = int(self.n_in.get())
            if n < 1:
                raise ValueError
        except:
            messagebox.showerror("Ошибка", "Шингл > 0")
            return
        if not self.lib:
            messagebox.showwarning("Внимание", "Библиотека пуста")
            return
        self.log.config(state=tk.NORMAL)
        self.log.delete(1.0, tk.END)
        self.log.config(state=tk.DISABLED)
        self.wr("="*50)
        self.wr("СТАРТ")
        self.wr(f"Шингл: {n}")
        self.wr(f"Файлов: {len(self.lib)}")
        self.wr("Шаг 1: Обработка...")
        w = clr(raw)
        self.wr(f"  Слов: {len(w)}")
        if len(w) < n:
            messagebox.showerror("Ошибка", "Слишком коротко")
            return
        self.wr("Шаг 2: Сравнение...")
        u, src = chk(w, self.lib, n)
        self.wr("Шаг 3: Готово")
        self.wr(f"  Уникальность: {u}%")
        self.wr(f"  Источник: {src}")
        self.wr("="*50)
        self.r1.config(text=f"Уникальность: {u}%")
        self.r2.config(text=f"Источник: {src}")

if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()
