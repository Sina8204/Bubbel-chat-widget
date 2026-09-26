# Chat Bubble Widget

[English](Docs%20/English%20/README.md)

<p dir="rtl"> 
یک ویجت چت حبابی (Bubble Chat) سبک و قابل توسعه برای PySide6 که پیام‌های کاربر و مخاطب را به صورت حباب‌های چت نمایش می‌دهد، از حالت «در حال تایپ» (Waiting) با انیمیشن GIF پشتیبانی می‌کند و به صورت خودکار بین ورودی تک‌خطی و چندخطی جابه‌جا می‌شود.
</p>

---

## <p dir="rtl"> ✨ ویژگی‌ها </p>

<ul dir="rtl">
    <li> 🎨 نمایش حبابی پیام‌ها با رنگ‌بندی متفاوت برای کاربر (<code>USER_ME</code>) و مخاطب (<code>USER_THEM</code>).
    </li>
    <li>⏳ حالت انتظار (Waiting) با پشتیبانی از انیمیشن GIF (مثلاً اسپینر).
    </li>
    <li>🔄 جابه‌جایی خودکار ورودی بین <code>QLineEdit</code> (تک‌خطی) و <code>QTextEdit</code> (چندخطی) بر اساس طول متن.</li>
    <li>✏️ ویرایش پیام‌ها با استفاده از <code>msg_id</code> (شناسه یکتای هر پیام).</li>
    <li>📜 اسکرول نرم با <code>ScrollPerPixel</code>.</li>
    <li>🧩 معماری MVC با استفاده از <code>QAbstractListModel</code> و <code>QStyledItemDelegate</code>.</li>
    <li>🔌 قابلیت سفارشی‌سازی سیاست ارسال پیام از طریق <code>message_policy</code>.</li>
</ul>

---

## <p dir="rtl"> 📁 ساختار پروژه</p>

```
project/
├── main.py                    # فایل اصلی شامل کل کد
├── assets/
│   └── spinner.gif            # انیمیشن حالت انتظار
└── README.md
```

---

## <p dir="rtl"> 🚀 نصب و اجرا </p>

### <p dir="rtl"> پیش‌نیازها </p>

<ul dir="rtl">
    <li> Python 3.8 یا بالاتر</li>
    <li> PySide6 </li>
</ul>

<p dir="rtl"> نصب PySide6 : </p>

```bash
pip install PySide6
```

> **نکته:** پوشه `assets` و فایل `spinner.gif` باید در کنار فایل `Bubbel_chat_qtpy6.py` قرار داشته باشند. در غیر این صورت می‌توانید مسیر دلخواه را به سازنده `ChatWindow` پاس دهید.

---

## <p dir="rtl"> 📖 استفاده پایه </p>

```python
from PySide6.QtWidgets import QApplication
from main import ChatWindow

app = QApplication([])

window = ChatWindow(waiting_gif_relative_path="assets/spinner.gif")
window.show()

# ارسال پیام از سمت کاربر
window.send("سلام! این یک پیام تستی است.")

# دریافت پیام از سمت مخاطب
window.receive("سلام، خوش آمدید!")

# فعال/غیرفعال کردن حالت انتظار
window.set_waiting(True)
# ... بعد از دریافت پاسخ
window.set_waiting(False)

app.exec()
```

---

## <p dir="rtl"> 🧠 اجزای اصلی </p>

### 1. `MessageModel`
مدل داده‌ای که پیام‌ها را در یک لیست نگه می‌دارد. هر پیام یک دیکشنری با کلیدهای زیر است:

| کلید   | نوع   | توضیح                          |
|--------|-------|--------------------------------|
| `id`   | `str` | شناسه یکتا (UUID)              |
| `who`  | `int` | `USER_ME`، `USER_THEM` یا `WAITING` |
| `text` | `str` | متن پیام                       |

**متدهای کلیدی:**
- `add_message(who, text)`
- `update_message(msg_id, new_text)`
- `get_message_by_id(msg_id)`
- `remove_last_waiting()`
- `has_waiting()`

---

### 2. `BubbleDelegate`
مسئول رسم حباب‌ها است. پارامترهای ظاهری قابل تنظیم:

