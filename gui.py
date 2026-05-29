"""
Графический интерфейс калькулятора полива теплицы.
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from datetime import datetime
import json
from calculator import calculate_watering, load_coefficients, compare_cultures
import os

class WateringCalculatorGUI:
    """Основной класс графического интерфейса"""

    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Агротех: Калькулятор полива теплицы")
        self.root.geometry("700x800")
        self.root.resizable(True, True)

        # Загрузка коэффициентов
        try:
            self.coefficients = load_coefficients()
            self.cultures = list(self.coefficients["cultures"].keys())
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить коэффициенты:\n{e}")
            self.coefficients = {"cultures": {}}
            self.cultures = []

        # История расчётов
        self.history = []

        # Создание интерфейса
        self.create_widgets()

    def create_widgets(self):
        """Создание всех элементов интерфейса"""

        # Заголовок
        title_label = tk.Label(
            self.root,
            text="Калькулятор полива теплицы",
            font=("Arial", 16, "bold")
        )
        title_label.pack(pady=10)

        # Предупреждение об учебном характере
        warning_label = tk.Label(
            self.root,
            text="⚠ УЧЕБНАЯ МОДЕЛЬ. Не использовать для реального планирования!",
            font=("Arial", 10),
            fg="red"
        )
        warning_label.pack(pady=5)

        # Основной фрейм для ввода данных
        input_frame = tk.LabelFrame(self.root, text="Входные данные", padx=10, pady=10)
        input_frame.pack(fill="x", padx=10, pady=5)

        # Выбор культуры
        tk.Label(input_frame, text="Культура:").grid(row=0, column=0, sticky="w", pady=5)
        self.culture_var = tk.StringVar()
        self.culture_combo = ttk.Combobox(
            input_frame,
            textvariable=self.culture_var,
            values=self.cultures,
            state="readonly",
            width=30
        )
        self.culture_combo.grid(row=0, column=1, sticky="w", pady=5)
        if self.cultures:
            self.culture_combo.set(self.cultures[0])

        # Площадь
        tk.Label(input_frame, text="Площадь (м²):").grid(row=1, column=0, sticky="w", pady=5)
        self.area_var = tk.StringVar()
        self.area_entry = tk.Entry(input_frame, textvariable=self.area_var, width=32)
        self.area_entry.grid(row=1, column=1, sticky="w", pady=5)

        # Температура
        tk.Label(input_frame, text="Температура (°C):").grid(row=2, column=0, sticky="w", pady=5)
        self.temp_var = tk.StringVar()
        self.temp_entry = tk.Entry(input_frame, textvariable=self.temp_var, width=32)
        self.temp_entry.grid(row=2, column=1, sticky="w", pady=5)

        # Влажность почвы
        tk.Label(input_frame, text="Влажность почвы (%):").grid(row=3, column=0, sticky="w", pady=5)
        self.moisture_var = tk.StringVar()
        self.moisture_entry = tk.Entry(input_frame, textvariable=self.moisture_var, width=32)
        self.moisture_entry.grid(row=3, column=1, sticky="w", pady=5)

        # Фрейм для кнопок
        button_frame = tk.Frame(self.root)
        button_frame.pack(pady=10)

        # Кнопка расчёта
        self.calc_button = tk.Button(
            button_frame,
            text="Рассчитать",
            command=self.on_calculate,
            bg="#4CAF50",
            fg="white",
            font=("Arial", 11),
            padx=20,
            pady=5
        )
        self.calc_button.pack(side="left", padx=5)

        # Кнопка очистки
        self.clear_button = tk.Button(
            button_frame,
            text="Очистить",
            command=self.on_clear,
            bg="#f44336",
            fg="white",
            font=("Arial", 11),
            padx=20,
            pady=5
        )
        self.clear_button.pack(side="left", padx=5)

        # Кнопка сравнения культур
        self.compare_button = tk.Button(
            button_frame,
            text="Сравнить культуры",
            command=self.on_compare,
            bg="#2196F3",
            fg="white",
            font=("Arial", 11),
            padx=20,
            pady=5
        )
        self.compare_button.pack(side="left", padx=5)

        # Результат
        result_frame = tk.LabelFrame(self.root, text="Результат расчёта", padx=10, pady=10)
        result_frame.pack(fill="both", expand=True, padx=10, pady=5)

        self.result_text = scrolledtext.ScrolledText(
            result_frame,
            height=12,
            wrap=tk.WORD,
            font=("Courier", 10)
        )
        self.result_text.pack(fill="both", expand=True)

        # История расчётов
        history_frame = tk.LabelFrame(self.root, text="История последних расчётов", padx=10, pady=10)
        history_frame.pack(fill="both", expand=True, padx=10, pady=5)

        self.history_text = scrolledtext.ScrolledText(
            history_frame,
            height=8,
            wrap=tk.WORD,
            font=("Courier", 9)
        )
        self.history_text.pack(fill="both", expand=True)

        # Кнопка экспорта истории
        export_button = tk.Button(
            history_frame,
            text="Экспорт истории в файл",
            command=self.on_export_history,
            bg="#FF9800",
            fg="white",
            font=("Arial", 9),
            padx=10
        )
        export_button.pack(pady=5)

    def validate_input(self):
        """Валидация и получение числовых значений из полей ввода"""
        try:
            area = float(self.area_var.get().replace(",", "."))
        except ValueError:
            raise ValueError("Площадь должна быть числом")

        try:
            temperature = float(self.temp_var.get().replace(",", "."))
        except ValueError:
            raise ValueError("Температура должна быть числом")

        try:
            moisture = float(self.moisture_var.get().replace(",", "."))
        except ValueError:
            raise ValueError("Влажность должна быть числом")

        return area, temperature, moisture

    def on_calculate(self):
        """Обработчик кнопки 'Рассчитать'"""
        try:
            culture = self.culture_var.get()
            if not culture:
                raise ValueError("Выберите культуру")

            area, temperature, moisture = self.validate_input()

            # Расчёт
            volume, formula = calculate_watering(
                culture, area, temperature, moisture, self.coefficients
            )

            # Вывод результата
            self.result_text.delete(1.0, tk.END)
            self.result_text.insert(tk.END, f"Расчёт полива для культуры: {culture}\n")
            self.result_text.insert(tk.END, "=" * 60 + "\n\n")
            self.result_text.insert(tk.END, "Формула с подстановкой значений:\n")
            self.result_text.insert(tk.END, "-" * 40 + "\n")
            self.result_text.insert(tk.END, formula + "\n\n")
            self.result_text.insert(tk.END, "=" * 60 + "\n")
            self.result_text.insert(tk.END, f"РЕЗУЛЬТАТ: {volume} литров\n")
            self.result_text.insert(tk.END, f"РЕЗУЛЬТАТ: {round(volume / 1000, 3)} м³\n")

            # Добавление в историю
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            history_entry = {
                "timestamp": timestamp,
                "culture": culture,
                "area": area,
                "temperature": temperature,
                "moisture": moisture,
                "volume": volume
            }
            self.history.append(history_entry)
            self.update_history_display()

        except Exception as e:
            messagebox.showerror("Ошибка", str(e))

    def on_clear(self):
        """Очистка полей ввода"""
        self.area_var.set("")
        self.temp_var.set("")
        self.moisture_var.set("")
        self.result_text.delete(1.0, tk.END)

    def on_compare(self):
        """Сравнение двух культур"""
        # Создание диалогового окна для выбора второй культуры
        dialog = tk.Toplevel(self.root)
        dialog.title("Сравнение культур")
        dialog.geometry("500x400")
        dialog.transient(self.root)
        dialog.grab_set()

        tk.Label(dialog, text="Выберите вторую культуру для сравнения:", font=("Arial", 11)).pack(pady=10)

        culture2_var = tk.StringVar()
        other_cultures = [c for c in self.cultures if c != self.culture_var.get()]
        if not other_cultures:
            messagebox.showinfo("Информация", "Нет других культур для сравнения")
            dialog.destroy()
            return

        culture2_combo = ttk.Combobox(
            dialog,
            textvariable=culture2_var,
            values=other_cultures,
            state="readonly",
            width=30
        )
        culture2_combo.pack(pady=5)
        culture2_combo.set(other_cultures[0])

        def do_compare():
            try:
                culture1 = self.culture_var.get()
                culture2 = culture2_var.get()
                area, temperature, moisture = self.validate_input()

                result = compare_cultures(
                    culture1, culture2, area, temperature, moisture, self.coefficients
                )

                # Вывод результатов сравнения
                self.result_text.delete(1.0, tk.END)
                self.result_text.insert(tk.END, "СРАВНЕНИЕ ДВУХ КУЛЬТУР\n")
                self.result_text.insert(tk.END, "=" * 60 + "\n\n")

                self.result_text.insert(tk.END, f"Культура 1: {result['culture1']['name']}\n")
                self.result_text.insert(tk.END, "-" * 40 + "\n")
                self.result_text.insert(tk.END, result['culture1']['formula'] + "\n\n")

                self.result_text.insert(tk.END, f"Культура 2: {result['culture2']['name']}\n")
                self.result_text.insert(tk.END, "-" * 40 + "\n")
                self.result_text.insert(tk.END, result['culture2']['formula'] + "\n\n")

                self.result_text.insert(tk.END, "=" * 60 + "\n")
                self.result_text.insert(
                    tk.END,
                    f"Разница: {result['difference_l']} литров ({result['difference_percent']}%)\n"
                )

                dialog.destroy()

            except Exception as e:
                messagebox.showerror("Ошибка", str(e))

        tk.Button(
            dialog,
            text="Сравнить",
            command=do_compare,
            bg="#2196F3",
            fg="white",
            font=("Arial", 11),
            padx=20,
            pady=5
        ).pack(pady=20)

    def update_history_display(self):
        """Обновление отображения истории расчётов"""
        self.history_text.delete(1.0, tk.END)

        # Показываем последние 10 записей
        for entry in self.history[-10:]:
            self.history_text.insert(
                tk.END,
                f"[{entry['timestamp']}] {entry['culture']}: "
                f"площадь={entry['area']}м², t={entry['temperature']}°C, "
                f"влаж={entry['moisture']}% → {entry['volume']}л\n"
            )

    def on_export_history(self):
        """Экспорт истории расчётов в файл"""
        if not self.history:
            messagebox.showinfo("Информация", "История расчётов пуста")
            return

        try:
            filename = f"watering_history_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(filename, "w", encoding="utf-8") as f:
                json.dump(self.history, f, ensure_ascii=False, indent=2)

            messagebox.showinfo("Успех", f"История экспортирована в файл:\n{filename}")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось экспортировать историю:\n{e}")