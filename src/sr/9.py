a = int(input('введите число'))
b = 0
while a > 0:
    b += a%10
    a = a // 10
print(f'сумма чисел {b}')