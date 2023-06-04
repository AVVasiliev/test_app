# Инструкция по сборке

Требуется заполнить конфиг `configs.json` актуальными значениями.

Команда сборки:
`pyinstaller -F --noconsole --add-data="configs.json;." --add-data="logo.ico;." --icon=logo.ico -n update_vt_bases main.py`

Результат можно будет найти в папке ``dist``.

flet pack main.py --icon icon.ico --product-name "Test system" --product-version 0.2.1 --file-version 0.2.1 --file-description "Test system from P117" --name "test_system"

Не работает с русским языком
