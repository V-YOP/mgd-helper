from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent, QMediaPlaylist
from PyQt5.QtCore import QUrl, QObject


class MyMediaPlayer(QObject):
    def __init__(self, parent=None):
        super().__init__(parent)

        # 一次性音效播放器
        self.alarm_player = QMediaPlayer()
        self.dingdong_player = QMediaPlayer()

        # 循环播放 clock.mp3 使用 Playlist
        self.clock_player = QMediaPlayer()
        self.clock_player.setMedia(QMediaContent(QUrl.fromLocalFile("asset/clock.mp3")))
        def handle_media_status(status):
            if status == QMediaPlayer.EndOfMedia:
                self.clock_player.setPosition(0)  # 回到开头
                self.clock_player.play()
        self.clock_player.mediaStatusChanged.connect(handle_media_status)

        

    def play_alarm(self):
        self.alarm_player.setMedia(QMediaContent(QUrl.fromLocalFile("asset/alarm.wav")))
        self.alarm_player.play()

    def play_dingdong(self):
        self.dingdong_player.setMedia(QMediaContent(QUrl.fromLocalFile("asset/ding-dong.wav")))
        self.dingdong_player.play()

    def start_clock(self):
        self.clock_player.play()

    def stop_clock(self):
        self.clock_player.stop()

if __name__ == "__main__":
    from PyQt5.QtWidgets import QApplication, QPushButton, QVBoxLayout, QWidget

    app = QApplication([])

    player = MyMediaPlayer()

    window = QWidget()
    layout = QVBoxLayout()

    btn_alarm = QPushButton("播放 alarm.wav")
    btn_alarm.clicked.connect(player.play_alarm)

    btn_ding = QPushButton("播放 ding-dong.wav")
    btn_ding.clicked.connect(player.play_dingdong)

    btn_clock_start = QPushButton("开始 clock.mp3")
    btn_clock_start.clicked.connect(player.start_clock)

    btn_clock_stop = QPushButton("停止 clock.mp3")
    btn_clock_stop.clicked.connect(player.stop_clock)

    for btn in [btn_alarm, btn_ding, btn_clock_start, btn_clock_stop]:
        layout.addWidget(btn)

    window.setLayout(layout)
    window.setWindowTitle("音效播放器 Demo")
    window.show()
    app.exec_()
