# Инструкция по сборке

Требуется заполнить конфиг `configs.json` актуальными значениями.

Команда сборки:
`pyinstaller -F --noconsole --add-data="configs.json;." --add-data="logo.ico;." --icon=logo.ico -n update_vt_bases main.py`

Результат можно будет найти в папке ``dist``.