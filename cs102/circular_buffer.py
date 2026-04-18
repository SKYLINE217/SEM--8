# CS 102 Requirement: O(1) circular buffer implementation
class CircularBuffer:
    def __init__(self, maxlen):
        self.buffer = [None] * maxlen
        self.maxlen = maxlen
        self.head = 0
        self.tail = 0
        self.size = 0

    def append(self, item):
        self.buffer[self.head] = item
        self.head = (self.head + 1) % self.maxlen
        if self.size < self.maxlen:
            self.size += 1
        else:
            self.tail = (self.tail + 1) % self.maxlen

    def get(self):
        if self.size == 0:
            return None
        item = self.buffer[self.tail]
        self.tail = (self.tail + 1) % self.maxlen
        self.size -= 1
        return item

    def is_empty(self):
        return self.size == 0
