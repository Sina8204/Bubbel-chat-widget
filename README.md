# Chat Bubble Widget

[English](Docs/English/README.md) _ [فارسی](Docs\Persian\README.md)

A lightweight and extensible Bubble Chat widget for PySide6 that displays user and contact messages as chat bubbles, supports a "typing" (Waiting) state with GIF animation, and automatically switches between single-line and multi-line input.

---

## ✨ Features

- 🎨 Bubble display of messages with different colors for the user (`USER_ME`) and the contact (`USER_THEM`).
- ⏳ Waiting state with GIF animation support (e.g., a spinner).
- 🔄 Automatic switching of the input between `QLineEdit` (single-line) and `QTextEdit` (multi-line) based on text length.
- ✏️ Editing messages using `msg_id` (a unique identifier for each message).
- 📜 Smooth scrolling with `ScrollPerPixel`.
- 🧩 MVC architecture using `QAbstractListModel` and `QStyledItemDelegate`.
- 🔌 Ability to customize the message-sending policy via `message_policy`.

---

## 📁 Project Structure

```
project/
├── main.py                    # Main file containing all the code
├── assets/
│   └── spinner.gif            # Waiting state animation
└── README.md
```

---

## 🚀 Installation and Running

### Prerequisites

- Python 3.8 or higher
- PySide6

Installing PySide6:

```bash
pip install PySide6
```

> **Note:** The `assets` folder and the `spinner.gif` file must be located next to the `Bubbel_chat_qtpy6.py` file. Otherwise, you can pass a custom path to the `ChatWindow` constructor.

---

## 📖 Basic Usage

```python
from PySide6.QtWidgets import QApplication
from main import ChatWindow

app = QApplication([])

window = ChatWindow(waiting_gif_relative_path="assets/spinner.gif")
window.show()

# Send a message from the user's side
window.send("Hello! This is a test message.")

# Receive a message from the contact's side
window.receive("Hello, welcome!")

# Enable/disable the waiting state
window.set_waiting(True)
# ... after receiving the response
window.set_waiting(False)

app.exec()
```

---

## 🧠 Main Components

### 1. `MessageModel`
The data model that keeps messages in a list. Each message is a dictionary with the following keys:

| Key    | Type  | Description                          |
|--------|-------|--------------------------------------|
| `id`   | `str` | Unique identifier (UUID)             |
| `who`  | `int` | `USER_ME`, `USER_THEM`, or `WAITING` |
| `text` | `str` | Message text                         |

**Key methods:**
- `add_message(who, text)`
- `update_message(msg_id, new_text)`
- `get_message_by_id(msg_id)`
- `remove_last_waiting()`
- `has_waiting()`

---

### 2. `BubbleDelegate`
Responsible for drawing the bubbles. Customizable appearance parameters:

```python
MAX_WIDTH      = 300   # Maximum bubble width
PADDING        = 12    # Internal bubble padding
BUBBLE_MARGIN  = 10    # Margin from the edges
ITEM_SPACING   = 8     # Spacing between messages
WAITING_SIZE   = 40    # Size of the waiting animation
```

---

### 3. `Small_sender_widgets` and `Long_sender_widgets`
Input widgets:
- **Small**: `QLineEdit` + send button (for short text)
- **Long**: `QTextEdit` + send button (for long text)

Switching between these two is done automatically based on `check_overflow_on_resize`.

---

### 4. `ChatWindow`
The main chat widget that brings all the components together.

**Important public methods:**

| Method | Description |
|--------|-------------|
| `send(text, clear_mode=True, go_end=True)` | Send a message from the user's side |
| `receive(text, go_end=True)` | Receive a message from the contact's side |
| `edit_message(msg_id, edited_text)` | Edit a message by its identifier |
| `set_waiting(state: bool)` | Enable/disable the waiting state |
| `get_input_field()` | Get the current text from the input field |
| `messages_info` (property) | Access the full list of messages |

---

## 🔧 Customization

### Changing the Message-Sending Policy

You can change the behavior of the send button as you wish:

```python
def my_policy():
    text = window.get_input_field()
    if text:
        print(f"Sending: {text}")
        window.send(text)

window.message_policy = my_policy
```

### Changing Bubble Colors

In `BubbleDelegate.paint`:

```python
bubble_color = QColor("#b2e281") if who == USER_ME else QColor("white")
```

### Changing the GIF Path

```python
window = ChatWindow(waiting_gif_relative_path="path/to/your/spinner.gif")
```

---

## ⚠️ Important Notes

1. `Thread Safety`: In the `send_message` method, `threading.Timer` is used to simulate a response. In a real project, be sure to use `QTimer` or `Signal/Slot`, because modifying the UI from another thread can cause a crash.
2. `GIF`: Make sure the GIF file exists at the specified path, otherwise `QMovie` will not work properly.
3. Message editing: Editing is only possible for `USER_ME` and `USER_THEM` messages, not `WAITING` messages.

---

## 🐛 Troubleshooting

| Problem | Solution |
|---------|----------|
| GIF is not displayed | Check the `waiting_gif_relative_path` |
| Bubbles overlap each other | Adjust the `PADDING` and `ITEM_SPACING` values |
| Input does not switch | Check `check_overflow_on_resize` |

---

## 📄 License

This project is free and you can use it in your personal and commercial projects.
