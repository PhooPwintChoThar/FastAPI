z_enrollment.py

import persistent

class Course (persistent.Persistent):
    def __init__(self, id=0, name="", credit=0):
        self.id=id
        self.name=name
        self.gradeScheme=[
            {"Grade": "A", "min":80, "max":100},
            {"Grade": "B", "min":70, "max":79},
            {"Grade": "C", "min":60, "max":69},
            {"Grade": "D", "min":50, "max":59},
            {"Grade": "F", "min":0, "max":49},
        ]
        self.credit=credit

    
    def printDetails(self):
        print(f"ID:\t{self.id}  Course: {self.name:<35},Credit {self.credit}")
    
    def getCredit(self):
        return self.credit
    
    def setName(self, name):
        self.name=name
        
        
    def  scoreGrading(self, score):
        for grade in self.gradeScheme:
            if score>=grade["min"] and score<=grade["max"]:
                return grade["Grade"]
            
    def setGradeScheme(self, scheme):
        if not isinstance(scheme, list):
            return
        
        required_keys = {"Grade", "min", "max"}
        
        for item in scheme:
            if not isinstance(item, dict):
                return
            
            if set(item.keys()) != required_keys:
                return
            
            if not isinstance(item["Grade"], str):
                return
            if not isinstance(item["min"], int) or not isinstance(item["max"], int):
                return
            if item["min"] > item["max"]:
                return
        
        self.gradeScheme = scheme

        


class Student (persistent.Persistent):
    def __init__(self, id=0, name=""):
        self.id=id
        self.name=name
        self.enrolls=[]

    def enrollCourse(self, course):
        enrolled=Enrollment(course,  self)
        self.enrolls.append(enrolled)

    
    
    def getEnrollment(self, course):
        for e in self.enrolls:
            if e.getCourse() == course:
                return  e
        return None

    def printTranscript(self):
       
        t_credit=0
        t_gpa=0
        for e in self.enrolls:
            course=e.getCourse()
            credit=course.getCredit()
            print(f"\tID:\t{course.id:<8}Course:  {course.name:<35}Credit {course.getCredit()} Score:  {e.getScore()}  Grade:  {e.getGrade()}")
            t_credit+=credit
            grade=e.getGrade()
            if( grade == 'A') :
                t_gpa+=4*credit
            elif(grade == 'B+'):
                t_gpa+=3.5*credit
            elif(grade == 'B'):
                t_gpa+=3*credit
            elif(grade == 'C+'):
                t_gpa+=2.5*credit
            elif(grade == 'C'):
                t_gpa+=2*credit
            elif(grade == 'D+'):
                t_gpa+=1.5*credit
            elif(grade == 'D'):
                t_gpa+=1*credit


        gpa=t_gpa/t_credit
        print(f"Total GPA is: {gpa:.2f}")

    def setName(self, name):
        self.name=name
        
    

    

class Enrollment (persistent.Persistent):
    def __init__ (self, course=Course(),  student=Student() ):
        self.course=course
        self.score=0
        self.student=student

    def __str__(self):
        return f"{self.course.id}\t{self.course.name}\t{self.course.getCredit()}\t{self.grade}"

    def getCourse(self):
        return self.course
    
    def getScore(self):
        return self.score
    
    def setScore(self, score):
        self.score=score
    
    def getGrade(self):
        return self.course.scoreGrading(self.score)
 

    def printDetail(self):
        print(f"\n\n{self.student.name}'s Enrollment :")
        print(f"ID:\t{self.course.id}\tCourse:{self.course.name}\tCredit {self.course.getCredit()}\tGrade:{self.grade}")

            

insert_data.py

import ZODB, ZODB.FileStorage

import transaction

from z_enrollment import *

import BTrees._OOBTree


storage=ZODB.FileStorage.FileStorage('mydata.fs')
db=ZODB.DB(storage)
connection=db.open()
root=connection.root()

if 'courses' not in root:
    root.courses=BTrees._OOBTree.BTree()
    
if 'students' not in root:
    root.students=BTrees._OOBTree.BTree()
    
computer=Course(101 , "Computer Programming", 4)
web=Course(201, "Web Programming", 4)
software=Course(202, "Software Engineering Principle", 5)
ai=Course(301, "Artificial Intelligent", 3)
new_scheme1=[
            {"Grade": "A", "min":90, "max":100},
            {"Grade": "B", "min":70, "max":89},
            {"Grade": "C", "min":60, "max":69},
            {"Grade": "D", "min":50, "max":59},
            {"Grade": "F", "min":0, "max":49},
        ]

software.setGradeScheme(new_scheme1)


new_scheme2=[
            {"Grade": "A", "min":90, "max":100},
            {"Grade": "B", "min":70, "max":90},
            {"Grade": "C", "min":50, "max":69},
            {"Grade": "D", "min":40, "max":49},
            {"Grade": "F", "min":0, "max":39},
        ]

ai.setGradeScheme(new_scheme2)

root.courses[101]=computer
root.courses[201]=web
root.courses[202]=software
root.courses[301]=ai



student=Student(67011255, "Miss Alice")

student.enrollCourse(computer)
student.enrollCourse(web)
student.enrollCourse(software)
student.enrollCourse(ai)

c=student.getEnrollment(computer)
if c:
    c.setScore(75)
    
w=student.getEnrollment(web)
if w:
    w.setScore(81)
    
s=student.getEnrollment(software)
if s:
    s.setScore(81)
    
a=student.getEnrollment(ai)
if a:
    a.setScore(57)
    
root.students[67011255]=student

transaction.commit()

connection.close()



retrieve_data.py

import ZODB, ZODB.FileStorage
import persistent
import transaction


storage = ZODB.FileStorage.FileStorage('mydata.fs')
db = ZODB.DB(storage)
connection = db.open()
root = connection.root()


if __name__ == "__main__":
    # Print all courses
    courses = root.courses
    for course_id in courses:
        course = courses[course_id]
        course.printDetails()
        print()

    # Print all students' transcripts
    students = root.students
    
    for student_id in students:
        print("\tTranscript")
        student = students[student_id]
        print(f"ID:\t{student.id} Name: {student.name}")
        print("Course list")
        student.printTranscript()
        print()