import sys
from enum import Enum

import flet
import json
from typing import List, Optional
from pathlib import Path

# TODO attachments

# TODO correct enum class in other file
# TODO pyinstaller with flet
# TODO picture from base64 that will be builded


class InputType(Enum):
    SELECT_ONE = "select_one"
    SELECT_MULTIPLE = "select_multiple"
    TEXT = "text"
    TABLE = "table"


class TaskTab:
    def __init__(self, task_id: str, body_path: str, attachments: List[str], solution_form: dict):
        self.solutions = solution_form.get('solutions')
        self.sol_type = solution_form.get('type')
        self.task_id = task_id
        self.task_body = body_path
        self.attachments = attachments

        self.text_solution = flet.Text()
        self.values = []
        self.tab = None
        self.image = None
        self.solution_item = None
        self.button = flet.ElevatedButton(text='Подтвердить', on_click=self.enter_answer)

    def enter_answer(self, event):
        result = ''

        if self.sol_type in [InputType.SELECT_ONE.value, InputType.TEXT.value]:
            result = self.solution_item.value
        elif self.sol_type == InputType.TABLE.value:
            items: list = self.solution_item.data
            result = [
                [items[i][j].value for i in range(len(items))]
                for j in range(len(items[-1]))
            ]
        elif self.sol_type == InputType.SELECT_MULTIPLE.value:
            result = [item.label for item in self.solution_item.controls if item.value]

        if not result:
            return

        self.text_solution.value = f'Ваш ответ: {result}'
        self.text_solution.update()
        self.tab.tab_content = flet.Row(controls=[
            flet.Icon(name=flet.icons.CHECK, color=flet.colors.GREEN),
            flet.Text(value=self.tab.text)
        ])
        self.tab.update()

    def on_scroll_image(self, event: flet.ScrollEvent):
        # scale image to minimum 50% size
        if self.image.scale > 0.5 and event.scroll_delta_y > 0:
            self.image.scale = self.image.scale - 0.1
        elif event.scroll_delta_y < 0:
            self.image.scale = self.image.scale + 0.1

        self.image.update()

    def _move_image_offset(self, x: Optional[float], y: Optional[float]):
        self.image.offset = flet.transform.Offset(
            self.image.offset.x + 0.05 * (x / abs(x) if x else 0),
            self.image.offset.y + 0.05 * (y / abs(y) if y else 0)
        )
        self.image.update()

    def _restore_image(self, event):
        self.image.scale = 1.0
        self.image.offset = flet.transform.Offset(0, 0)
        self.image.update()

    def drag_image(self, event: flet.gesture_detector.DragUpdateEvent):
        if abs(event.delta_x) > 5 >= abs(event.delta_y):
            self._move_image_offset(event.delta_x, None)
        elif abs(event.delta_y) > 5 >= abs(event.delta_x):
            self._move_image_offset(None, event.delta_y)
        elif abs(event.delta_x) > 5 and abs(event.delta_y) > 5:
            self._move_image_offset(event.delta_x, event.delta_y)

    @staticmethod
    def _build_custom_table(rows: int, columns: int) -> flet.DataTable:
        text_fields = [
            [flet.TextField(content_padding=0, border_width=0)
             for _ in range(rows)] for _ in range(columns)
        ]

        dt = flet.DataTable(
            columns=[
                flet.DataColumn(flet.Text()),
                *[flet.DataColumn(flet.Text(chr(value + 65))) for value in range(columns)]
            ],
            data=text_fields,
            rows=[
                flet.DataRow(
                    cells=[
                        flet.DataCell(flet.Text(str(j + 1), width=10)),
                        *[
                            flet.DataCell(flet.Container(
                                content=text_fields[i][j],
                                margin=flet.Margin(left=-30, bottom=0, right=0, top=0), padding=2,
                                border=flet.border.only(left=flet.border.BorderSide(1, flet.colors.BLACK26)),
                                width=80, height=30, expand=1)
                            ) for i in range(columns)
                        ]
                    ],
                ) for j in range(rows)
            ]
        )
        return dt

    def _build_solution_form(self):
        if self.sol_type == InputType.SELECT_ONE.value:
            self.solution_item = flet.RadioGroup(
                content=flet.Column(
                    controls=[
                        flet.Radio(
                            label=value.get('answer'),
                            value=value.get('answer')
                        ) for value in self.solutions
                    ]
                )
            )
        elif self.sol_type == InputType.SELECT_MULTIPLE.value:
            self.solution_item = []
            for label in self.solutions:
                self.solution_item.append(flet.Checkbox(label=label.get('answer')))
            self.solution_item = flet.Column(controls=self.solution_item)
        elif self.sol_type == InputType.TEXT.value:
            self.solution_item = flet.TextField(label='Ответ', expand=1)
        elif self.sol_type == InputType.TABLE.value:
            row, column = len(self.solutions), len(self.solutions[-1])
            self.solution_item = self._build_custom_table(row, column)

    def create_page(self):
        # require in flet.app define assets_dir, path to pict ONLY relative
        self.image = flet.Image(
                src=self.task_body,
                scale=1,
                offset=flet.transform.Offset(0, 0),
                tooltip='Двойной клик ЛКМ для восстановления исходного размера'
            )
        image_container = flet.Container(
            content=flet.GestureDetector(
                content=self.image, on_scroll=self.on_scroll_image, expand=1,
                on_vertical_drag_update=self.drag_image,
                on_horizontal_drag_update=self.drag_image,
                drag_interval=50,
                on_double_tap=self._restore_image
            ),
            alignment=flet.alignment.top_left,
            expand=2,
            clip_behavior=flet.ClipBehavior.HARD_EDGE
        )

        solution_form = flet.Row()
        self._build_solution_form()
        solution_form.controls.append(self.solution_item)

        tab_content = flet.Container(
            content=flet.Row(controls=[
                image_container,
                flet.VerticalDivider(width=2),
                flet.Column(controls=[
                    solution_form,
                    self.button,
                    self.text_solution
                ], expand=1)
            ]),
            border=flet.border.all(2, flet.colors.BLUE), border_radius=10,
            padding=5,
            margin=5
        )

        self.tab = flet.Tab(
            text=f'{self.task_id}',
            content=tab_content
        )
        return self.tab


def main(page: flet.Page):
    if sys.executable.endswith('python.exe'):
        data_folder: Path = Path(__file__).parent / 'test_data'
    else:
        data_folder: Path = Path(sys.executable).parent / 'test_data'

    tasks: list = json.loads(Path(data_folder / "task_data.json").read_text(encoding='utf-8'))
    tabs = flet.Tabs(
        selected_index=0,
        tabs=[],
        expand=1,
        animation_duration=300
    )
    tabs_objects = []
    for task in tasks:
        task_tab = TaskTab(
            body_path=task.get('body'),
            task_id=task.get('task_id'),
            attachments=[],
            solution_form=task.get('solution_form')
        )
        tabs.tabs.append(task_tab.create_page())
        tabs_objects.append(task_tab)

    page.navigation_bar = flet.NavigationBar(
        destinations=[
            flet.NavigationDestination(
                icon=flet.icons.CLOSE,
                selected_icon=flet.icons.CLOSE,
                label="Завершить тест",
            ),
        ],
        on_change=lambda e: print(e)
    )

    page.add(tabs)


if __name__ == '__main__':
    if sys.executable.endswith('python.exe'):
        data_folder: Path = Path(__file__).parent / 'test_data'
    else:
        data_folder: Path = Path(sys.executable).parent / 'test_data'

    flet.app(
        target=main,
        assets_dir=str(data_folder / 'data')
    )
