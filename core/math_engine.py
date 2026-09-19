import math

def dot(v1: list[float], v2: list[float]) -> float: # Алгоритм скалярного произведения
    total = 0.0
    if len(v1) != len(v2):
        raise ValueError("Векторы должны быть одинаковой длины!")

    for i in range(len(v1)):
        total += v1[i] * v2[i]
    return total

def vector_magnitude(v: list[float]) -> float: # длинна вектора (Евклидова норма/ L2)
    total = 0.0
    for i in v:
        total += i**2
    return math.sqrt(total)

def cs(v1:list[float], v2:list[float]): # косинусное сходство
    high = dot(v1,v2)
    low = vector_magnitude(v1) * vector_magnitude(v2)

    if low == 0:
        raise ValueError("Не делится на 0")

    return high / low

def matrix_vector(matrix: list[list[float]], vector:list[float]) -> list[float]: # алгоритм прямого прохода слоя нейросети
    result = []

    if len(matrix[0]) != len(vector):
        raise ValueError

    for i in matrix:       
        result.append(dot(i, vector))
    return result

print(matrix_vector([ [1.0, 2.0],[3.0, 4.0]],[0.5, 2.0]))

def matrix_transpose(matrix: list[list[float]]) -> list[list[float]]: # поворот матрицы
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
    


normal = [80.0, 500.0, 0.1]        
suspicious = [80.0, 510.0, 0.11]    
ddos = [443.0, 150000.0, 0.0001]    


# print(cs(normal, suspicious))
# print(cs(normal,ddos))