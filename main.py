from fastapi import FastAPI, Request, Form, Depends, Response
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.status import HTTP_401_UNAUTHORIZED
import base64
import os

from sqlalchemy.orm import Session
from database import SessionLocal, engine
from models import Base, Blog

Base.metadata.create_all(bind=engine)

app = FastAPI()


USERNAME = "raj@69"
PASSWORD = "kamingo@69"


@app.middleware("http")
async def basic_auth_middleware(request: Request, call_next):
    # Skip auth for docs or root if you want
    if request.url.path in ["/docs", "/openapi.json"]:
        return await call_next(request)

    auth = request.headers.get("Authorization")
    if auth:
        try:
            scheme, credentials = auth.split()
            if scheme.lower() == "basic":
                decoded = base64.b64decode(credentials).decode("utf-8")
                username, password = decoded.split(":")
                if username == USERNAME and password == PASSWORD:
                    return await call_next(request)
        except Exception:
            pass

    return Response(
        content="Unauthorized",
        status_code=HTTP_401_UNAUTHORIZED,
        headers={"WWW-Authenticate": "Basic"},
    )


app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

os.makedirs("blogs", exist_ok=True)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/", response_class=HTMLResponse)
def index(request: Request, db: Session = Depends(get_db)):
    blogs = db.query(Blog).all()
    return templates.TemplateResponse("index.html", {"request": request, "blogs": blogs})


@app.get("/create", response_class=HTMLResponse)
def create_get(request: Request):
    return templates.TemplateResponse("create.html", {"request": request})


@app.post("/create")
def create_post(
    title: str = Form(...),
    content: str = Form(...),
    db: Session = Depends(get_db)
):
    filename = title.replace(" ", "_").lower() + ".md"
    filepath = os.path.join("blogs", filename)

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)

    blog = Blog(title=title.lower(), filename=filename)
    db.add(blog)
    db.commit()
    return RedirectResponse(url="/", status_code=303)


@app.get("/view/{blog_id}", response_class=HTMLResponse)
def view_blog(blog_id: int, request: Request, db: Session = Depends(get_db)):
    blog = db.query(Blog).filter(Blog.id == blog_id).first()
    if not blog:
        return HTMLResponse(content="Blog not found", status_code=404)

    filepath = os.path.join("blogs", blog.filename)
    if not os.path.exists(filepath):
        return HTMLResponse(content="File not found", status_code=404)

    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()
        
   
    return templates.TemplateResponse(
        "view.html", {"request": request, "blog": blog, "content": content}
    )
    
    



