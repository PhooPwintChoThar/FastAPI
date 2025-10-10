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


