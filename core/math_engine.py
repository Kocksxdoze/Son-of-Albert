import math

def dot(v1: list[float], v2: list[float]) -> float:
    total = 0.0
    if len(v1) != len(v2):
        raise ValueError("Векторы должны быть одинаковой длины!")

    for i in range(len(v1)):
        total += v1[i] * v2[i]
    return total

# print(dot([1,2],[2,1]))

def vector_magnitude(v: list[float]) -> float:
    total = 0.0
    for i in v:
        total += i**2
    return math.sqrt(total)

# print(vector_magnitude([4,5]))

def cs(v1:list[float], v2:list[float]):
    high = dot(v1,v2)
    low = vector_magnitude(v1) * vector_magnitude(v2)

    if low == 0:
        raise ValueError("Не делится на 0")

    return high / low

# print(cs([3,4],[2,1]))

normal = [80.0, 500.0, 0.1]        
suspicious = [80.0, 510.0, 0.11]    
ddos = [443.0, 150000.0, 0.0001]    
print("Сходство нормального с похожим:", cs(normal, suspicious))
print("Сходство нормального с DDoS:", cs(normal, ddos))