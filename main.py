from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from db.database import db
from routers.tokens import router as tokens
from routers.proposes import router as proposes
from routers.users import router as users

app = FastAPI(title="Order manager")


async def on_startup():
    app.state.pool = await db.start()
app.add_event_handler("startup", on_startup)

origins = [
    "http://localhost:3000"
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)
app.include_router(
    router=proposes,
    prefix="/proposes",
    tags=["Propose"]
)
app.include_router(
    router=users,
    prefix="/user",
    tags=["User"]
)
app.include_router(
    router=tokens,
    prefix="/token",
    tags=["Token"]
)
