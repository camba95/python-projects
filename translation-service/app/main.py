from fastapi import FastAPI, BackgroundTasks, HTTPException, Request, Depends
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.templating import Jinja2Templates
import schemas
import crud
import models
from database import get_db, engine
from sqlalchemy.orm import Session
from utils import perform_translation

models.Base.metadata.create_all(bind=engine)
app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

# Setup for jinja2 templates
templates = Jinja2Templates(directory='templates')

@app.get('/index', response_class=HTMLResponse)
def index(request: Request):
  return templates.TemplateResponse('index.html', {'request': request})

@app.get('/translate/{task_id}', response_model=schemas.TranslationStatus)
def translate(task_id: int, request: Request, db: Session = Depends(get_db)):
    task = crud.get_translation_task(db, task_id)

    if not task:
      raise HTTPException(status_code=404, detail='Task not found')

    print('main', task.translations)
    return templates.TemplateResponse('results.html', {'request': request, 'translations': task.translations})

@app.post('/translate', response_model=schemas.TaskResponse)
def translate(request: schemas.TranslationRequest, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    task = crud.create_translation_task(db, request.text, request.languages)
    background_tasks.add_task(perform_translation, task.id, request.text, request.languages, db)

    return { 'task_id': task.id, 'status': task.status == 'completed' }
