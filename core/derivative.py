from typing import Callable

def derivative(f: Callable[[float],float], x: float, h:float =1e-5) -> float:
    moved = f(x+h)
    no_moved = f(x)

    return (moved - no_moved) / h

def square(x:float) -> float:
    return x**2

def loss(w: float) -> float:
    return (w-5.0) **2

print("Численная производная в точке x=3:", derivative(square,3.00))
w = -10.0
learning_rate = 0.1

print(f"Старт: вес w={w}, ошибка = {square(w)}")

for e in range(20):
    grad = derivative(loss,w)

    w = w - (learning_rate*grad)

    print(f"Шаг: {e + 1}: w = {w:.4f}, ошибка: = {loss(w):.4f}")
