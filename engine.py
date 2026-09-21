FOODS = [
    {"id": "oats", "name": "جو دوسر با شیر", "kcal": 320, "p": 14, "c": 48, "f": 8, "meal": "صبحانه"},
    {"id": "egg", "name": "املت ۲ تخم‌مرغ", "kcal": 180, "p": 13, "c": 2, "f": 13, "meal": "صبحانه"},
    {"id": "yogurt", "name": "ماست یونانی", "kcal": 130, "p": 17, "c": 6, "f": 4, "meal": "میان‌وعده"},
    {"id": "chicken", "name": "سینه مرغ کبابی", "kcal": 280, "p": 42, "c": 0, "f": 8, "meal": "ناهار"},
    {"id": "rice", "name": "برنج قهوه‌ای", "kcal": 220, "p": 5, "c": 46, "f": 2, "meal": "ناهار"},
    {"id": "salad", "name": "سالاد سبزیجات", "kcal": 90, "p": 3, "c": 12, "f": 3, "meal": "ناهار"},
    {"id": "apple", "name": "سیب", "kcal": 80, "p": 0, "c": 21, "f": 0, "meal": "میان‌وعده"},
    {"id": "fish", "name": "ماهی سالمون", "kcal": 310, "p": 34, "c": 0, "f": 18, "meal": "شام"},
    {"id": "veg", "name": "سبزی بخارپز", "kcal": 70, "p": 3, "c": 12, "f": 1, "meal": "شام"},
    {"id": "nuts", "name": "مخلوط آجیل (۳۰گ)", "kcal": 180, "p": 6, "c": 6, "f": 16, "meal": "میان‌وعده"},
]


def search_foods(q: str = ""):
    q = (q or "").strip()
    if not q:
        return FOODS
    return [f for f in FOODS if q in f["name"]]
