<https://v-yop.github.io/2025-natsu2/07-28写一个202020应用/index.html>

通过规律弹窗提醒护眼，默认设置下每隔20分钟弹窗，护眼4分钟，再隔20分钟弹窗，3个轮次后长休，护眼13分钟。

弹窗不可手动关闭，弹窗后可要求推迟数分钟后重新弹窗。弹窗中要求用户输入当前正在干的事情，并做记录，供后续做数据统计。

配置、记录数据分别使用json，jsonl保存，不提供相应GUI界面（因为是给我自己用的！）。

# 编译

```sh
pyinstaller.exe main.py --add-data 'icon.ico:.' --icon 'asset/icon.ico' --noconsole --onefile --name MGD-Helper
```