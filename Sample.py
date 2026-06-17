x=1


class Task:
    def __init__(self, task_id, title, status="To Do", assignee=None):
        self.task_id = task_id
        self.title = title
        self.status = status
        self.assignee = assignee


def greet():
    print("Hello, World!")

greet()




# Simple Calculator Program

class Calculator:
    """A simple calculator class for basic arithmetic operations."""

    @staticmethod
    def add(a, b):
        return a + b

    @staticmethod
    def subtract(a, b):
        return a - b

    @staticmethod
    def multiply(a, b):
        return a * b

    @staticmethod
    def divide(a, b):
        if b == 0:
            return "Error: Cannot divide by zero"
        return a / b

    @staticmethod
    def power(a, b):
        return a ** b

    @staticmethod
    def square_root(a):
        if a < 0:
            return "Error: Cannot calculate square root of a negative number"
        return a ** 0.5

    @staticmethod
    def percentage(a, b):
        if b == 0:
            return "Error: Cannot divide by zero"
        return (a / b) * 100

    @staticmethod
    def modulo(a, b):
        if b == 0:
            return "Error: Cannot divide by zero"
        return a % b


def calculator():
    print("=" * 40)
    print("      SIMPLE CALCULATOR")
    print("=" * 40)
    print("1. Add")
    print("2. Subtract")
    print("3. Multiply")
    print("4. Divide")
    print("5. Power")
    print("6. Square Root")
    print("7. Percentage")
    print("8. Modulo")
    print("9. Exit")

    calc = Calculator()

    while True:
        choice = input("\nChoose operation (1-9): ").strip()

        if choice == '9':
            print("Goodbye!")
            break

        if choice in ['1', '2', '3', '4', '5', '7', '8']:
            try:
                num1 = float(input("Enter first number: "))
                num2 = float(input("Enter second number: "))
            except ValueError:
                print("Invalid number entered.")
                continue

            if choice == '1':
                print(f"Result: {calc.add(num1, num2)}")
            elif choice == '2':
                print(f"Result: {calc.subtract(num1, num2)}")
            elif choice == '3':
                print(f"Result: {calc.multiply(num1, num2)}")
            elif choice == '4':
                print(f"Result: {calc.divide(num1, num2)}")
            elif choice == '5':
                print(f"Result: {calc.power(num1, num2)}")
            elif choice == '7':
                print(f"Result: {calc.percentage(num1, num2)}%")
            elif choice == '8':
                print(f"Result: {calc.modulo(num1, num2)}")

        elif choice == '6':
            try:
                num = float(input("Enter a number: "))
            except ValueError:
                print("Invalid number entered.")
                continue
            print(f"Result: {calc.square_root(num)}")

        else:
            print("Invalid choice. Please enter 1-9.")


if __name__ == '__main__':
    calculator()


