from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import Optional
from pathlib import Path
import json
import uuid
from datetime import date

from nutrition_engine.engine import calc_bmr, calc_tdee, calc_macros
from food_engine.engine import FOODS, search_foods
from meal_engine.engine import build_daily_plan
from portion_engine.engine import scale_item
from progress_engine.engine import adherence
from ai_orchestrator.engine import coach_reply

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "database" / "store.json"
APP_DIR = ROOT / "app"

app = FastAPI(title="RAVIN AI", version="1.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


def load_db():
    if DATA.exists():
        return json.loads(DATA.read_text(encoding="utf-8"))
    return {"users": {}, "logs": {}, "weights": {}, "chats": {}}


def save_db(db):
    DATA.parent.mkdir(parents=True, exist_ok=True)
    DATA.write_text(json.dumps(db, ensure_ascii=False, indent=2), encoding="utf-8")


class OnboardIn(BaseModel):
    name: str
    age: int
    sex: str
    height: float
    weight: float
    activity: str
    goal: str


class LogIn(BaseModel):
    user_id: str
    food_id: Optional[str] = None
    name: Optional[str] = None
    kcal: Optional[int] = None
    p: Optional[float] = None
    c: Optional[float] = None
    f: Optional[float] = None
    portion: float = 1.0


class WeightIn(BaseModel):
    user_id: str
    kg: float


class ChatIn(BaseModel):
    user_id: str
    message: str


@app.get("/api/health")
def health():
    return {"ok": True, "name": "RAVIN AI"}


@app.post("/api/auth/onboard")
def onboard(body: OnboardIn):
    db = load_db()
    uid = str(uuid.uuid4())[:8]
    user = body.model_dump()
    user["id"] = uid
    db["users"][uid] = user
    db["logs"][uid] = []
    db["weights"][uid] = [{"date": str(date.today()), "kg": body.weight}]
    db["chats"][uid] = [
        {
            "from": "bot",
            "text": f"سلام {body.name}! هدف تو «{body.goal}» است. برنامه را ساختم.",
        }
    ]
    save_db(db)
    return {"user": user, "targets": _targets(user)}


@app.get("/api/users/{user_id}")
def get_user(user_id: str):
    db = load_db()
    user = db["users"].get(user_id)
    if not user:
        raise HTTPException(404, "user not found")
    return {"user": user, "targets": _targets(user)}


@app.get("/api/foods")
def foods(q: str = ""):
    return {"foods": search_foods(q)}


@app.get("/api/plans/daily")
def daily(user_id: str):
    db = load_db()
    user = db["users"].get(user_id)
    if not user:
        raise HTTPException(404, "user not found")
    targets = _targets(user)
    return {"plan": build_daily_plan(targets), "targets": targets}


@app.get("/api/plans/weekly")
def weekly(user_id: str):
    db = load_db()
    user = db["users"].get(user_id)
    if not user:
        raise HTTPException(404, "user not found")
    t = _targets(user)
    return {
        "focus": [
            "پروتئین در هر وعده حداقل ۲۵ گرم",
            "۸ لیوان آب",
            "شام سبک‌تر، ۳ ساعت قبل خواب",
        ],
        "pattern": "۳ روز پروتئین بالا، ۲ روز متعادل، ۲ روز ریکاوری کربوهیدرات",
        "targets": t,
    }


@app.post("/api/logs")
def add_log(body: LogIn):
    db = load_db()
    if body.user_id not in db["users"]:
        raise HTTPException(404, "user not found")
    item = None
    if body.food_id:
        item = next((f for f in FOODS if f["id"] == body.food_id), None)
    if not item:
        item = {
            "id": "custom",
            "name": body.name or "غذا",
            "kcal": body.kcal or 0,
            "p": body.p or 0,
            "c": body.c or 0,
            "f": body.f or 0,
            "meal": "سفارشی",
        }
    item = scale_item(item, body.portion)
    item["date"] = str(date.today())
    db["logs"][body.user_id].append(item)
    save_db(db)
    return {"ok": True, "item": item, "summary": _eaten(db, body.user_id)}


@app.get("/api/logs")
def list_logs(user_id: str):
    db = load_db()
    today = str(date.today())
    logs = [x for x in db["logs"].get(user_id, []) if x.get("date") == today]
    return {"logs": logs, "summary": _eaten(db, user_id)}


@app.post("/api/progress/weight")
def add_weight(body: WeightIn):
    db = load_db()
    if body.user_id not in db["users"]:
        raise HTTPException(404, "user not found")
    db["weights"][body.user_id].append({"date": str(date.today()), "kg": body.kg})
    db["users"][body.user_id]["weight"] = body.kg
    save_db(db)
    return {"weights": db["weights"][body.user_id]}


@app.get("/api/progress")
def progress(user_id: str):
    db = load_db()
    user = db["users"].get(user_id)
    if not user:
        raise HTTPException(404, "user not found")
    logs = [x for x in db["logs"].get(user_id, []) if x.get("date") == str(date.today())]
    return {
        "weights": db["weights"].get(user_id, []),
        "adherence": adherence(logs, _targets(user)),
        "today_count": len(logs),
    }


@app.post("/api/coach")
def coach(body: ChatIn):
    db = load_db()
    user = db["users"].get(body.user_id)
    if not user:
        raise HTTPException(404, "user not found")
    eaten = _eaten(db, body.user_id)
    targets = _targets(user)
    reply = coach_reply(body.message, user, targets, eaten)
    db["chats"][body.user_id].append({"from": "me", "text": body.message})
    db["chats"][body.user_id].append({"from": "bot", "text": reply})
    save_db(db)
    return {"reply": reply, "chat": db["chats"][body.user_id]}


@app.get("/api/coach")
def get_chat(user_id: str):
    db = load_db()
    return {"chat": db["chats"].get(user_id, [])}


def _targets(user):
    tdee = calc_tdee(user)
    return {"bmr": calc_bmr(user), "tdee": tdee, **calc_macros(tdee)}


def _eaten(db, user_id):
    today = str(date.today())
    logs = [x for x in db["logs"].get(user_id, []) if x.get("date") == today]
    out = {"kcal": 0, "p": 0, "c": 0, "f": 0}
    for x in logs:
        out["kcal"] += x.get("kcal", 0)
        out["p"] += x.get("p", 0)
        out["c"] += x.get("c", 0)
        out["f"] += x.get("f", 0)
    return out


if APP_DIR.exists():
    app.mount("/", StaticFiles(directory=str(APP_DIR), html=True), name="app")
