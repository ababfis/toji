a = {'march': '31', "february": '28', 'january': '31', 'may': '31'}
b = input('введите название месяца, чтобы увидеть сколько в нем дней: ').lower()
print(a.get(b))