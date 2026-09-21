# Architecture

لایه‌ها از بیرون به داخل:

1. mobile-app (UI)
2. backend/ai-orchestrator + authentication
3. domain engines (nutrition, food, meal, portion, progress)
4. database

اصل طراحی: موتورهای دامنه جدا از ارکستراسیون AI هستند تا قوانین تغذیه قابل تست و قابل نسخه‌گذاری بمانند.
