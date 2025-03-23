from fastapi import FastAPI, Depends, HTTPException, Request, Form
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
import os
import sqlite3

app = FastAPI()
templates = Jinja2Templates(directory="templates")

# Secret key for session (Flask equivalent)
SECRET_KEY = "Put some random key which is used to sign the session cookies"

# Simulated session (FastAPI doesn't use session like Flask)
session = {}

#  Middleware (Decorator Equivalent)
def auth_required(func):
    async def wrapper(*args, **kwargs):
        if "username" not in session:
            return RedirectResponse(url="/login", status_code=303)
        return await func(*args, **kwargs)
    return wrapper


#  Database Dependency (SQLite)
def get_db():
    conn = sqlite3.connect("people.db")
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()


# Check Password Function
def check_password(username: str, password: str) -> bool:
    return username == "ganesh" and password == "hero"


#  Logout
@app.get("/logout")
async def logout():
    session.pop("username", None)
    return "Logged out"


#  Login
@app.get("/login", response_class=HTMLResponse)
async def login_form():
    return """
    <html>
    <head><title>Login</title></head>    
    <body>
    <form action="/login" method="post">
        Username:<input type="text" name="username" required/>
        <br/>
        Password:<input type="password" name="password" required/>
        <br/>
        <input type="submit" value="Submit" />
    </form>
    </body>
    </html>        
    """

@app.post("/login")
async def login(username: str = Form(...), password: str = Form(...)):
    if check_password(username, password):
        session["username"] = username
        return "Login success"
    return RedirectResponse(url="/login", status_code=303)


#  Protected Route
@app.get("/", dependencies=[Depends(auth_required)], response_class=HTMLResponse)
async def home():
    return """
    <html>
    <head><title>My Webserver</title>
    <style>
    .some { color: red; }
    </style>
    <body>
    <h1 class="some">Hello there</h1>
    <h1 class="some">Hello again</h1>
    </body>
    </html>
    """


#  Favicon Handling
@app.get("/favicon.ico")
async def favicon():
    return RedirectResponse(url="/static/favicon.ico")


#  Environment Variables Display
@app.get("/env", response_class=HTMLResponse)
async def env_form():
    return """
    <html>
    <head><title>Give Env</title></head>    
    <body>
    <form action="/env" method="post">
        Env Var:<input type="text" name="envp" value="ALL" />
        <br/>
        Color:<input type="text" name="color" value="black" />
        <br/>
        <input type="submit" value="Submit" />
    </form>
    </body>
    </html>        
    """

@app.post("/env")
async def env(envp: str = Form("ALL"), color: str = Form("black")):
    env_dict = os.environ

    if envp.upper() != "ALL":
        env_dict = {k: os.environ.get(k.upper()) for k in envp.split(";") if os.environ.get(k.upper())}

    return templates.TemplateResponse("env.html", {"request": {}, "envs": env_dict, "color": color})


#  Request Model for API
class NameFormat(BaseModel):
    name: str = "ABC"
    format: str = "json"


#  Get Age from Database
def get_age(db, name: str):
    cursor = db.cursor()
    cursor.execute("SELECT age FROM people WHERE name = ?", (name,))
    row = cursor.fetchone()
    return row[0] if row else None


#  API Route for Fetching Name & Age
@app.get("/helloj/{name}/{format}")
@app.get("/helloj/{name}")
@app.get("/helloj")
async def helloj(name: str = "ABC", format: str = "json", db=Depends(get_db)):
    age = get_age(db, name.lower())

    if format == "json":
        if age is not None:
            return JSONResponse(content={"name": name, "age": age}, status_code=200)
        return JSONResponse(content={"name": name, "details": "Not found"}, status_code=404)

    elif format == "xml":
        xml_response = f"""<?xml version="1.0"?>
                        <data><name>{name}</name><age>{age}</age></data>"""
        return Response(content=xml_response, media_type="application/xml")

    return "Format not recognized"


#  Post Request Handling JSON/XML
@app.post("/helloj")
async def helloj_post(request: Request, db=Depends(get_db)):
    content_type = request.headers.get("Content-Type", "")

    if content_type == "application/json":
        body = await request.json()
        name = body.get("name", "ABC")
        format = body.get("format", "json")
    elif content_type == "application/xml":
        body = await request.body()
        root = ET.fromstring(body)
        name_element = root.find("name")
        name = name_element.text if name_element is not None else "ABC"
        format = "xml"
    else:
        raise HTTPException(status_code=400, detail="Content type not recognized")

    return await helloj(name, format, db)


# Run FastAPI App
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=5000)
