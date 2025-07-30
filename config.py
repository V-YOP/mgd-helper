from pathlib import Path
from pydantic import BaseModel

class Config(BaseModel):
    mention_duration: int = 20
    """ 提示间隔，按 20-20-20 原则，20分钟一提醒 """

    long_mention_rounds: int = 3 
    """ 每几轮短休来一次长休，默认 3 轮，即短-短-长-短-短-长 """

    delay_time: int = 5
    """ 推迟时间，默认 5 分钟 """

    short_mention_time: int = 4
    """ 短休时间，默认 4 分钟"""

    short_mention_msg: str = '该短休了！眺望并用力闭眼1分钟，冥想 3 分钟！'

    long_mention_time: int = 13
    """ 长休时间，默认 13 分钟"""

    long_mention_msg: str = '该长休了，眺望并用力闭眼 3 分钟，冥想 10 分钟！'

    delay_msg: str = '延迟 5 分钟显示'
    delay_time: int = 5

    choices: list[str] = ['不在电脑前', '画画', '纸笔画画', '学习', '刷视频', '玩游戏']

    debug: bool = False

    muted: bool = False

def get_config():
    if Path('config.json').exists():
        try: 
            return Config.model_validate_json(Path('config.json').read_bytes())
        except: 
            pass
    default_config = Config()
    Path('config.json').write_text(default_config.model_dump_json(indent=4), encoding='utf-8')
    return default_config