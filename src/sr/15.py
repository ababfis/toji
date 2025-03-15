class person:
    def __init__(self, name, age):
        self.name = name
        self.age = age
        

class student(person):
    def __init__(self, name, age, grade):
        super().__init__(name, age)
        self.grade = grade


ar1 = student('name', 'age', 'grade')
print(ar1.name)


    