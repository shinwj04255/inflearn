def calculate(a, b):
    print(f"\n  {a} + {b} = {a + b}")
    print(f"  {a} - {b} = {a - b}")
    print(f"  {a} * {b} = {a * b}")
    print(f"  {a} / {b} = {a / b:.4f}" if b != 0 else f"  {a} / {b} = 나누기 불가 (0으로 나눌 수 없음)")

a = float(input("첫 번째 숫자: "))
b = float(input("두 번째 숫자: "))
calculate(a, b)
