from fastapi import FastAPI, Body, HTTPException, Header, Depends
from fastapi.security import OAuth2PasswordBearer
from random import randint
import bcrypt
from pydantic import BaseModel
app=FastAPI()
oauth2_scheme=OAuth2PasswordBearer(tokenUrl='token')
tokenuser={}

class Course(BaseModel):
    id: str
    name: str
    grade: str

class Student(BaseModel):
    id: str
    name: str
    hashed_password: str
    enroll: list[Course]

def hash_password(pw: str):
    passw = pw.encode('utf-8')
    return bcrypt.hashpw(passw, bcrypt.gensalt())

persondb = {
    "1": {
        "id": "1",
        "name": "Alice",
        "hashed_password": hash_password("thisIsAlice"),
        "enroll": [
            {"id": "101", "name": "python", "grade": "B"},
            {"id": "102", "name": "rust", "grade": "A"}
        ]
    },
    "2": {
        "id": "2",
        "name": "Jame",
        "hashed_password": hash_password("thisIsJame"),
        "enroll": [
            {"id": 101, "name": "python", "grade": "B"},
        ]
    }
}

def verify_password(plain, hashed):
    return bcrypt.checkpw(plain.encode('utf-8'), hashed)

def gen_token(id:str):
    for token in tokenuser:
        if tokenuser[token]==id:
            return token
        
    token="%020x"% randint(0, 0xffffffffffffffff)
    while token in tokenuser:
        token="%020x"% randint(0, 0xffffffffffffffff)
    tokenuser[token]=id
    return token


def verify_token(token:str):
    token=token.lower()
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
    user_record=persondb.get(id)
    if not user_record:
        raise HTTPException(status_code=401, detail="User not found")
    return user_record


@app.get('/student/all')
def show_all_students():
    students_without_password = []
    for student in persondb.values():
        student_copy = student.copy()
        student_copy.pop("hashed_password", None)
        students_without_password.append(student_copy)
    return students_without_password

@app.post("/student/new")
async def add_new_student(s: Student):
    for student in persondb.values():
        if student["id"] == s.id:
            return {"detail": "Student already exists"}
    
    s.hashed_password = hash_password(s.hashed_password)
    persondb[s.id] = s.dict()
    
    return {"detail": "Student added successfully", "student": s.dict()}

@app.post("/student/login")
def login(id: str = Body(...), password: str = Body(...)):
    user = persondb.get(id)
    if not user:
        raise HTTPException(status_code=400, detail="Invalid username or password")

    if not verify_password(password, user["hashed_password"]):
        raise HTTPException(status_code=400, detail="Invalid username or password")
    
    return {"access_token":gen_token(id) , "token_type":"token"}

from fastapi import Header

from fastapi import Depends, HTTPException, Header

@app.post("/student/enroll")
async def enroll_course(course: Course, current_user: dict = Depends(get_current_user)):
    for enrolled_course in current_user["enroll"]:
        if enrolled_course["id"] == course.id:
            raise HTTPException(status_code=400, detail="Course already enrolled")

    current_user["enroll"].append(course.dict())  # Add the new course to the student's enrollment
    
    return {"detail": "Course enrolled successfully", "course": course.dict()}

@app.get("/student/enrollinfo")
async def show_enroll_info(current_user: dict = Depends(get_current_user)):

    return  current_user["enroll"]


@app.post("/student/logout")
def logout(current_user: dict = Depends(get_current_user)):
    id = current_user["id"]
  
    for token in tokenuser:
        if tokenuser[token] == id:
            del tokenuser[token]
            break
    return {"message": f"See you, {current_user['name']}! You logged out."}
