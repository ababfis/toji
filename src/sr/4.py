a = input('введите строку: ')
b = 'аеуыоэяиюУЕЫАОЭЯИЮ'
for i in a:
    if i in b:
        print(i)
