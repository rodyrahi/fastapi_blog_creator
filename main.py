from fastapi import FastAPI, Request, Form, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

import os

from sqlalchemy.orm import Session
from database import SessionLocal, engine
from models import Base, Blog

Base.metadata.create_all(bind=engine)

app = FastAPI()

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

    blog = Blog(title=title, filename=filename)
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
    
    


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8011)
