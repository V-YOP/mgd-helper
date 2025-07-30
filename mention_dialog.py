from datetime import datetime, timedelta
from typing import Annotated, Literal, cast
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from pydantic import BaseModel, Field
from sympy import sec

class DialogParam(BaseModel):
    choices: list[str] = Field([])

    title: str

    duration: int
    """in seconds"""

    msg: str

    delay_msg: str = ''
    can_delay: bool = True
    debug: bool = False

class DialogResult(BaseModel):
    action: Literal['DEBUG_CLOSE', 'DELAY', 'NORMAL']
    action_content: str = ''
    inflammation: int
    open_time: datetime
    close_time: datetime
    
class _DialogState(BaseModel):
    state: Literal['INIT', 'RUNNING', 'DONE']
    open_time: datetime = Field(default_factory=datetime.now)
    close_time: datetime = Field(default_factory=datetime.now)


class MentionDialog(QDialog):
    """
    定时的弹窗，仅包含展示、自动关闭逻辑，不包含任何其他副作用，保存记录啥的，不是这个模块的任务
    """

    def __init__(self, config: DialogParam):
        super().__init__()
        # 设置该 widget 及其所有子控件的字体大小
        self.setStyleSheet("""
            * {
                font-size: 32px;  /* 统一字体大小 */
            }
            QRadioButton::indicator {
                width: 32px;      /* 圆形标记宽度 */
                height: 32px;     /* 圆形标记高度 */
            }
        """)

        self.__config = config
        self.__state = _DialogState(state='INIT')

        self.setWindowTitle(config.title)
        self.setMinimumSize(800, 600)

        # 设置窗口标志
        self.setWindowFlags(
            Qt.Window |  # 作为窗口
            Qt.WindowStaysOnTopHint   # 始终置顶
            | Qt.CustomizeWindowHint  # 自定义窗口提示，允许我们移除关闭按钮
        )
        
        # 移除关闭按钮
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowCloseButtonHint)

        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)
        self.setLayout(layout)
        layout.addStretch(1)

        ## choices
        layout.addWidget(QLabel('我正在：', self))
        choice_button_group, choice_btns = self.__choice_widgets()
        def selected_choice_getter() -> str:
            if choice_button_group.checkedId() == -1:
                return ''
            return self.__config.choices[choice_button_group.checkedId() - 1]
        self.__selected_choice_getter = selected_choice_getter
        choice_btns_widget = QWidget(self)
        choice_btn_layout = QHBoxLayout(choice_btns_widget)
        [choice_btn_layout.addWidget(btn) for btn in choice_btns]
        layout.addWidget(choice_btns_widget)

        ## 眼睛炎症程度
        layout.addWidget(QLabel("眼睛炎症程度：", self))
        inflammation_button_group, inflammation_btns = self.__inflammation_widgets()
        def selected_inflammation_getter():
            return inflammation_button_group.checkedId()
        self.__selected_inflammation_getter = selected_inflammation_getter
        inflammation_btns_widget = QWidget(self)
        inflammation_btn_layout = QHBoxLayout(inflammation_btns_widget)
        [inflammation_btn_layout.addWidget(btn) for btn in inflammation_btns]
        layout.addWidget(inflammation_btns_widget)


        ## MSG AND TIMER_MSG
        layout.addWidget(QLabel(config.msg, self))
        self.__timer_label = QLabel(self)
        layout.addWidget(self.__timer_label)
        
        
        ## DELAY_BUTTON
        if config.can_delay:
            delay_button = QPushButton(config.delay_msg or 'DELAY ME', self)
            delay_button.clicked.connect(self.__delay_close)
            self.layout().addWidget(delay_button)

        ## DEBUG_CLOSE_BUTTON
        if config.debug:
            debug_close_button = QPushButton(self)
            debug_close_button.setText('DEBUG CLOSE')
            debug_close_button.clicked.connect(self.__debug_close)
            layout.addWidget(debug_close_button)

        self.__close_button = QPushButton(self)
        self.__close_button.setText("完成")
        self.__close_button.setEnabled(False)
        self.__close_button.clicked.connect(lambda: self.done(0))
        layout.addWidget(self.__close_button)

        layout.addStretch(1)
        self.__timer = self.__loop_timer()
        self.__timer.start()

    def __choice_widgets(self):
        button_group = QButtonGroup(self)

        btns = [QRadioButton(i, self) for i in self.__config.choices]
        for i, v in enumerate(btns):
            button_group.addButton(v, i + 1)
        return button_group, btns

    def __inflammation_widgets(self):
        button_group = QButtonGroup(self)

        btns = [QRadioButton(f'{i}', self) for i in range(1, 6)]
        for i, v in enumerate(btns):
            button_group.addButton(v, i + 1)
        return button_group, btns


    def __loop_timer(self) -> QTimer:
        timer = QTimer(self)
        timer.setInterval(100)
        @timer.timeout.connect
        def _():
            if not self.__state.state == 'RUNNING':
                return
            expect_close_time = self.__state.open_time + timedelta(seconds=self.__config.duration)
            last_delta = expect_close_time - datetime.now()
            self.__timer_label.setText(f'关闭时间剩余：{last_delta.total_seconds():.1f} s（至 {expect_close_time:%H:%M:%S} ）')
            if last_delta.total_seconds() < 0:
                self.__after_timeout()
        return timer
    
    def __after_timeout(self):
        """will repeat execute after timeout"""
        if self.__selected_choice_getter() and self.__selected_inflammation_getter() != -1:
            self.__close_button.setEnabled(True)

    def __debug_close(self):
        self.done(1)
    
    def __delay_close(self):
        self.done(2)
    
    def start_mentioning(self):
        self.__state.open_time = datetime.now()
        self.__state.state = 'RUNNING'
        code = self.exec()
        self.__state.state = 'DONE'
        self.__state.close_time = datetime.now()
        if code == 1:
            return DialogResult(action='DEBUG_CLOSE', open_time=self.__state.open_time, close_time=self.__state.close_time, inflammation=self.__selected_inflammation_getter() )
        if code == 2:
            return DialogResult(action='DELAY', open_time=self.__state.open_time, close_time=self.__state.close_time, inflammation=self.__selected_inflammation_getter())
        if choice := self.__selected_choice_getter():
            return DialogResult(action='NORMAL', action_content=choice, open_time=self.__state.open_time, close_time=self.__state.close_time, inflammation=self.__selected_inflammation_getter() )
        raise NotImplementedError('Impossible')
        # return DialogResult(action='LEAVING', open_time=self.__state.open_time, close_time=self.__state.close_time)

    # 重写closeEvent方法，禁用Alt+F4
    def closeEvent(self, event):
        event.ignore()  # 忽略关闭事件
    
    # 可选：禁用Esc键关闭
    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            event.ignore()
        else:
            super().keyPressEvent(event)

if __name__ == '__main__':
    app = QApplication([])
    dialog = MentionDialog(DialogParam(title='title',duration=5, msg='但该休息了！', debug=True, choices=['LEAVING', '画画', '健身', '娱乐', '学习']))
    print(dialog.start_mentioning())