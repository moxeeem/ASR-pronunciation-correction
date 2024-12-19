from typing import Sequence, Any
import numpy as np


# версия на чистом Python, не использующая внешних библиотек
def edit_distance_python(a: str, b: str):
    """
    Вычисляет расстояние Левенштейна между двумя строками `a` и `b`.
    Расстояние Левенштейна — это минимальное количество операций (вставка, удаление, замена),
    необходимых для преобразования одной строки в другую.

    Аргументы:
        a (str): Первая строка.
        b (str): Вторая строка.

    Возвращает:
        int: Расстояние Левенштейна между строками `a` и `b`.
    """
    # для оптимизации: если длина строки `a` меньше,
    # чем `b` - меняем их местами
    if len(a) < len(b):
        return edit_distance_python(b, a)

    # если строка `b` пустая, то расстояние
    # равно длине строки `a` (все символы нужно удалить)
    if len(b) == 0:
        return len(a)

    # только две строки (предыдущая и текущая)
    # нужны для хранения промежуточных данных
    distances = []
    distances.append(
        [i for i in range(len(b) + 1)]
    )  # Первая строка с начальными значениями
    distances.append(
        [0 for _ in range(len(b) + 1)]
    )  # Вторая строка для текущих вычислений
    costs = [
        0 for _ in range(3)
    ]  # Вспомогательный массив для хранения стоимости операций

    # Проходим по символам строки `a`
    for i, a_token in enumerate(a, start=1):
        distances[1][0] += (
            1  # Обновляем первый элемент строки (удаление символа из `a`)
        )
        for j, b_token in enumerate(b, start=1):
            # Три варианта операций: вставка, удаление и замена
            costs[0] = distances[1][j - 1] + 1  # Вставка
            costs[1] = distances[0][j] + 1  # Удаление
            costs[2] = distances[0][j - 1] + (
                0 if a_token == b_token else 1
            )  # Замена, если символы разные
            distances[1][j] = min(costs)  # Выбираем минимальную стоимость операции
        # Переходим к следующей строке
        distances[0][:] = distances[1][:]

    # Возвращаем расстояние Левенштейна (последний элемент в строке)
    return distances[1][len(b)]


# версия с использованием библиотеки numpy
def edit_distance_numpy(seq1: Sequence[Any], seq2: Sequence[Any]):
    """
    Вычисляет расстояние Левенштейна между двумя строками `seq1` и `seq2`
    с использованием матрицы NumPy для хранения промежуточных результатов.

    Аргументы:
        seq1 (str): Первая строка.
        seq2 (str): Вторая строка.

    Возвращает:
        int: Расстояние Левенштейна между строками `seq1` и `seq2`.
    """
    # определяем размеры матрицы для хранения промежуточных результатов
    size_x = len(seq1) + 1
    size_y = len(seq2) + 1

    # инициализируем матрицу нулями
    matrix = np.zeros((size_x, size_y))

    # заполняем первую строку и первый столбец (границы матрицы)
    for x in range(size_x):
        matrix[x, 0] = x  # Заполнение первой колонки (удаление символов)

    for y in range(size_y):
        matrix[0, y] = y  # Заполнение первой строки (вставка символов)

    # заполняем оставшуюся часть матрицы
    for x in range(1, size_x):
        for y in range(1, size_y):
            # если символы совпадают, то стоимость замены равна 0
            if seq1[x - 1] == seq2[y - 1]:
                matrix[x, y] = min(
                    matrix[x - 1, y] + 1,  # Удаление
                    matrix[x - 1, y - 1],  # Совпадение/замена
                    matrix[x, y - 1] + 1,  # Вставка
                )
            else:
                # если символы не совпадают, то стоимость замены равна 1
                matrix[x, y] = min(
                    matrix[x - 1, y] + 1,  # Удаление
                    matrix[x - 1, y - 1] + 1,  # Замена
                    matrix[x, y - 1] + 1,  # Вставка
                )

    # возвращаем расстояние Левенштейна (последний элемент матрицы)
    return matrix[size_x - 1, size_y - 1]
