class MovingAverage:
    def __init__(self, size):
        self.size = size
        self.buffer = [0] * size
        self.index = 0
        self.total = 0
        self.count = 0

    def update(self, value):
        self.total -= self.buffer[self.index]
        self.total += value
        self.buffer[self.index] = value
        self.index = (self.index + 1) % self.size
        if self.count < self.size:
            self.count += 1

    def average(self):
        if self.count == 0:
            return 0

        return self.total // self.count
