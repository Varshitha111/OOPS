class Course:
    course_name=""
    price=0
    def __init__(self,course_name,price):
        self.course_name=course_name
        self.price=price
    def show_course(self):
        print(self.course_name,self.price)
class ProgrammingCourse(Course):
    language=""
    duration=""
    def __init__(self,course_name,price,language,duration):
        super().__init__(course_name,price)
        self.duration=duration
        self.language=language
    def show_programming_course(self):
        super().show_course()
        print(self.language,self.duration)
ob=ProgrammingCourse("python",20000,"english","1 month")
ob.show_programming_course()
ob1=ProgrammingCourse("java",30000,"telugu","2 months")
ob1.show_programming_course()