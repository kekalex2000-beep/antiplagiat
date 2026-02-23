import os
import hashlib
import re
import tkinter as tk
from tkinter import scrolledtext, messagebox, filedialog

def preprocess_text(text):
    
    # Удаляем все символы, кроме букв и пробелов
    text = re.sub(r'[^\w\s]', ' ', text)
    # Приводим к нижнему регистру
    text = text.lower()
    # Разбиваем на слова
    words = text.split()
    return words

def generate_shingles(words, shingle_size=3):
    
    shingles = []
    if len(words) < shingle_size:
        return shingles

    for i in range(len(words) - shingle_size + 1):
        shingle = words[i:i + shingle_size]
        shingle_str = ' '.join(shingle)
        shingles.append(shingle_str)
    return shingles

def hash_shingle(shingle):
    
    return hashlib.md5(shingle.encode('utf-8')).hexdigest()

def calculate_uniqueness_for_pair(text1_words, text2_words, shingle_size):
    
    # Генерация шинглов
    shingles1 = generate_shingles(text1_words, shingle_size)
    shingles2 = generate_shingles(text2_words, shingle_size)

    if not shingles1 or not shingles2:
        return 100.0  # Если нет шинглов для сравнения, считаем текст уникальным

    # Хеширование
    hashes1 = [hash_shingle(s) for s in shingles1]
    hashes2_set = set([hash_shingle(s) for s in shingles2])

    # Подсчет совпадений
    matches = 0
    for h in hashes1:
        if h in hashes2_set:
            matches += 1

    # Расчет уникальности
    total = len(hashes1)
    uniqueness = ((total - matches) / total) * 100
    return round(uniqueness, 2)

def load_library_from_folder(folder_path="library"):
    
    library = {}
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)  # Создаем папку, если её нет
        return library

    for filename in os.listdir(folder_path):
        if filename.endswith(".txt"):
            file_path = os.path.join(folder_path, filename)
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    text = f.read()
                # Сразу обрабатываем текст и сохраняем слова
                words = preprocess_text(text)
                library[filename] = words
                print(f"Загружен файл: {filename} ({len(words)} слов)")
            except Exception as e:
                print(f"Ошибка загрузки {filename}: {e}")
    return library

def check_text_against_library(check_words, library, shingle_size):
    
    if not library:
        return 100.0, "Библиотека пуста"

    min_uniqueness = 100.0
    worst_source = "Не найдено"

    for filename, lib_words in library.items():
        uniqueness = calculate_uniqueness_for_pair(check_words, lib_words, shingle_size)
        # Логируем промежуточные результаты
        print(f"  Сравнение с {filename}: уникальность {uniqueness}%")
        if uniqueness < min_uniqueness:
            min_uniqueness = uniqueness
            worst_source = filename

    return min_uniqueness, worst_source

class AntiplagiatApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Прототип Антиплагиата (с библиотекой)")
        self.root.geometry("750x600")

        # Загружаем библиотеку при старте
        self.library = load_library_from_folder("library")
        self.lib_status = f"Библиотека: {len(self.library)} файлов загружено"

        self.create_widgets()

    def create_widgets(self):
        # Статус библиотеки
        lib_label = tk.Label(self.root, text=self.lib_status, font=("Arial", 10))
        lib_label.pack(pady=5)

        # Кнопка обновления библиотеки
        refresh_btn = tk.Button(self.root, text="Обновить библиотеку", command=self.refresh_library)
        refresh_btn.pack(pady=2)

        # Рамка для текста
        frame = tk.Frame(self.root)
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # Текст для проверки
        tk.Label(frame, text="Текст для проверки:").pack(anchor=tk.W)
        self.text_input = scrolledtext.ScrolledText(frame, height=8)
        self.text_input.pack(fill=tk.BOTH, expand=True, pady=5)

        # Кнопка загрузки из файла
        load_btn = tk.Button(frame, text="Загрузить текст из файла", command=self.load_from_file)
        load_btn.pack(pady=2)

        # Настройки
        settings_frame = tk.Frame(self.root)
        settings_frame.pack(pady=5)

        tk.Label(settings_frame, text="Длина шингла:").pack(side=tk.LEFT)
        self.shingle_size_entry = tk.Entry(settings_frame, width=5)
        self.shingle_size_entry.insert(0, "3")
        self.shingle_size_entry.pack(side=tk.LEFT, padx=5)

        # Кнопка проверки
        check_btn = tk.Button(settings_frame, text="Проверить уникальность", command=self.check)
        check_btn.pack(side=tk.LEFT, padx=10)

        # Результаты
        result_frame = tk.Frame(self.root)
        result_frame.pack(fill=tk.X, padx=10, pady=5)

        self.result_label = tk.Label(result_frame, text="Уникальность: --%", font=("Arial", 14, "bold"))
        self.result_label.pack()

        self.source_label = tk.Label(result_frame, text="Источник: --", font=("Arial", 10))
        self.source_label.pack()

        # Лог (для отладки)
        log_frame = tk.Frame(self.root)
        log_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        tk.Label(log_frame, text="Лог выполнения:").pack(anchor=tk.W)
        self.log_text = scrolledtext.ScrolledText(log_frame, height=6, state=tk.DISABLED)
        self.log_text.pack(fill=tk.BOTH, expand=True)

    def log(self, message):
        """Добавляет сообщение в лог-область"""
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)
        self.root.update()

    def refresh_library(self):
        self.library = load_library_from_folder("library")
        self.lib_status = f"Библиотека: {len(self.library)} файлов загружено"
        # Обновляем надпись (нужно пересоздать или обновить, для простоты можно просто показать в логе)
        self.log(f"Библиотека обновлена. Загружено файлов: {len(self.library)}")

    def load_from_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("Text files", "*.txt")])
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                self.text_input.delete(1.0, tk.END)
                self.text_input.insert(1.0, content)
                self.log(f"Загружен файл: {file_path}")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось загрузить файл: {e}")

    def check(self):
        # Получаем текст из поля ввода
        raw_text = self.text_input.get("1.0", tk.END).strip()
        if not raw_text:
            messagebox.showwarning("Предупреждение", "Введите текст для проверки!")
            return

        # Получаем длину шингла
        try:
            shingle_size = int(self.shingle_size_entry.get())
            if shingle_size < 1:
                raise ValueError
        except:
            messagebox.showerror("Ошибка", "Длина шингла должна быть положительным целым числом")
            return

        # Проверяем, загружена ли библиотека
        if not self.library:
            messagebox.showwarning("Предупреждение", "Библиотека пуста. Добавьте .txt файлы в папку 'library'")
            return

        # Очищаем лог
        self.log_text.config(state=tk.NORMAL)
        self.log_text.delete(1.0, tk.END)
        self.log_text.config(state=tk.DISABLED)

        self.log("="*50)
        self.log("НАЧАЛО ПРОВЕРКИ")
        self.log(f"Длина шингла: {shingle_size}")
        self.log(f"Размер библиотеки: {len(self.library)} файлов")

        # Обработка проверяемого текста
        self.log("Этап 1: Предобработка текста...")
        check_words = preprocess_text(raw_text)
        self.log(f"  Получено слов: {len(check_words)}")

        if len(check_words) < shingle_size:
            messagebox.showerror("Ошибка", "Текст слишком короткий для выбранной длины шингла")
            return

        # Проверка по библиотеке
        self.log("Этап 2: Сравнение с библиотекой...")
        min_uniqueness, worst_source = check_text_against_library(check_words, self.library, shingle_size)

        # Вывод результатов
        self.log("Этап 3: Анализ завершен")
        self.log(f"  Итоговая уникальность: {min_uniqueness}%")
        self.log(f"  Основной источник заимствований: {worst_source}")
        self.log("="*50)

        self.result_label.config(text=f"Уникальность: {min_uniqueness}%")
        self.source_label.config(text=f"Источник: {worst_source}")

if __name__ == "__main__":
    root = tk.Tk()
    app = AntiplagiatApp(root)
    root.mainloop()
