import math

class Value:
    def __init__(self,data:float,_children=(),_op: str = ""):
        self.data: float = float(data)
        self.grad: float = 0.0
        self._prev: set['Value'] = set(_children)
        self._op: str = _op
        self._backward = lambda: None

    def __repr__(self) -> str:
        return f"Value(data={self.data}, grad={self.grad})"

    def __add__(self, other):
        other = other if isinstance(other, Value) else Value(other)
        out = Value(self.data + other.data, _children=(self,other), _op="+")

        def _backward():
            self.grad += 1.0 * out.grad
            other.grad += 1.0 * out.grad
        out._backward = _backward
        return out

    def __radd__(self, other):
        return self + other

    def __mul__(self, other):
        other = other if isinstance(other, Value) else Value(other)
        out = Value(self.data * other.data, _children=(self, other), _op="*")

        def _backward():
            self.grad += other.data * out.grad
            other.grad += self.data * out.grad
        out._backward = _backward
        return out

    def __rmul__(self, other):
        return self * other

    def tanh(self) -> 'Value':
        x = self.data

        # формула tanh: (e^(2x) - 1) / (e^(2x) + 1)
        # Защита от переполнения при слишком больших x
        if x > 20:
            t = 1.0
        elif x < -20:
            t = -1.0
        else:
            t = (math.exp(2*x) - 1) / (math.exp(2*x) + 1)

        out = Value(t, _children=(self,), _op="tanh")

        def _backward():
            self.grad += (1.0 - t**2) * out.grad
        out._backward = _backward
        return out

    def backward(self):
        # Алгоритм топологической сортировки графа вычислений
        topo: list['Value'] = []
        visited: set['Value'] = set()

        def build(v: 'Value'):
            if v not in visited:
                visited.add(v)
                for child in v._prev:
                    build(child)
                topo.append(v)

        build(self)

        # Запуск градиентов с начала д оконца
        self.grad = 1.0
        for node in reversed(topo):
            node._backward()

if __name__ == "__main__":
    a = Value(2.0)
    b = Value(-3.0)
    c = Value(10.0)
    d = (a * b) + c
    # Теперь ОДНА строчка делает всю магию!
    d.backward()
    print("d:", d)
    print("a.grad (должен быть -3.0):", a.grad)
    print("b.grad (должен быть 2.0):", b.grad)
    print("c.grad (должен быть 1.0):", c.grad)