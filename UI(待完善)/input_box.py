import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QTextEdit, QListWidget, QVBoxLayout,
    QListWidgetItem, QShortcut, QMessageBox, QHBoxLayout, QFrame
)
from PyQt5.QtCore import Qt, QEvent
from PyQt5 import QtGui
import re

class ProtectedTextEdit(QTextEdit):
    def __init__(self):
        super().__init__()
        self.protected_ranges = []

    def insert_protected_text(self, text, fmt):
        cursor = self.textCursor()
        start = cursor.position()
        cursor.insertText(text, fmt)
        end = cursor.position()
        self.protected_ranges.append((start, end))

    def keyPressEvent(self, event):
        cursor = self.textCursor()
        pos = cursor.position()
        selected_text = cursor.selectedText()
        selection_start = cursor.selectionStart()
        selection_end = cursor.selectionEnd()

        # 检查光标或选择范围是否在受保护的范围内
        in_protected_range = False
        for start, end in self.protected_ranges:
            if (start <= pos <= end) or (selection_start < end and selection_end > start):
                in_protected_range = True
                break

        # 如果在受保护的范围内，阻止任何文本修改
        if in_protected_range:
            if event.key() in (Qt.Key_Left, Qt.Key_Right, Qt.Key_Up, Qt.Key_Down,
                               Qt.Key_Home, Qt.Key_End, Qt.Key_PageUp, Qt.Key_PageDown):
                super().keyPressEvent(event)  # 允许光标移动
            else:
                return  # 阻止其他按键事件
        else:
            super().keyPressEvent(event)
            self.update_protected_ranges()

    def insertFromMimeData(self, source):
        # 阻止粘贴到受保护的范围内
        cursor = self.textCursor()
        pos = cursor.position()
        selection_start = cursor.selectionStart()
        selection_end = cursor.selectionEnd()

        in_protected_range = False
        for start, end in self.protected_ranges:
            if (start <= pos <= end) or (selection_start < end and selection_end > start):
                in_protected_range = True
                break

        if in_protected_range:
            return  # 阻止粘贴
        else:
            super().insertFromMimeData(source)
            self.update_protected_ranges()

    def update_protected_ranges(self):
        # 更新受保护的范围
        self.protected_ranges = []
        text = self.toPlainText()
        pattern = r'\[.*?\]'
        for match in re.finditer(pattern, text):
            start = match.start()
            end = match.end()
            self.protected_ranges.append((start, end))

    def mousePressEvent(self, event):
        super().mousePressEvent(event)
        self.ensure_cursor_not_in_protected_area()

    def mouseReleaseEvent(self, event):
        super().mouseReleaseEvent(event)
        self.ensure_cursor_not_in_protected_area()

    def ensure_cursor_not_in_protected_area(self):
        cursor = self.textCursor()
        pos = cursor.position()
        for start, end in self.protected_ranges:
            if start <= pos <= end:
                if pos > end:
                    cursor.setPosition(end)
                else:
                    cursor.setPosition(start)
                self.setTextCursor(cursor)
                break

    def contextMenuEvent(self, event):
        # 禁用右键菜单，防止用户进行剪切、粘贴等操作
        pass

class InputAreaWidget(QWidget):
    def __init__(self):
        super().__init__()
        # 设置样式背景属性
        self.setAttribute(Qt.WA_StyledBackground, True)

        # 创建受保护的文本编辑器
        self.text_edit = ProtectedTextEdit()
        self.text_edit.setPlaceholderText("请输入内容...")
        self.text_edit.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.text_edit.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.text_edit.setFrameShape(QFrame.NoFrame)
        self.text_edit.setStyleSheet("""
            QTextEdit {
                border: none;
                padding: 15px 10px 0px 10px;
                margin: 0px;
                font-size: 20px;
                background-color: transparent;
            }
            QTextEdit:focus {
                outline: none;
            }
        """)

        # 创建布局
        self.layout = QHBoxLayout()
        self.layout.setContentsMargins(10, 5, 10, 5)  # 调整内边距
        self.layout.setSpacing(10)
        self.layout.addWidget(self.text_edit)

        self.setLayout(self.layout)

        # 设置整个小部件的背景和边框
        self.setStyleSheet("""
            InputAreaWidget {
                border: 2px solid #ccc;
                border-radius: 23px;
                background-color: whitesmoke;
            }
        """)

        # 设置固定高度
        self.setFixedHeight(65)

