# custom_data_structures.py


class Stack:
    def __init__(self):
        self.items = []

    def push(self, item):
        """Add an item to the stack."""
        self.items.append(item)

    def pop(self):
        """Remove and return the top item from the stack."""
        if not self.is_empty():
            return self.items.pop()
        return None

    def peek(self):
        """Return the top item without removing it."""
        if not self.is_empty():
            return self.items[-1]
        return None

    def is_empty(self):
        """Check if the stack is empty."""
        return len(self.items) == 0

    def size(self):
        """Return the number of items in the stack."""
        return len(self.items)

    def clear(self):
        """Clear all items from the stack."""
        self.items = []

    def contains(self, item):
        """Check if a specific item is in the stack."""
        return item in self.items

    def reverse(self):
        """Reverse the order of items in the stack."""
        self.items.reverse()

    def to_list(self):
        """Return the stack as a list."""
        return self.items[:]

    def print_stack(self):
        """Print all items in the stack (top to bottom)."""
        for item in reversed(self.items):
            print(item)


class Queue:
    def __init__(self):
        self.items = []

    def enqueue(self, item):
        """Add an item to the end of the queue."""
        self.items.append(item)

    def dequeue(self):
        """Remove and return the item at the front of the queue."""
        if not self.is_empty():
            return self.items.pop(0)
        return None

    def peek(self):
        """Return the front item without removing it."""
        if not self.is_empty():
            return self.items[0]
        return None

    def is_empty(self):
        """Check if the queue is empty."""
        return len(self.items) == 0

    def size(self):
        """Return the number of items in the queue."""
        return len(self.items)

    def clear(self):
        """Clear all items from the queue."""
        self.items = []

    def contains(self, item):
        """Check if a specific item is in the queue."""
        return item in self.items

    def reverse(self):
        """Reverse the order of items in the queue."""
        self.items.reverse()

    def to_list(self):
        """Return the queue as a list."""
        return self.items[:]

    def print_queue(self):
        """Print all items in the queue (front to back)."""
        for item in self.items:
            print(item)
