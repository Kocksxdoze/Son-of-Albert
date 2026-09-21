import random
from typing import Sequence
from engine import Value

class Neuron:
    def __init__(self,nin:int):
        """
        nin: number of inputs (кол-во вход синапсов)
        """

        #Создание случайных весов для каждого входа: от -1.0 до 1.0
        self.w: list[Value] = [Value(random.uniform(-1.0,1.0)) for _ in range(nin)]

        # случ смещение (bias)
        self.b: Value = Value(random.uniform(-1.0,1.0))

    def __call__(self, x: Sequence[float | Value]) -> Value:
        # Вычисление act = (w1*x1 + w2*x2 + ...) + b
        # Сумма со смещения self.b
        act = sum((wi*xi for wi, xi in zip(self.w, x)) , self.b)

        out = act.tanh()
        return out

    def parameters(self) -> list[Value]:
        # Возвращает все обучаемые настрйоки нейрона (веса + смещение)
        return self.w + [self.b]


if __name__ == "__main__":
    # 1. Создаем нейрон, который принимает 3 признака (например, из Empasis AI: тревога, стресс, пульс)
    n = Neuron(nin=3)
    print("Начальные веса нейрона:", n.w)
    print("Начальное смещение b:", n.b)
    # 2. Подаем на вход сигнал от человека
    x = [0.8, -0.5, 0.2]
    # 3. Прямой проход (Нейрон принимает решение!)
    out = n(x)
    print("\nРешение нейрона (от -1.0 до 1.0):", out)
    # 4. Обратный проход (Нейрон моментально вычисляет чувствительность всех своих весов!)
    out.backward()
    print("\nГрадиенты весов после обратного хода:")
    for i, w in enumerate(n.w):
        print(f"Градиент веса w[{i}]: {w.grad:.4f}")
    print(f"Градиент смещения b: {n.b.grad:.4f}")