class InputWidget(QWidget):
    def __init__(self):
        super().__init__()
        # 设置窗口标志
        self.setWindowFlag(Qt.FramelessWindowHint)
        self.setWindowFlag(Qt.SplashScreen)
        self.setWindowFlag(Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)

        # 设置窗口大小和位置
        self.setFixedWidth(700)
        self.input_height = 65  # 输入框高度
        self.suggestion_item_height = 40  # 候选项高度

        # 创建输入区域
        self.input_area = InputAreaWidget()

        # 创建候选列表
        self.suggestion_list = QListWidget()
        self.suggestion_list.hide()
        self.suggestion_list.setStyleSheet("""
            QListWidget {
                border: 2px solid #ccc;
                border-top: none;
                border-bottom-left-radius: 23px;
                border-bottom-right-radius: 23px;
                font-size: 20px;
                background-color: whitesmoke;
            }
            QListWidget::item {
                height: 40px;
                padding-left: 20px;
            }
            QListWidget::item:selected {
                background-color: #d3d3d3; /* 浅灰色 */
                color: black;
            }
        """)

        # 功能列表
        self.suggestions = ["功能1", "功能2", "功能3"]
        for func in self.suggestions:
            item = QListWidgetItem(func)
            self.suggestion_list.addItem(item)

        # 设置布局
        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)  # 去除边距
        self.layout.setSpacing(0)  # 控件间距为0
        self.layout.addWidget(self.input_area)
        self.layout.addWidget(self.suggestion_list)
        self.setLayout(self.layout)

        # 连接信号和槽
        self.input_area.text_edit.textChanged.connect(self.on_text_changed)
        self.input_area.text_edit.installEventFilter(self)
        self.suggestion_list.itemClicked.connect(self.on_suggestion_clicked)
        self.suggestion_list.installEventFilter(self)

        # 设置快捷键
        self.shortcut_show = QShortcut(QtGui.QKeySequence("Alt+P"), self)
        self.shortcut_show.activated.connect(self.show_input_widget)
        self.shortcut_hide = QShortcut(QtGui.QKeySequence("Escape"), self)
        self.shortcut_hide.activated.connect(self.hide_input_widget)

        # 显示窗口
        self.adjust_position()
        self.adjustSize()
        self.show()

    def show_input_widget(self):
        self.show()
        self.activateWindow()
        self.input_area.text_edit.setFocus()

    def hide_input_widget(self):
        self.hide()

    def adjust_position(self):
        # 将窗口放置在屏幕高度的3/7位置
        screen = QApplication.primaryScreen().geometry()
        x = (screen.width() - self.width()) // 2
        y = screen.height() * 3 // 7
        self.move(x, y)

    def eventFilter(self, source, event):
        if event.type() == QEvent.KeyPress:
            if source == self.input_area.text_edit:
                if self.suggestion_list.isVisible():
                    # 焦点已经在候选列表，不需要处理
                    return True
                if event.key() == Qt.Key_Return or event.key() == Qt.Key_Enter:
                    self.execute_input()
                    return True
            elif source == self.suggestion_list:
                if event.key() == Qt.Key_Return or event.key() == Qt.Key_Enter:
                    self.insert_function(self.suggestion_list.currentItem().text())
                    return True
                elif event.key() == Qt.Key_Escape:
                    self.input_area.text_edit.setFocus()
                    self.suggestion_list.hide()
                    self.adjust_input_area_style()
                    self.adjustSize()
                    return True
            return False
        return super().eventFilter(source, event)

    def on_text_changed(self):
        text = self.input_area.text_edit.toPlainText()
        if text.strip() == '@':
            self.suggestion_list.show()
            self.suggestion_list.setCurrentRow(0)  # 默认选中第一项
            self.adjust_input_area_style(show_suggestions=True)
            self.adjust_suggestion_list_height()
            self.adjustSize()
            # 焦点移动到候选列表
            self.suggestion_list.setFocus()
        else:
            self.suggestion_list.hide()
            self.adjust_input_area_style(show_suggestions=False)
            self.adjustSize()

    def adjust_input_area_style(self, show_suggestions=False):
        if show_suggestions:
            # 输入框上圆角，下面直角
            self.input_area.setStyleSheet("""
                InputAreaWidget {
                    border: 2px solid #ccc;
                    border-top-left-radius: 23px;
                    border-top-right-radius: 23px;
                    border-bottom-left-radius: 0px;
                    border-bottom-right-radius: 0px;
                    background-color: whitesmoke;
                }
            """)
        else:
            # 输入框四个角都是圆角
            self.input_area.setStyleSheet("""
                InputAreaWidget {
                    border: 2px solid #ccc;
                    border-radius: 23px;
                    background-color: whitesmoke;
                }
            """)

    def adjust_suggestion_list_height(self):
        # 动态调整候选列表高度
        item_height = self.suggestion_item_height
        count = self.suggestion_list.count()
        total_height = item_height * count
        self.suggestion_list.setFixedHeight(total_height)

    def on_suggestion_clicked(self, item):
        self.insert_function(item.text())

    def insert_function(self, func_name):
        text_edit = self.input_area.text_edit
        cursor = text_edit.textCursor()
        # 移除 '@' 符号
        text = text_edit.toPlainText()
        if text.strip() == '@':
            text_edit.clear()
        else:
            cursor.movePosition(QtGui.QTextCursor.Left, QtGui.QTextCursor.KeepAnchor, 1)
            if cursor.selectedText() == '@':
                cursor.removeSelectedText()
        # 插入格式化的功能标签，并防止被删除或修改
        text_edit.setFocus()
        cursor = text_edit.textCursor()
        cursor_position = cursor.position()

        # 插入功能标签
        fmt = QtGui.QTextCharFormat()
        fmt.setForeground(QtGui.QBrush(Qt.blue))
        fmt.setBackground(QtGui.QBrush(Qt.yellow))
        text_edit.insert_protected_text(f"[{func_name}]", fmt)

        # 插入空格
        default_fmt = QtGui.QTextCharFormat()
        cursor.insertText(" ", default_fmt)

        self.suggestion_list.hide()
        self.adjust_input_area_style(show_suggestions=False)
        self.adjustSize()
        text_edit.setFocus()
        # 将光标移动到标签后
        cursor.setPosition(cursor_position + len(f"[{func_name}] ") )
        text_edit.setTextCursor(cursor)

    def execute_input(self):
        # 获取输入内容并解析
        text = self.input_area.text_edit.toPlainText()
        if '[' in text and ']' in text:
            start = text.index('[')
            end = text.index(']', start)
            func_name = text[start+1:end]
            user_input = text[end+1:].strip()
            # 调用对应的功能
            if func_name in self.suggestions:
                getattr(self, f'function_{func_name}')(user_input)
            else:
                QMessageBox.warning(self, "错误", f"未找到功能: {func_name}")
        else:
            QMessageBox.warning(self, "错误", "未指定功能")
        self.input_area.text_edit.clear()

    # 功能1
    def function_功能1(self, input_text):
        # 用户输入的文本在 input_text 中
        pass  # 在此实现功能1的逻辑

    # 功能2
    def function_功能2(self, input_text):
        # 用户输入的文本在 input_text 中
        pass  # 在此实现功能2的逻辑

    # 功能3
    def function_功能3(self, input_text):
        # 用户输入的文本在 input_text 中
        pass  # 在此实现功能3的逻辑

if __name__ == "__main__":
    app = QApplication(sys.argv)
    widget = InputWidget()
    sys.exit(app.exec_())
