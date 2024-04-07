from functools import partial

import flet
import datetime
import threading
import time
from pathlib import Path


TITLE_PATH = Path(__file__).parent / 'static' / 'title.png'


def build_timer_repr(total_seconds: int) -> str:
    hours: int = total_seconds // 3600
    minutes: int = total_seconds // 60 % 60
    seconds: int = total_seconds % 60
    return (f"{hours}:" if hours else "") + (f"{minutes}".zfill(2) + ":" + f"{seconds}".zfill(2))


def disable_answers(page: flet.Page):
    tabs_block: flet.Tabs = next(filter(lambda item: item.data == 'main_tabs', page.controls))
    for tab in tabs_block.tabs:
        if hasattr(tab.content.data, 'get_result'):
            tab.content.data.button.disabled = True
    page.data['answers_available'] = False
    page.update()


def thread_timer(page: flet.Page):
    base = page.title
    duration: int = int(page.data.get('total_time'))
    finish: datetime.datetime = datetime.datetime.fromtimestamp(
        page.client_storage.get('user_start')
    ) + datetime.timedelta(minutes=duration)

    current = int((finish - datetime.datetime.now()).total_seconds())
    while current > 0:
        page.title = base + f" {build_timer_repr(current)}"
        page.update()
        time.sleep(1)
        current = int((finish - datetime.datetime.now()).total_seconds())

    page.title = f"{base} - время истекло"
    disable_answers(page)
    page.update()


def add_tabs_to_page(tabs: flet.Tabs, navigation_bar: flet.NavigationBar, event: flet.ControlEvent):

    for control in event.page.controls:
        if control.data == '__INPUT_FORM__':
            event.page.remove(control)

    event.page.client_storage.set("user_key", "_".join(map(
        lambda item: item.value.replace(' ', ''),
        event.control.data)
    ))

    now_timestamp: float = datetime.datetime.now().timestamp()
    event.page.client_storage.set("user_start", now_timestamp)

    event.page.add(tabs)
    event.page.navigation_bar = navigation_bar
    event.page.update()
    threading.Thread(target=thread_timer, args=(event.page,), daemon=True).start()


def build_input_form(page: flet.Page, tabs: flet.Tabs, navigation_bar: flet.NavigationBar):
    name = flet.TextField(label='Имя')
    family = flet.TextField(label='Фамилия')
    group = flet.TextField(label='Группа')

    form = flet.Container(content=flet.ResponsiveRow(
        controls=[
            flet.Column(
                controls=[
                    flet.Text('Форма подготовки'), family, name, group,
                    flet.TextButton(
                        text='Запустить тест',
                        on_click=partial(add_tabs_to_page, tabs, navigation_bar),
                        data=(name, family, group)
                    ),
                ], col=4
            ),
            flet.Container(
                content=flet.Image(
                    src=str(TITLE_PATH),
                    scale=0.8,
                ),
                alignment=flet.alignment.top_left,
                border=flet.border.all(2, flet.colors.BLUE), border_radius=10,
                clip_behavior=flet.ClipBehavior.HARD_EDGE,
                col=8,
            )
        ]), data='__INPUT_FORM__')
    page.add(form)
    page.update()

