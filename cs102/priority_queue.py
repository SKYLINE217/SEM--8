# CS 102 Requirement: PriorityQueue implementation
class PriorityQueue:
    def __init__(self):
        self.queue = []

    def push(self, item, priority):
        entry = (priority, item)
        self.queue.append(entry)
        self._bubble_up(len(self.queue) - 1)

    def pop(self):
        if not self.queue:
            return None
        if len(self.queue) == 1:
            return self.queue.pop()[1]
        
        root = self.queue[0][1]
        self.queue[0] = self.queue.pop()
        self._bubble_down(0)
        return root

    def _bubble_up(self, index):
        parent = (index - 1) // 2
        while index > 0 and self.queue[index][0] < self.queue[parent][0]:
            self.queue[index], self.queue[parent] = self.queue[parent], self.queue[index]
            index = parent
            parent = (index - 1) // 2

    def _bubble_down(self, index):
        child = 2 * index + 1
        while child < len(self.queue):
            if child + 1 < len(self.queue) and self.queue[child + 1][0] < self.queue[child][0]:
                child += 1
            if self.queue[index][0] <= self.queue[child][0]:
                break
            self.queue[index], self.queue[child] = self.queue[child], self.queue[index]
            index = child
            child = 2 * index + 1

    def is_empty(self):
        return len(self.queue) == 0
