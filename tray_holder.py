from datetime import datetime
import sys
from PyQt5.QtWidgets import QApplication, QSystemTrayIcon, QMenu, QAction, QMessageBox
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QTimer, QTime,    pyqtSignal, QObject


class TrayHolder(QObject):
    """
    Tray 包含：
        1. 下次提醒的时间
        2. 当前轮次
        3. 立即短休（轮次+1）
        4. 立即长休（轮次重置）
        5. 重设定时
        ---
        6. 退出
    """

    shortMention = pyqtSignal()
    """短休 signal"""

    longMention = pyqtSignal()
    """长休 signal"""

    resetTimer = pyqtSignal()
    """重置定时 signal"""

    quitApp = pyqtSignal()
    """退出 signal"""

    def __init__(self, icon: QIcon):
        super().__init__()
        self.__tray_icon = QSystemTrayIcon(self)
        self.__tray_icon.setIcon(icon)
        self.__tray_icon.setVisible(True)

        # 菜单和动作
        self.__menu = QMenu()
        self.__tray_icon.setContextMenu(self.__menu)
        self.__next_mention_label = QAction("下一次提醒: --:--:--")
        self.__menu.addAction(self.__next_mention_label)

        self.__current_round_label = QAction("当前轮次：-/-")
        self.__menu.addAction(self.__current_round_label)

        self.__short_action = QAction("立即短休（轮次+1）")
        self.__short_action.triggered.connect(self.shortMention)
        self.__menu.addAction(self.__short_action)

        self.__long_action = QAction("立即长休（轮次重置）")
        self.__long_action.triggered.connect(self.longMention)
        self.__menu.addAction(self.__long_action)

        self.__reset_action = QAction("重设定时")
        self.__reset_action.triggered.connect(self.resetTimer)
        self.__menu.addAction(self.__reset_action)


        self.__quit_action = QAction("退出")
        self.__quit_action.triggered.connect(self.quitApp)
        self.__menu.addAction(self.__quit_action)

        self.__current_round = -1
        self.__rounds = -1
        self.__next_mention_time = '--:--:--'

    @property
    def current_round(self):
        return self.__current_round
    
    @current_round.setter
    def current_round(self, x: int):
        self.__current_round = x
        self.__current_round_label.setText(f'当前轮次：{self.__current_round}/{self.rounds}')
    
    @property
    def rounds(self):
        return self.__rounds
    @rounds.setter
    def rounds(self, x: int):
        self.__rounds = x
        self.__current_round_label.setText(f'当前轮次：{self.__current_round}/{self.rounds}')

    @property
    def next_mention_time(self):
        return self.__next_mention_time
    @next_mention_time.setter
    def next_mention_time(self, x: datetime):
        self.__next_mention_time = x.strftime('%H:%M:%S')
        self.__next_mention_label.setText(f'下一次提醒: {self.__next_mention_time}')



if __name__ == "__main__":
    app = QApplication([])
    holder = TrayHolder(QIcon(r'D:\DESKTOP\QQ图片20250717223011.jpg'))
    update_timer = QTimer()
    update_timer.setInterval(100)
    @update_timer.timeout.connect
    def _():
        holder.next_mention_time = datetime.now()
        holder.current_round += 1
        holder.rounds += 2
    
    def go(msg: str):
        def mygo():
            # 使用弹窗
            box = QMessageBox()
            box.setText(msg)
            box.exec() 
        return mygo
    holder.shortMention.connect(go('short'))
    holder.longMention.connect(go('long'))
    holder.resetTimer.connect(go('reset'))
    update_timer.start()
    holder.quitApp.connect(lambda: app.exit())
    app.exec()