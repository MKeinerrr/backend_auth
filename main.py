from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from database import init_db
from routes.auth import router as auth_router
from routes.billetera import router as billetera_router
from routes.catalogos import router as catalogos_router
from routes.salones import router as salones_router
from routes.admin_panel import router as admin_router

app = FastAPI()

BASE_DIR = Path(__file__).resolve().parent
UPLOADS_DIR = BASE_DIR / 'uploads'
UPLOADS_DIR.mkdir(parents=True, exist_ok=True)

app.add_middleware(
	CORSMiddleware,
	allow_origins=['*'],
	allow_credentials=True,
	allow_methods=['*'],
	allow_headers=['*'],
)


@app.on_event('startup')
def on_startup() -> None:
	init_db()


app.include_router(auth_router, prefix='/auth')
app.include_router(billetera_router, prefix='/billetera')
app.include_router(catalogos_router)
app.include_router(salones_router)
app.include_router(admin_router, prefix='/admin')

app.mount('/uploads', StaticFiles(directory=str(UPLOADS_DIR)), name='uploads')
