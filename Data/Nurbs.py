

class Nurbs(object):
    def __init__(self):
        self._knots = [0,0,0,1,1,1]
        self._weights = None
        self._controls = []
        self._degree = 2

    def set_controls(self, controls):
        self._controls = controls
        self._knots.clear()
        self._weights = None
        self._knots.append(0.0)
        self._knots.append(0.0)
        for i in range(len(controls)-1):
            k = i/(len(controls)-2)
            self._knots.append(k)
        self._knots.append(1)
        self._knots.append(1)

    def g(self, i, n, u):
        num = self._knots[i+n] - u
        denom = self._knots[i+n] - self._knots[i]
        if denom == 0.0:
            denom = 1.0e-30
        return num / denom

    def f(self, i, n, u):
        num = u - self._knots[i]
        denom = self._knots[i + n] - self._knots[i]
        if denom == 0.0:
            denom = 1.0e-30
        return num / denom

    def N(self, i, n, u):
        if n == 0:
            if self._knots[i] <= u < self._knots[i+1]:
                return 1.0
            elif u == self._knots[i+1] and i+2 == len(self._knots):
                return 1.0
            return 0.0
        return self.f(i, n, u) * self.N(i, n-1, u) + self.g(i+1, n, u) * self.N(i+1, n-1, u)

    def R(self, i, n, u):
        if self._weights is None:
            return self.N(i, n, u)
        else:
            num = self.N(i, n, u) * self._weights[i]
            denom = 0.0
            for j in range(self._controls):
                denom += self.N(j, n, u) * self._weights[i]
            return num / denom

    def C(self, u):
        c = None
        n = self._degree
        for i in range(len(self._controls)):
            P = self._controls[i]
            if c is None:
                c = self.R(i, n, u) * P
            else:
                c += self.R(i, n, u) * P
        return c