```python
MAX_WIDTH      = 300   # حداکثر عرض حباب
PADDING        = 12    # فاصله داخلی حباب
BUBBLE_MARGIN  = 10    # فاصله از لبه‌ها
ITEM_SPACING   = 8     # فاصله بین پیام‌ها
WAITING_SIZE   = 40    # اندازه انیمیشن انتظار
```

---

### 3. `Small_sender_widgets` و `Long_sender_widgets`
ویجت‌های ورودی:
- **Small**: `QLineEdit` + دکمه ارسال (برای متن کوتاه)
- **Long**: `QTextEdit` + دکمه ارسال (برای متن بلند)

جابه‌جایی بین این دو به صورت خودکار بر اساس `check_overflow_on_resize` انجام می‌شود.

---

### 4. `ChatWindow`
ویجت اصلی چت که همه اجزا را کنار هم قرار می‌دهد.

**متدهای عمومی مهم:**

| متد | توضیح |
|-----|-------|
| `send(text, clear_mode=True, go_end=True)` | ارسال پیام از سمت کاربر |
| `receive(text, go_end=True)` | دریافت پیام از سمت مخاطب |
| `edit_message(msg_id, edited_text)` | ویرایش پیام با شناسه مشخص |
| `set_waiting(state: bool)` | فعال/غیرفعال کردن حالت انتظار |
| `get_input_field()` | دریافت متن فعلی از فیلد ورودی |
| `messages_info` (property) | دسترسی به لیست کامل پیام‌ها |

---

## <p dir="rtl"> 🔧 سفارشی‌سازی </p>

### <p dir="rtl"> تغییر سیاست ارسال پیام </p>

<p dir="rtl"> می‌توانید رفتار دکمه ارسال را به دلخواه تغییر دهید : </p>


```python
def my_policy():
    text = window.get_input_field()
    if text:
        print(f"ارسال: {text}")
        window.send(text)

window.message_policy = my_policy
```

### <p dir="rtl"> تغییر رنگ حباب‌ها </p>

در `BubbleDelegate.paint`:

```python
bubble_color = QColor("#b2e281") if who == USER_ME else QColor("white")
```

### <p dir="rtl"> تغییر مسیر GIF </p>

```python
window = ChatWindow(waiting_gif_relative_path="path/to/your/spinner.gif")
```

---

## <p dir="rtl"> ⚠️ نکات مهم </p>

<p dir="rtl">
1. <code>Thread Safety</code>: در متد <code>send_message</code> از <code>threading.Timer</code> برای شبیه‌سازی پاسخ استفاده شده است. در پروژه واقعی، حتماً از <code>QTimer</code> یا <code>Signal/Slot</code> استفاده کنید، چون تغییرات UI از ترد دیگر می‌تواند باعث کرش شود.</br>
2. <code>GIF</code>: مطمئن شوید فایل GIF در مسیر مشخص‌شده وجود دارد، در غیر این صورت <code>QMovie</code> به درستی کار نخواهد کرد.</br>
3. ویرایش پیام: ویرایش فقط روی پیام‌های <code>USER_ME</code> و <code>USER_THEM</code> امکان‌پذیر است، نه پیام‌های <code>WAITING</code>.
</p>
---

## <p dir="rtl"> 🐛 عیب‌یابی </p>

| مشکل | راه‌حل |
|------|-------|
| <p dir="rtl"> GIF نمایش داده نمی‌شود </p> | <p dir="rtl"> مسیر `waiting_gif_relative_path` را بررسی کنید </p> |
| <p dir="rtl"> حباب‌ها با هم تداخل دارند </p> | <p dir="rtl"> مقادیر `PADDING` و `ITEM_SPACING` را تنظیم کنید </p> |
|<p dir="rtl"> ورودی جابه‌جا نمی‌شود </p> | <p dir="rtl"> `check_overflow_on_resize` را بررسی کنید </p> |

---

## <p dir="rtl"> 📄 لایسنس </p>

<p dir="rtl">
این پروژه آزاد است و می‌توانید آن را در پروژه‌های شخصی و تجاری خود استفاده کنید.
</p>
