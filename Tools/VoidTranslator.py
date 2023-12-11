import sys
import os
from dataclasses import dataclass
from pathlib import Path
from PyQt5 import QtCore
from PyQt5.QtCore import QFile, QTextStream, Qt
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
    QPushButton,
    QFileDialog,
    QComboBox,
    QStatusBar,
    QHBoxLayout,
    QLineEdit,
    QStyledItemDelegate,
    QTextEdit,
    QHeaderView,
    QAbstractItemView,
)


@dataclass
class key_val:
    text: str
    blanks: str


class HighlightDelegate(QStyledItemDelegate):
    def __init__(self, parent=None):
        super(HighlightDelegate, self).__init__(parent)
        self.matched_text = ""

    def setMatchedText(self, text):
        self.matched_text = text

    def paint(self, painter, option, index):
        text = index.data(QtCore.Qt.DisplayRole)
        if self.matched_text and self.matched_text.lower() in text.lower():
            painter.fillRect(option.rect, QColor("yellow"))

        QStyledItemDelegate.paint(self, painter, option, index)

    # Agradecimientos especiales a Mr. GPT
    def createEditor(self, parent, option, index):
        editor = QTextEdit(parent)
        return editor

    def setEditorData(self, editor, index):
        editor.setPlainText(index.model().data(index, role=0))

    def setModelData(self, editor, model, index):
        model.setData(index, editor.toPlainText(), role=0)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.base_folder: Path
        self.text_files: list[Path] = []

        self.setWindowTitle("VoidTranslator")

        self.resize(640, 480)
        self.setMinimumSize(640, 480)

        self.table = QTableWidget(0, 3, self)
        self.table.setHorizontalHeaderLabels(["Key", "Blanks", "Text"])
        self.table.itemChanged.connect(self.item_changed)
        self.table.setColumnHidden(1, True)
        self.table.verticalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Interactive
        )
        self.table.setHorizontalScrollMode(QAbstractItemView.ScrollMode.ScrollPerPixel)

        self.highlight_delegate = HighlightDelegate(self.table)
        self.table.setItemDelegateForColumn(2, self.highlight_delegate)

        top_layout = QHBoxLayout()

        self.file_selector = QComboBox()
        self.file_selector.currentIndexChanged.connect(self.load_file)
        top_layout.addWidget(self.file_selector)

        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("Search...")
        self.search_box.textChanged.connect(self.search_text)
        self.search_box.setFixedWidth(200)
        top_layout.addWidget(self.search_box)

        self.save_button = QPushButton("Save Changes")
        self.save_button.clicked.connect(self.save_changes)
        self.save_button.setEnabled(False)
        self.save_button.setFixedWidth(100)
        top_layout.addWidget(self.save_button)

        layout = QVBoxLayout()
        layout.addLayout(top_layout)
        layout.addWidget(self.table)

        self.folder_button = QPushButton("Select Folder")
        self.folder_button.clicked.connect(self.select_folder)
        layout.addWidget(self.folder_button)

        widget = QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)

        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)

        self.num_lines = 0
        self.num_modified_lines = 0
        self.matching_files = 0

    def get_path_pretty(self, path: Path) -> str:
        rel_path = str(path.relative_to(self.base_folder))
        return rel_path.replace(os.path.sep, " > ")

    def save_changes(self) -> None:
        sel_idx: int = self.file_selector.currentIndex()
        file_path = self.file_selector.itemData(sel_idx, Qt.ItemDataRole.UserRole)

        # Transformamos el texto de vuelta
        with open(file_path, "w", encoding="utf-8-sig") as file:
            for row in range(self.table.rowCount()):
                # Se extrae la clave y se inserta el ':'
                key = self.table.item(row, 0).text()
                key += ":"

                # Se extraen los espacios
                blanks = self.table.item(row, 1).text()

                # Se extrae el valor
                text = self.table.item(row, 2).text()
                # normalizar saltos de línea
                text = text.replace("\r\n", "\n")
                text = text.replace("\n\r", "\n")
                text = text.replace("\r", "\n")
                # escapar caracteres
                text = text.replace("\\", "\\\\").replace('"', '\\"')

                # En caso de ser texto multi línea hacer se trata de forma especial
                if "\n" in text:
                    # El texto multi línea va encomillado
                    text = '"' + text + '"'

                    # Las líneas deben estar alineadas
                    pad_str = (" " * len(key)) + blanks

                    # Obtener líneas individuales
                    lines = text.split("\n")

                    # Escribir primera línea
                    file.write(key + blanks + lines[0] + "\n")

                    # Escribir el resto
                    for line in lines[1:]:
                        file.write(pad_str + line + "\n")

                    # Añadir salto de línea vacío
                    file.write("\n")
                else:
                    file.write(key + blanks + text + "\n")

        self.save_button.setEnabled(False)
        self.num_modified_lines = 0
        self.update_status_bar()

    def select_folder(self) -> None:
        folder_path = QFileDialog.getExistingDirectory(self, "Select Folder")

        # No hay carpeta no hay fiesta
        if folder_path == "":
            return

        self.folder_button.hide()
        self.text_files.clear()

        self.base_folder = Path(folder_path)
        for p in self.base_folder.rglob("*.txt"):
            self.text_files.append(p)
            name = self.get_path_pretty(p)
            self.file_selector.addItem(name, p)

    def dict_from_file(self, path: Path) -> dict[str, key_val]:
        d = dict()

        self.file = QFile(str(path))
        self.file.open(QFile.ReadOnly | QFile.Text)
        inStream = QTextStream(self.file)
        inStream.setCodec("utf-8-sig")

        while not inStream.atEnd():
            # Obtener línea original
            raw_line = inStream.readLine()

            # Los archivos contienen pares clave-valor separados
            # por ':' (con espacios opcionales en medio), con esta
            # garantía en mente separamos en el primer ':' que encontremos
            key, raw_value = raw_line.split(":", maxsplit=1)

            # Como necesitamos conservar los espacios intermedios primero
            # sacamos la cuenta y los restauramos al final del parseo
            value_clean = raw_value.lstrip(" ")
            ws_count = len(raw_value) - len(value_clean)

            # En caso de que un valor comience con comillas (") significa
            # que es un valor multi línea, así que necesitamos consumir
            # líneas extra para obtener el valor completo, la buena
            # noticia es que las entradas multi línea dejan un espacio
            # en blanco justo después, lo que facilita el parseo
            if value_clean.startswith('"'):
                value = value_clean[1:]  # quitamos la comilla inicial
                while True:
                    ln = inStream.readLine()
                    if ln == "":
                        value = value[:-1]  # quitamos la comilla final
                        break
                    value += "\n" + ln.lstrip(" ")
            else:
                value = value_clean

            # des-escapar caracteres
            value = value.replace("\\\\", "\\").replace('\\"', '"')

            # Comprobar que no haya claves duplicadas (sanity check)
            if key in d:
                raise ValueError

            # Insertar clave y continuar
            d[key] = key_val(value, " " * ws_count)

        return d

    def load_file(self, index) -> None:
        file_path = self.file_selector.itemData(index, Qt.ItemDataRole.UserRole)

        # Limpiar la tabla antes de cargar un nuevo archivo
        self.table.setRowCount(0)
        entries: dict[str, key_val] = self.dict_from_file(file_path)

        for row, (key, v) in enumerate(entries.items()):
            self.table.insertRow(row)

            key_item = QTableWidgetItem(key)
            key_item.setFlags(key_item.flags() ^ Qt.ItemFlag.ItemIsEditable)
            self.table.setItem(row, 0, key_item)

            blanks_item = QTableWidgetItem(v.blanks)
            blanks_item.setFlags(blanks_item.flags() ^ Qt.ItemFlag.ItemIsEditable)
            self.table.setItem(row, 1, blanks_item)

            value_item = QTableWidgetItem(v.text)
            self.table.setItem(row, 2, value_item)

        self.table.resizeColumnsToContents()
        self.table.resizeRowsToContents()
        self.save_button.setEnabled(False)
        self.num_lines = self.table.rowCount()
        self.num_modified_lines = 0
        self.update_status_bar()

    def item_changed(self, item):
        if item.column() == 2:  # Solo contar las modificaciones en la columna "Text"
            self.save_button.setEnabled(True)
            self.num_modified_lines += 1
            self.update_status_bar()

    def search_text(self, text: str) -> None:
        # Cantidad de archivos con el texto deseado
        matching_files = 0

        # Se limpia la lista de archivos
        self.file_selector.clear()

        # Nada que buscar, repoblar la lista con los
        # archivos originales y volver
        if text == "":
            self.highlight_delegate.setMatchedText(None)
            self.table.viewport().update()
            for p in self.text_files:
                name: str = self.get_path_pretty(p)
                self.file_selector.addItem(name, p)
        else:
            # La búsqueda es insesible a las mayúsculas
            text = text.lower()
            for p in self.text_files:
                match = False
                entries: dict[str, key_val] = self.dict_from_file(p)
                for v in entries.values():
                    if text in v.text.lower():
                        match = True
                        break
                if match:
                    name: str = self.get_path_pretty(p)
                    self.file_selector.addItem(name, p)
                    matching_files += 1

            self.highlight_delegate.setMatchedText(text)
            self.table.viewport().update()

        self.matching_files = matching_files
        self.update_status_bar()

    def update_status_bar(self) -> None:
        message = f"Lines: {self.num_lines} - Modified: {self.num_modified_lines} - Matching files: {self.matching_files}"
        self.status_bar.showMessage(message)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
