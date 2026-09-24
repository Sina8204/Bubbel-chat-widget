import os , uuid
from PySide6.QtCore import QAbstractListModel, Qt
from PySide6.QtWidgets import QStyledItemDelegate
from PySide6.QtGui import QPainter, QColor, QFontMetrics , QTextCursor
from PySide6.QtCore import (QRect, Qt, QSize , QTimer , 
                            QObject, Signal , QEvent)
from PySide6.QtWidgets import (
    QListView, QWidget, QHBoxLayout , QVBoxLayout ,
    QGridLayout, QTextEdit , QLineEdit, QPushButton , 
    QSpacerItem , QSizePolicy
    )
from PySide6.QtGui import QMovie
from pathlib import Path

if __name__ == "__main__":
    from threading import Timer

USER_ME = 0
USER_THEM = 1
WAITING = 2

input_limit = 5

class Long_sender_widgets(QHBoxLayout):
    def __init__(self , input_event , btn_event , default_text = ''):
        super().__init__()

        # Create 'container' to controle the size
        self.container = QWidget()
        self.container.setSizePolicy(
            QSizePolicy.Policy.Expanding,  # Horizontal: expand
            QSizePolicy.Policy.Fixed       # Vertical: keep it steady
        )
        self.container.setMaximumHeight(200)  # Maximum total height of the 'container'
        self.container_layout = QHBoxLayout(self.container)
        self.container_layout.setContentsMargins(0, 0, 0, 0)

        self.btn_V_layout = QVBoxLayout()

        self.Long_input = QTextEdit(plainText = default_text)
        self.Long_input.setFocus()
        self.Long_input.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Expanding  # Expand inside the 'container'
        )
        
        self.Long_input.textChanged.connect(input_event)

        self.send_btn = QPushButton("Send")
        self.send_btn.clicked.connect(btn_event)
        
        self.verticalSpacer = QSpacerItem(18, 49, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.btn_V_layout.addItem(self.verticalSpacer)
        self.btn_V_layout.addWidget(self.send_btn)

        self.container_layout.addWidget(self.Long_input)
        self.container_layout.addLayout(self.btn_V_layout)
        
        # Adding a container to the main layout
        self.addWidget(self.container)

    def remove(self):
        self.Long_input.deleteLater()
        self.send_btn.deleteLater()
        self.container_layout.deleteLater()
        self.container.deleteLater()
        self.btn_V_layout.deleteLater()
        self.deleteLater()

class Small_sender_widgets(QHBoxLayout):
    def __init__(self , input_event , btn_event , default_text = ''):
        super().__init__()

        self.Small_input = QLineEdit(text=default_text)
        self.Small_input.textChanged.connect(input_event)

        self.btn_event = btn_event
        self.send_btn = QPushButton("Send")
        self.send_btn.clicked.connect(self.btn_event)

        self.addWidget(self.Small_input)
        self.addWidget(self.send_btn)

    def remove(self):
        self.Small_input.deleteLater()
        self.send_btn.deleteLater()
        self.deleteLater()

    def set_btn_event(self , event):
        self.btn_event = event
        self.send_btn.clicked.connect(self.btn_event)


class MessageModel(QAbstractListModel):
    def __init__(self):
        super().__init__()
        self.messages = []  # messages info : {"id": str, "who": int, "text": str}

    def data(self, index, role):
        if role == Qt.DisplayRole:
            msg = self.messages[index.row()]
            return (msg["who"], msg["text"], msg["id"])
        if role == Qt.UserRole + 1:  # For the 'delegate' to access the entire dictionary
            return self.messages[index.row()]

    def rowCount(self, index):
        return len(self.messages)

    def add_message(self, who, text):
        self.messages.append({"id": str(uuid.uuid4()), "who": who, "text": text})
        self.layoutChanged.emit()

    def update_message(self, msg_id, new_text):
        for i, msg in enumerate(self.messages):
            if msg["id"] == msg_id:
                msg["text"] = new_text
                idx = self.index(i, 0)
                self.dataChanged.emit(idx, idx, [Qt.DisplayRole])
                return True
        return False

    def get_message_by_id(self, msg_id):
        for msg in self.messages:
            if msg["id"] == msg_id:
                return msg
        return None

    def remove_last_waiting(self):
        for i in range(len(self.messages) - 1, -1, -1):
            if self.messages[i]["who"] == WAITING:
                del self.messages[i]
                self.layoutChanged.emit()
                return True
        return False

    def has_waiting(self):
        return any(m["who"] == WAITING for m in self.messages)


class BubbleDelegate(QStyledItemDelegate):
    MAX_WIDTH = 300
    PADDING = 12
    BUBBLE_MARGIN = 10
    ITEM_SPACING = 8
    WAITING_SIZE = 40

    def __init__(self, waiting_movie=None, parent=None):
        super().__init__(parent)
        self.waiting_movie = waiting_movie

    def _paint_waiting(self, painter, option, index):
        if self.waiting_movie is None:
            return
        x = option.rect.left() + self.BUBBLE_MARGIN
        y = option.rect.top() + self.PADDING
        target = QRect(x, y, self.WAITING_SIZE, self.WAITING_SIZE)
        pix = self.waiting_movie.currentPixmap()
        if not pix.isNull():
            painter.drawPixmap(target, pix)

    def _compute_text_rect(self, option, text):
        """Calculating the actual dimensions of text with wrap at max_width"""
        fm = QFontMetrics(option.font)
        rect = fm.boundingRect(
            QRect(0, 0, self.MAX_WIDTH, 10000),
            Qt.TextWordWrap | Qt.AlignLeft | Qt.AlignTop,
            text
        )
        return rect, fm

    def paint(self, painter, option, index):
        who, text, msg_id = index.data()

        # ==== waiting mode ====
        if who == WAITING:
            self._paint_waiting(painter, option, index)
            return

        painter.save()

        bubble_color = QColor("#b2e281") if who == USER_ME else QColor("white")

        text_rect, fm = self._compute_text_rect(option, text)
        text_width = text_rect.width()
        text_height = text_rect.height()

        final_width = text_width + self.PADDING * 2
        final_height = text_height + self.PADDING * 2

        bubble_rect = QRect(
            option.rect.x(),
            option.rect.y(),
            final_width,
            final_height
        )

        if who == USER_ME:
            bubble_rect.moveRight(option.rect.right() - self.BUBBLE_MARGIN)
        else:
            bubble_rect.moveLeft(option.rect.left() + self.BUBBLE_MARGIN)

        painter.setBrush(bubble_color)
        painter.setPen(Qt.NoPen)
        painter.drawRoundedRect(bubble_rect, 10, 10)

        painter.setPen(Qt.black)

        draw_rect = QRect(
            bubble_rect.x() + self.PADDING,
            bubble_rect.y() + self.PADDING,
            text_width,
            text_height
        )

        painter.drawText(
            draw_rect,
            Qt.TextWordWrap | Qt.AlignLeft | Qt.AlignTop,
            text
        )

        painter.restore()

    def sizeHint(self, option, index):
        who, text, msg_id = index.data()
        if who == WAITING:
            return QSize(self.WAITING_SIZE + self.PADDING * 2,
                         self.WAITING_SIZE + self.PADDING * 2 + self.ITEM_SPACING)

        text_rect, _ = self._compute_text_rect(option, text)
        final_width = text_rect.width() + self.PADDING * 2
        final_height = text_rect.height() + self.PADDING * 2 + self.ITEM_SPACING
        return QSize(final_width, final_height)

class ChatWindow(QWidget):
    def __init__(self , waiting_gif_relative_path = "assets/spinner.gif"):
        super().__init__()
        self.waiting_gif_relative_path = Path(waiting_gif_relative_path) 
        self.resize(400, 600)
        self.model = MessageModel()
        self.view = QListView()
        self.view.setModel(self.model)
        print(self.waiting_gif_path)
        self.waiting_movie = QMovie(self.waiting_gif_path)
        self.waiting_movie.setScaledSize(QSize(40, 40))

        self.view.setItemDelegate(BubbleDelegate(waiting_movie=self.waiting_movie))

        # ==== Soft scroll settings ====
        self.view.setVerticalScrollMode(QListView.ScrollMode.ScrollPerPixel)
        self.view.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.view.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.view.setUniformItemSizes(False)
        self.view.setResizeMode(QListView.ResizeMode.Adjust)
        self.view.setSpacing(0)
        self.view.setWordWrap(True)
        # ============================

        self._message_policy = self.send_message
        self.input_limit = 50

        self.sender_widgets = Small_sender_widgets(
            input_event=self.small_sender_widgets_event,
            btn_event=self.message_policy
        )

        self.V_layout = QVBoxLayout(self)
        self.V_layout.addWidget(self.view)
        self.V_layout.addLayout(self.sender_widgets)
        self.sender_widgets.Small_input.setFocus()

        self._waiting_timer = QTimer(self)
        self._waiting_timer.setInterval(50)
        self._waiting_timer.timeout.connect(self.view.viewport().update)

    @property
    def waiting_gif_path(self):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        gif_path = os.path.join(base_dir, self.waiting_gif_relative_path)
        return gif_path
    # =========================================================
    #            Edit message method
    # =========================================================
    def edit_message(self, msg_id, edited_text):
        """
        Changes the message with the ID 'msg_id' to edited_text.
        This method edits both 'USER_ME' and 'USER_THEM' messages.

        :param msg_id: The unique ID of the message (str)
        :param edited_text: The new message text (str)
        :return: 'True' if the edit was successful, otherwise 'False'
        """

        if not msg_id or edited_text is None:
            return False

        msg = self.model.get_message_by_id(msg_id)

        # Just edit chat message (USER_ME / USER_THEM) , not 'WAITING' message
        if msg is None or msg["who"] == WAITING:
            return False

        success = self.model.update_message(msg_id, edited_text)

        if success:
            # If the same message is open for editing in the 'input' , update it too
            if getattr(self, "_editing_msg_id", None) == msg_id:
                if type(self.sender_widgets) is Long_sender_widgets:
                    self.sender_widgets.Long_input.setPlainText(edited_text)
                else:
                    self.sender_widgets.Small_input.setText(edited_text)
            self.view.scrollToBottom()

        return success

    def check_overflow_on_resize(self, line_edit):
        font_metrics = QFontMetrics(line_edit.font())
        text_width = font_metrics.horizontalAdvance(line_edit.text())
        available_width = line_edit.width() - 10
        return text_width > available_width

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if type(self.sender_widgets) is Small_sender_widgets:
            if self.check_overflow_on_resize(self.sender_widgets.Small_input):
                self.small_sender_widgets_event()
        elif type(self.sender_widgets) is Long_sender_widgets:
            self.input_limit = self.get_chars_per_first_line(self.sender_widgets.Long_input)
            len_text_line = len(self.sender_widgets.Long_input.toPlainText())
            if len_text_line < self.input_limit:
                self.Long_sender_widgets_event()

    def small_sender_widgets_event(self):
        if type(self.sender_widgets) is Small_sender_widgets:
            len_text_line = len(self.sender_widgets.Small_input.text())
            if self.check_overflow_on_resize(self.sender_widgets.Small_input):
                text = self.sender_widgets.Small_input.text()
                self.V_layout.removeItem(self.sender_widgets)
                self.sender_widgets.remove()

                self.sender_widgets = Long_sender_widgets(
                    input_event=self.Long_sender_widgets_event,
                    btn_event=self.message_policy,
                    default_text=text
                )
                self.input_limit = self.get_chars_per_first_line(self.sender_widgets.Long_input)
                self.V_layout.addLayout(self.sender_widgets)
                QTimer.singleShot(10, self.set_focus)

    def Long_sender_widgets_event(self):
        if type(self.sender_widgets) is Long_sender_widgets:
            len_text_line = len(self.sender_widgets.Long_input.toPlainText())
            if len_text_line < self.input_limit:
                text = self.sender_widgets.Long_input.toPlainText()
                self.V_layout.removeItem(self.sender_widgets)
                self.sender_widgets.remove()

                self.sender_widgets = Small_sender_widgets(
                    input_event=self.small_sender_widgets_event,
                    btn_event=self.message_policy,
                    default_text=text
                )
                self.V_layout.addLayout(self.sender_widgets)
                QTimer.singleShot(10, self.set_focus)

    def set_focus(self):
        if type(self.sender_widgets) is Long_sender_widgets:
            self.sender_widgets.Long_input.setFocus()
            self.sender_widgets.Long_input.moveCursor(QTextCursor.End)
        elif type(self.sender_widgets) is Small_sender_widgets:
            self.sender_widgets.Small_input.setFocus()
            self.sender_widgets.Small_input.end(False)

    def send_message(self):
        text = ''
        if type(self.sender_widgets) is Long_sender_widgets:
            text = self.sender_widgets.Long_input.toPlainText()
        elif type(self.sender_widgets) is Small_sender_widgets:
            text = self.sender_widgets.Small_input.text()

        if text:
            self.model.add_message(USER_ME, text)
            if type(self.sender_widgets) is Long_sender_widgets:
                self.sender_widgets.Long_input.clear()
            elif type(self.sender_widgets) is Small_sender_widgets:
                self.sender_widgets.Small_input.clear()
            self.set_waiting(True)
            Timer(2, self.__receive_message).start()
            self.view.scrollToBottom()

    def __receive_message(self):
        self.set_waiting(False)
        self.model.add_message(USER_THEM, "Receive message (wait 3 seconds for editing)")
        Timer(3, self.__edit_receive_message).start()
    def __edit_receive_message(self):
        msg_id = self.model.messages[-1]["id"]
        self.edit_message(msg_id, "The received message has been edited")
        print(self.messages_info)
        print(self.__call__())

    @property
    def message_policy(self):
        return self._message_policy

    @message_policy.setter
    def message_policy(self , event):
        self._message_policy = event
        self.sender_widgets.send_btn.clicked.disconnect()
        self.sender_widgets.send_btn.clicked.connect(self._message_policy)

    def get_input_field(self):
        text = ''
        if type(self.sender_widgets) is Long_sender_widgets:
            text = self.sender_widgets.Long_input.toPlainText()
        elif type(self.sender_widgets) is Small_sender_widgets:
            text = self.sender_widgets.Small_input.text()
        return text

    def send(self, text, clear_mode=True, go_end=True):
        if text:
            self.model.add_message(USER_ME, text)
            if clear_mode:
                if type(self.sender_widgets) is Long_sender_widgets:
                    self.sender_widgets.Long_input.clear()
                elif type(self.sender_widgets) is Small_sender_widgets:
                    self.sender_widgets.Small_input.clear()
            if go_end:
                self.view.scrollToBottom()

    def receive(self, text, go_end=True):
        if text:
            self.model.add_message(USER_THEM, text)
            if go_end:
                self.view.scrollToBottom()

    def get_chars_per_first_line(self, text_edit):
        """
        Calculates the number of characters that 
        fit in the first line of a 'QTextEdit'
        """
        font_metrics = QFontMetrics(text_edit.font())
        margins = text_edit.contentsMargins()
        available_width = text_edit.width() - margins.left() - margins.right() - 10

        document = text_edit.document()
        first_block = document.firstBlock()
        first_line_text = first_block.text()

        char_count = 0
        for i, char in enumerate(first_line_text):
            text_until_i = first_line_text[:i + 1]
            text_width = font_metrics.horizontalAdvance(text_until_i)
            if text_width > available_width:
                break
            char_count = i + 1

        return char_count

    def set_waiting(self, state: bool):
        if state:
            if not self.model.has_waiting():
                if self.waiting_movie.state() != QMovie.MovieState.Running:
                    self.waiting_movie.start()
                self.model.add_message(WAITING, "")
                self.view.scrollToBottom()
                self._waiting_timer.start()
        else:
            if self.model.remove_last_waiting():
                self._waiting_timer.stop()
                self.waiting_movie.stop()
                self.view.scrollToBottom()

    @property
    def messages_info(self):
        return self.model.messages
    
    def __call__(self, *args, **kwds):
        return self.messages_info

    
if __name__ == "__main__":
    from PySide6.QtWidgets import QApplication
    app = QApplication([])

    window = ChatWindow()
    window.show()

    app.exec()