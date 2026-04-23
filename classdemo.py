#TASK1

class Student:
    school_name="xyz high school"
    def set_details(self):

        name="vamsi"
        marks=85
        self.name=name
        self.marks=marks
        
    def display(self):
        print(self.name,self.marks,Student.school_name)
obj=Student()
obj.set_details()
obj.display()
print(obj.name)
# TASK2
class Employee:
    company = "Infosys"
    def set_data(self):
        name = "Ravi"
        self.salary=salary = 20000
        self.salary=salary
        self.name=name
    def increase_salary(self):
        self.salary1=self.salary+5000
    def display(self):
        print(self.name,self.salary1,Employee.company)
o1=Employee()
o1.set_data()
o1.increase_salary()
o1.display()
# TASK3
class Mobile:
    brand = "Apple"
    def set_details(self):
        model = "iPhone 14"
        price = 80000
        self.model=model
        self.price=price
    def discount(self):
        self.price=self.price-self.price*(10/100)
    def show_details(self):
        print(Mobile.brand,self.model,self.price)
o2=Mobile()
o2.set_details()
o2.discount()
o2.show_details()