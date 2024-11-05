import os.path
import json

import config_env #do not remove it it loads env file
from fastapi import FastAPI, Request
from starlette.middleware.cors import CORSMiddleware
from Models.Users import Users

from Database import init_db_schema, get_db
from routers import auth, home
from dotenv import load_dotenv

print(os.getenv('ALLOWED_ORIGINS'))
origins = json.loads(os.getenv('ALLOWED_ORIGINS'))
app = FastAPI()

app.include_router(auth.router, prefix="/auth", tags=['Auth'])
app.include_router(home.router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

last_env_edit_time = 0

def add (num1, mum2):
    return num1+mum2


def reload_env_if_needed():
    try:
        global last_env_edit_time
        current_env_edit_time = os.path.getatime('.env')
        if current_env_edit_time != last_env_edit_time:
            load_dotenv(override=True)
            last_env_edit_time = current_env_edit_time
            print('.env file reloaded')
    except FileNotFoundError:
        print('.env file does not exists')


@app.middleware('http')
async def reload_env(request: Request, call_next):
    reload_env_if_needed()
    response = await call_next(request)
    return response


init_db_schema()

# if __name__ == "__main__":
#     uvicorn.run(app, host="0.0.0.0", port=8000)


