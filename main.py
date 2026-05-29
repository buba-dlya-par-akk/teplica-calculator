"""
Агротех: калькулятор полива теплицы
Точка входа в приложение
"""

import tkinter as tk
import sys
import os

# Добавление src в путь для импортов
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from gui import WateringCalculatorGUI


def main():
    """Запуск приложения"""
    try:
        root = tk.Tk()
        app = WateringCalculatorGUI(root)
        root.mainloop()
    except Exception as e:
        print(f"Критическая ошибка: {e}")
        import traceback
        traceback.print_exc()
        input("Нажмите Enter для выхода...")


if __name__ == "__main__":
    main()