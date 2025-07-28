from datetime import datetime, timedelta
from pathlib import Path
from pydantic import BaseModel
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *

from config import Config, get_config
from mention_dialog import DialogParam, DialogResult, MentionDialog
from tray_holder import TrayHolder

class State(BaseModel):
    is_running: bool
    is_showing_dialog: bool
    next_mention_time: datetime
    can_delay: bool
    current_round: int

class Main:
    def __init__(self, config: Config, tray: TrayHolder) -> None:
        self.__config = config
        self.__state = State(
            is_running=False,
            is_showing_dialog=False,
            next_mention_time=self.__calculate_next_mention_time(),
            can_delay=True,
            current_round=1
        )
        self.__timer = QTimer()
        self.__timer.setInterval(1000)
        self.__timer.timeout.connect(self.__loop)
        self.__tray_holder = tray
        self.__init_tray(tray)
    
    def __calculate_next_mention_time(self):
        return datetime.now() + timedelta(minutes=self.__config.mention_duration)

    def __init_tray(self, tray: TrayHolder):
        @tray.shortMention.connect
        def _():
            self.__state.can_delay = False
            self.__trigger_dialog(False)
        @tray.longMention.connect
        def _():
            self.__state.can_delay = False
            self.__trigger_dialog(True)
        @tray.resetTimer.connect
        def _():
            self.__state.next_mention_time = self.__calculate_next_mention_time()
        @tray.quitApp.connect
        def _():
            if ins := QApplication.instance():
                ins.exit(0)

    def __loop(self):
        if not self.__state.is_running:
            return
        self.__update_tray()
        if datetime.now() < self.__state.next_mention_time:
            return
        self.__trigger_dialog(self.__state.current_round > self.__config.long_mention_rounds)

    def __trigger_dialog(self, long_mention: bool):
        if self.__state.is_showing_dialog:
            return
        dialog = MentionDialog(DialogParam(
            choices=self.__config.choices,
            title='',
            duration=60 * (self.__config.long_mention_time if long_mention else self.__config.short_mention_time),
            msg=self.__config.long_mention_msg if long_mention else self.__config.short_mention_msg,
            can_delay=self.__state.can_delay,
            delay_msg=self.__config.delay_msg,
            debug=self.__config.debug,
        ))
        self.__state.is_showing_dialog = True
        response = dialog.start_mentioning()
        self.__state.is_showing_dialog = False
        self.__update_state(response, long_mention)
        self.__append_log(response)

    def __update_state(self, response: DialogResult, long_mention: bool):
        if response.action == 'DELAY':
            self.__state.next_mention_time = datetime.now() + timedelta(minutes=self.__config.delay_time)
            self.__state.can_delay = False # 禁止连续 delay
            return

        self.__state.is_showing_dialog = False
        self.__state.can_delay = True
        self.__state.next_mention_time = self.__calculate_next_mention_time()
        self.__state.current_round += 1
        if long_mention:
            self.__state.current_round = 1
        
    def __update_tray(self):
        self.__tray_holder.current_round = self.__state.current_round
        self.__tray_holder.rounds = self.__config.long_mention_rounds
        self.__tray_holder.next_mention_time = self.__state.next_mention_time

    def __append_log(self, response: DialogResult):
        with Path('log.jsonl').open('at', encoding='utf-8') as f:
            f.write(response.model_dump_json())
            f.write('\n')

    def start(self):
        self.__state.is_running = True
        self.__state.next_mention_time = self.__calculate_next_mention_time()
        self.__timer.start()


if __name__ == '__main__':
    app = QApplication([])
    app.setQuitOnLastWindowClosed(False)
    main = Main(get_config(), TrayHolder(QIcon(str((Path(__file__).parent/'icon.ico')))))
    main.start()
    app.exec()