import persistent
import bcrypt
import ZODB, ZODB.FileStorage
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

    
    def getDetail(self):
       return {"id":self.id, "name":self.name,"credit" :self.credit, "gradeScheme":self.gradeScheme}
    
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
    def __init__(self, id=0, pw="", name=""):
        self.id=id
        self.name=name
        self.password=pw
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
    def getT(self):
        enrolls=[]
        for e in self.enrolls:
            enrolls.append(e.getDetail())
        return {"id":self.id, "name":self.name, "enroll":enrolls, "gpa":self.getGPA()}
    
    def getGPA(self):
        t_credit=0
        t_gpa=0
        for e in self.enrolls:
            course=e.getCourse()
            credit=course.getCredit()
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

        return f"{t_gpa/t_credit:.2f}"


    def setName(self, name):
        self.name=name

    def login(self, id, pw):
        if self.id==id and self.password==pw:
            return True
        return False
    
    def getDetail(self):
        enrolls=[]
        for e in self.enrolls:
            enrolls.append(e.getCourse().getDetail())
        return {"id":self.id, "name":self.name,"password":self.password, "enroll":enrolls}
    

    

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
 
    def getDetail(self):
       return {"id":self.course.id, "name":self.course.name,"credit" :self.course.getCredit(), "score":self.score, "grade":self.getGrade()}
    
    def printDetail(self):
        print(f"\n\n{self.student.name}'s Enrollment :")
        print(f"ID:\t{self.course.id}\tCourse:{self.course.name}\tCredit {self.course.getCredit()}\tGrade:{self.grade}")

class Token(persistent.Persistent):
    def __init__(self , tokem="", student=Student()) :
        self.token=tokem
        self.student=student
    

    def get_Token(self):
        return self.token
    
    def getStudent(self):
        return self.student



