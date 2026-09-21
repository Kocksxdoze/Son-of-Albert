import math

# Алгоритм скалярного произведения
def dot(v1: list[float], v2: list[float]) -> float: 
    total = 0.0
    if len(v1) != len(v2):
        raise ValueError("Векторы должны быть одинаковой длины!")

    for i in range(len(v1)):
        total += v1[i] * v2[i]
    return total

# длина вектора (Евклидова норма/ L2)
def vector_magnitude(v: list[float]) -> float: 
    total = 0.0
    for i in v:
        total += i**2
    return math.sqrt(total)

# косинусное сходство
def cs(v1:list[float], v2:list[float]): 
    high = dot(v1,v2)
    low = vector_magnitude(v1) * vector_magnitude(v2)

    if low == 0:
        raise ValueError("Не делится на 0")

    return high / low

# алгоритм прямого прохода слоя нейросети
def matrix_vector(matrix: list[list[float]], vector:list[float]) -> list[float]: 
    result = []

    if len(matrix[0]) != len(vector):
        raise ValueError

    for i in matrix:       
        result.append(dot(i, vector))
    return result

print(matrix_vector([ [1.0, 2.0],[3.0, 4.0]],[0.5, 2.0]))

# поворот матрицы
def matrix_transpose(matrix: list[list[float]]) -> list[list[float]]: 
    transpose = []
    num_cols = len(matrix[0])
    num_rows = len(matrix)

    for i in range(num_cols):
        new_row = []
        for j in range(num_rows):
            new_row.append(matrix[j][i])
        transpose.append(new_row)
    return transpose

print(matrix_transpose([[1, 2], [3, 4], [5, 6]]))