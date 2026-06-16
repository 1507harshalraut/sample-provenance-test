# AI Provenance full test file
# Run through all scenarios in the test checklist, then commit.

def hello():
    print("human typed baseline")


x = 1
# Plugin Development


def greet():
    print("Hello, World!")

greet()


class Task:
    def __init__(self, task_id, title, status="To Do", assignee=None):
        self.task_id = task_id
        self.title = title
        self.status = status
        self.assignee = assignee


def create_task(task_id, title):
    return Task(task_id, title)


def fib(n):
    a, b = 0, 1
    seq = []
    for _ in range(n):
        seq.append(a)
        a, b = b, a + b
    return seq


def calculator(a, b, op):
    ops = {
        "+": lambda x, y: x + y,
        "-": lambda x, y: x - y,
        "*": lambda x, y: x * y,
        "/": lambda x, y: "undefined" if y == 0 else x / y,
        "%": lambda x, y: "undefined" if y == 0 else x % y,
    }
    return ops.get(op, lambda *_: "unsupported operation")(a, b)


def main():
    print("Fibonacci 10:", fib(10))
    print("12 + 5 =", calculator(12, 5, "+"))
    print("12 * 5 =", calculator(12, 5, "*"))


if __name__ == "__main__":
    main()