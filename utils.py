import flet
import sys
import json
from pathlib import Path
from encryption import encrypt_data

if sys.executable.endswith('python.exe'):
    MAIN_PATH = Path(__file__).parent
else:
    MAIN_PATH = Path(sys.executable).parent


def get_all_answers(page: flet.Page) -> list:
    answers = []
    tabs_block: flet.Tabs = next(filter(lambda item: item.data == 'main_tabs', page.controls))
    for tab in tabs_block.tabs:
        if hasattr(tab.content.data, 'get_result'):
            answers.append(tab.content.data.get_result())
    return answers


def save_answers(page: flet.Page, path: str, encrypted: bool = False):
    if not page.data.get('answers_available'):
        return

    answers = get_all_answers(page)
    data = {i: value for i, value in enumerate(answers)}

    if not encrypted:
        with open(path, 'w') as file:
            dumped_json: str = json.dumps(data, indent=4, ensure_ascii=False)
            file.write(dumped_json)
    else:
        with open(MAIN_PATH / 'result.data', 'wb') as file:
            dumped_json: str = json.dumps(data, indent=4, ensure_ascii=False)
            file.write(encrypt_data(dumped_json.encode('utf-8')))


def save_result_to_file(event: flet.FilePickerResultEvent):
    if event.path:
        save_answers(event.page, event.path)


def create_result_table(page: flet.Page):
    tabs_block: flet.Tabs = next(filter(lambda item: item.data == 'main_tabs', page.controls))
    if tabs_block.tabs[len(tabs_block.tabs) - 1].text == "Ответы":
        tabs_block.tabs.pop(len(tabs_block.tabs) - 1)

    dt = flet.DataTable(
        columns=[
            flet.DataColumn(flet.Text('Номер задания')),
            flet.DataColumn(flet.Text('Ответ'))
        ],
        rows=[
            flet.DataRow(
                cells=[
                    flet.DataCell(flet.Text(str(i + 1), width=50)),
                    flet.DataCell(flet.Text(str(value)))
                ],
            ) for i, value in enumerate(get_all_answers(page))
        ],
        show_bottom_border=True,
        data_row_height=24
    )
    tab = flet.Tab(text='Ответы', content=flet.Column(
        controls=[flet.Container(
            content=dt, margin=40, border=flet.border.all(2, 'blue'), border_radius=10,
            alignment=flet.alignment.center
        )],
        scroll=flet.ScrollMode.ADAPTIVE)
    )
    tabs_block: flet.Tabs = next(filter(lambda item: item.data == 'main_tabs', page.controls))
    tabs_block.tabs.append(tab)
    tabs_block.selected_index = len(tabs_block.tabs) - 1
    page.update()


def close_dlg_false(e):
    e.page.dialog.open = False
    e.page.update()


def close_dlg_true(event):
    create_result_table(event.page)
    dialog = event.page.data.get('save_result_dialog')
    dialog.save_file(
        initial_directory=str(MAIN_PATH),
        file_name=event.page.client_storage.get('user_key') + ".json"
    )
    event.page.dialog.open = False
    event.page.update()


def close_alert_bar(event):
    dlg = flet.AlertDialog(
        modal=True,
        title=flet.Text('Завершить тест?'),
        content=flet.Text('После заверешения теста ответ будет сохранен в файл result.json '),
        actions=[
            flet.TextButton('Да', on_click=close_dlg_true),
            flet.TextButton('Нет', on_click=close_dlg_false)
        ],
        on_dismiss=close_dlg_false,
        open=True
    )
    event.page.dialog = dlg
    event.page.update()
