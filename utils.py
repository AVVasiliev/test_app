import sys
from pathlib import Path

import flet

from xlsx_generator import ReportGenerator

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


def save_answers(page: flet.Page, path: str):
    if not page.data.get('answers_available'):
        return

    answers = get_all_answers(page)
    data = {i + 1: value for i, value in enumerate(answers)}

    report_path = Path(path).parent / f'Ответы_{page.client_storage.get("user_key")}.xlsx'
    with ReportGenerator(data, page.client_storage.get("user_key"), str(report_path)) as generator:
        generator.generate()
        return


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
        file_name="Ответы_" + event.page.client_storage.get('user_key') + ".xlsx"
    )
    event.page.dialog.open = False
    event.page.update()


def close_alert_bar(event):
    dlg = flet.AlertDialog(
        modal=True,
        title=flet.Text('Завершить тест?'),
        content=flet.Text('После заверешения теста ответ будет сохранен в файл Ответы_ФИО.xlsx '),
        actions=[
            flet.TextButton('Да', on_click=close_dlg_true),
            flet.TextButton('Нет', on_click=close_dlg_false)
        ],
        on_dismiss=close_dlg_false,
        open=True
    )
    event.page.dialog = dlg
    event.page.update()
