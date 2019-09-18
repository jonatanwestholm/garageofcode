def fibonacci(n):
    a = 1
    b = 1
    while b <= n:
        yield b
        a, b = b, a + b

print("Numbers:", list(fibonacci(40)))
print("Sum:", sum(filter(lambda x: x % 2 == 0, fibonacci(4e6))))