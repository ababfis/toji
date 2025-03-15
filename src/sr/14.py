class car:
    def __init__(self, car, brand, speed):
        self.car = car
        self.brand = brand
        self.speed = speed
        
    def increase_speed(self):
        a = int(input('введите число на которое надо увеличить скорость: '))
        self.speed += a
        print(self.speed)


atr1 = car('bmw', 'aboba', 1488)
atr1.increase_speed()