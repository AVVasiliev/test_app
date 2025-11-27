from openpyxl import Workbook


class ReportGenerator:
    def __init__(self, items: dict, username: str, base_path: str):
        self.items = items
        self.username = username
        self.base_path = base_path

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    def generate(self):
        wb = Workbook()
        ws = wb.active
        ws.title = self.username
        row_title = ['Задание', 'Ответ']
        ws.append(row_title)
        for key, value in self.items.items():
            if isinstance(value, list) and isinstance(value[0], list):
                first_row = [key, *value[0]]
                ws.append(first_row)
                for i in range(1, len(value)):
                    row = ["", *value[i]]
                    ws.append(row)
            elif isinstance(value, list):
                ws.append([key, *value])
            else:
                ws.append([key, value])

        wb.save(self.base_path)
