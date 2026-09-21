# RAVIN AI

اپ مربی تغذیه + بک‌اند Python (FastAPI).

## اجرا

```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

بعد در مرورگر:

- اپ: http://127.0.0.1:8000
- مستندات API: http://127.0.0.1:8000/docs

بدون سرور هم می‌توانی `app/index.html` را مستقیم باز کنی؛ در آن حالت داده‌ها محلی ذخیره می‌شود.

## ساختار

```
RAVIN-AI
├── app/index.html
├── backend/
│   ├── main.py
│   ├── nutrition_engine
│   ├── food_engine
│   ├── meal_engine
│   ├── portion_engine
│   ├── progress_engine
│   └── ai_orchestrator
├── database/store.json
└── docs
```

## API

- POST /api/auth/onboard
- GET /api/users/{id}
- GET /api/foods
- GET /api/plans/daily
- GET /api/plans/weekly
- POST /api/logs
- GET /api/progress
- POST /api/progress/weight
- POST /api/coach
