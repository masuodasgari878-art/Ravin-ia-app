def coach_reply(message: str, user: dict, targets: dict, eaten: dict) -> str:
    q = message or ""
    left = int(targets.get("kcal", 0) - eaten.get("kcal", 0))
    if "شام" in q:
        return f"برای شام حدود {max(250, round(left * 0.35))} کالری بگذار. پیشنهاد: ماهی + سبزی."
    if "گرسن" in q:
        return "یک میان‌وعده پروتئینی مثل ماست یونانی یا چند عدد مغز انتخاب کن."
    if "ورزش" in q:
        return f"با فعالیت {user.get('activity')} کالری هدف {targets.get('kcal')} است. بعد تمرین پروتئین و کربوهیدرات را با هم بگیر."
    if "وزن" in q:
        return f"وزن فعلی {user.get('weight')} کیلو و هدف «{user.get('goal')}» است. روند را هفتگی بسنج."
    return (
        f"کالری باقی‌مانده امروز حدود {left} است. "
        f"پروتئین هدف {targets.get('p')} گرم. اگر منحرف شدی سهم شام را کم کن، کل روز را رها نکن."
    )
