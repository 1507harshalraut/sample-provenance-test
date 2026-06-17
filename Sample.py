x=1
y=2
z=x+y
print(z)



class Task:
    def __init__(self, task_id, title, status="To Do", assignee=None):
        self.task_id = task_id
        self.title = title
        self.status = status
        self.assignee = assignee



def greet():
    print("Hello, World!")


def add(a, b):
    return a + b


def subtract(a, b):
    return a - b


def multiply(a, b):
    return a * b


def divide(a, b):
    if b == 0:
        raise ValueError("Cannot divide by zero")
    return a / b


def calculator():
    print("\nSimple Calculator")
    while True:
        print("\nChoose an operation:")
        print("1. Add")
        print("2. Subtract")
        print("3. Multiply")
        print("4. Divide")
        print("5. Exit")

        choice = input("Enter choice (1-5): ")
        if choice == "5":
            print("Exiting calculator.")
            break

        if choice not in {"1", "2", "3", "4"}:
            print("Invalid choice. Please choose a number between 1 and 5.")
            continue

        try:
            a = float(input("Enter first number: "))
            b = float(input("Enter second number: "))
        except ValueError:
            print("Invalid input. Please enter numeric values.")
            continue

        try:
            if choice == "1":
                result = add(a, b)
            elif choice == "2":
                result = subtract(a, b)
            elif choice == "3":
                result = multiply(a, b)
            else:
                result = divide(a, b)
        except ValueError as err:
            print(err)
            continue

        print(f"Result: {result}")


if __name__ == "__main__":
    greet()
    calculator()



