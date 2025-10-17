from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

app=FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
template=Jinja2Templates(directory="template")

course_dict={
    101 : ["Computer Programming", 4, 75],
    201 : ["Web Programming", 4, 81],
    202 : ["SE Principle", 4, 81],
    301 : ["AI", 3, 57],
    404 : ["Hide and seek", 1, 0],
}

name_dict={
    1101 :"Mr. Tom Jerry",
    1102 :"Miss Marry May"
}

@app.get("/student")
def read_index(request:Request, id:int):
    if id not in name_dict:
        return {
            "Error":"Student id not found"
        }

    return template.TemplateResponse("page.html", {"request":request, "id":id, "name":name_dict[id], "courses":course_dict})
