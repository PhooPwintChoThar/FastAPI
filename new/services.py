from fastapi import FastAPI, Body, HTTPException, Header, Depends
from fastapi.security import OAuth2PasswordBearer
from random import randint
import bcrypt
from pydantic import BaseModel
from fastapi.responses import HTMLResponse
from fastapi import Header

from fastapi import Depends, HTTPException, Header
import ZODB, ZODB.FileStorage

import transaction

from z_enrollment import *

import BTrees._OOBTree

app=FastAPI()
oauth2_scheme=OAuth2PasswordBearer(tokenUrl='token')


def hash_password(pw: str):
    passw = pw.encode('utf-8')
    return bcrypt.hashpw(passw, bcrypt.gensalt())

def verify_password(plain, hashed):
    return bcrypt.checkpw(plain.encode('utf-8'), hashed)

def gen_token(id:str):
    tokenuser=root.token_user
    for token in tokenuser:
        if tokenuser[token]==id:
            return token
        
    token="%020x"% randint(0, 0xffffffffffffffff)
    while token in tokenuser:
        token="%020x"% randint(0, 0xffffffffffffffff)
    tokenuser[token]=id
    transaction.commit()
    return token


def verify_token(token:str):
    token=token.lower()
    tokenuser=root.token_user
    if token in tokenuser:
        return tokenuser[token]
    return None

async def get_current_user(authorization:str=Header(...)):
    if not authorization.startswith('token '):
        raise HTTPException(status_code=401, detail="invalid header")
    token=authorization[len("token "):].strip()
    id=verify_token(token)
    if not id:
        raise HTTPException(status_code=401, detail="invalid OR EXPIRED TOKEN")
    user_db=root.students
    if id not in user_db:
        raise HTTPException(status_code=401, detail="User not found")
    user_record=user_db[id]
    return user_record

@app.on_event("startup")
def strtup_event():
    global db, root
    storage=ZODB.FileStorage.FileStorage('mydata.fs')
    db=ZODB.DB(storage)
    connection=db.open()
    root=connection.root()

    
    if 'courses' not in root:
        root.courses=BTrees._OOBTree.BTree()
        
    if 'students' not in root:
        root.students=BTrees._OOBTree.BTree()
    
    if 'token_user' not in root:
        root.token_user=BTrees._OOBTree.BTree()

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



    student=Student(67011255, hash_password("thisIsAlice"), "Miss Alice")

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
    app.state.connection=connection



@app.on_event("shutdown")
def shutdown_event():
    global db
    connection=getattr(app.state, "connection", None)
    if connection:
        connection.close()
    db.close()

@app.get('/student/all')
def show_all_students():
    data= {}
    students=root.students
    for student in students:
        temp=students[student]
        data[student]=temp.getDetail()
    return data

@app.post("/student/new")
async def add_new_student(id:int=Body(), name:str=Body(), password:str=Body()):
    user_db=root.students
    if id in user_db:
        raise HTTPException(status_code=400, detail="Student already exists")
    user_db[id]=Student(id,hash_password(password), name)
    transaction.commit()
    temp=user_db[id].getDetail()
    temp.pop("password")
    return temp


@app.post("/student/login")
def login(id: int = Body(...), password: str = Body(...)):
    persondb=root.students
    if id not in persondb:
        raise HTTPException(status_code=400, detail="Invalid username or password1")
    user=persondb[id].getDetail()
    
    if not verify_password(password, user["password"]):
        raise HTTPException(status_code=400, detail="Invalid username or password")
    
    token=gen_token(user["id"])
    return {"access_token":token , "token_type":"token"}



@app.post("/student/enroll")
async def enroll_course(id:int=Body(), score:int=Body(),current_user: dict = Depends(get_current_user)):
    for enrolled_course in current_user.enrolls:
        if enrolled_course.course.id == id:
            raise HTTPException(status_code=400, detail="Course already enrolled")

    students=root.students
    student=students[current_user.id]
    courses=root.courses
    course=courses[id]
    if not course:
        raise HTTPException(status_code=400, detail="Course not exists")
    student.enrollCourse(course)
    enro=student.getEnrollment(course)
    enro.setScore(score)
    return {"detail": "Course enrolled successfully", "course":course.getDetail() }

@app.get("/student/enrollinfo")
async def show_enroll_info(current_user: dict = Depends(get_current_user)):
    ans=[]
    for e in current_user.enrolls:
        ans.append(e.getDetail())
    return  ans


@app.post("/student/logout")
def logout(current_user: dict = Depends(get_current_user)):
    id=current_user.id
    token_user=root.token_user
    for token in token_user:
        if token_user[token]==id:           

            del token_user[token]
            break
    return {"message": f"See you, {current_user.name}! You logged out."}



@app.get('/course')
def show_all_courses():
    result= {}
    courses=root.courses
    for course in courses:
        temp=courses[course]
        result[course]=temp.getDetail()
    return result

@app.get('/course/html', response_class=HTMLResponse)
def show_html():
    courses=root.courses
    content=""" <html><head></head><body><table>"""

    for course in courses:
        temp=courses[course]
        content+="""<tr><td>"""+str(course)+"""</td><td>"""+temp.name+"""</td><td>"""+str(temp.credit)+"""</td></tr>"""
    content+="""</table></body></html>"""
    return content


@app.post("/course/new")
async def add_new_course(id:int=Body(), name:str=Body(), credit:int=Body()):
    course_db=root.courses
    if id in course_db:
        raise HTTPException(status_code=400, detail="Course already exists")
    course_db[id]=Course(id, name, credit)
    transaction.commit()
    temp=course_db[id].getDetail()
    return temp

@app.get('/student/transcript/html', response_class=HTMLResponse)
def show_t(current_user: dict = Depends(get_current_user)):
    content=""" <html><head></head><body><p>ID : """+str(current_user.id)+"""</p><p>Name:"""+current_user.name+"""</p><table>"""

    for e in current_user.enrolls:
        content+="""<tr><td>"""+str(e.course.id)+"""</td><td>"""+str(e.course.name)+"""</td><td>"""+str(e.course.credit)+"""</td><td>"""+str(e.score)+"""</td><td>"""+str(e.getGrade())+"""</td></tr>"""
    content+="""</table><p>GPA:"""
    content+=str(current_user.getGPA())+ """</p></body></html>"""
    return content

@app.get('/student/transcript', response_class=HTMLResponse)
def show_t(current_user: dict = Depends(get_current_user)):
    students=root.students
    s=students[current_user.id]
    if s:
        return s.getT()
    
