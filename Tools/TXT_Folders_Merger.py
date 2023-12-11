import os
import shutil
from PyQt5.QtWidgets import (
    QApplication,
    QWidget,
    QVBoxLayout,
    QPushButton,
    QFileDialog,
    QMessageBox,
)
from PyQt5.QtCore import QFile, QDir
from pathlib import Path
from dataclasses import dataclass


@dataclass
class FileData:
    key_align: int
    data: dict[str, str]


class FileMerger(QWidget):
    def __init__(self):
        super().__init__()
        self.dir_a = None
        self.dir_b = None
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()
        self.select_dir_a_btn = QPushButton("Select folder A")
        self.select_dir_b_btn = QPushButton("Select folder B")
        self.merge_btn = QPushButton("Merge")

        self.select_dir_a_btn.clicked.connect(self.select_directory_a)
        self.select_dir_b_btn.clicked.connect(self.select_directory_b)
        self.merge_btn.clicked.connect(self.merge)

        layout.addWidget(self.select_dir_a_btn)
        layout.addWidget(self.select_dir_b_btn)
        layout.addWidget(self.merge_btn)
        self.setLayout(layout)

    def select_directory_a(self):
        path_str = QFileDialog.getExistingDirectory(self, "Select folder A")
        if path_str:
            self.dir_a = Path(path_str)
            self.select_dir_a_btn.setText(self.dir_a.name)
            self.select_dir_a_btn.setEnabled(False)
            QMessageBox.information(self, "Folder A", "Selected: " + str(self.dir_a))

    def select_directory_b(self):
        path_str = QFileDialog.getExistingDirectory(self, "Select folder B")
        if path_str:
            self.dir_b = Path(path_str)
            self.select_dir_b_btn.setText(self.dir_b.name)
            self.select_dir_b_btn.setEnabled(False)
            QMessageBox.information(self, "Folder B", "Selected: " + str(self.dir_b))

    def merge(self):
        if not self.dir_a or not self.dir_b:
            QMessageBox.warning(self, "Warning", "Please select both folders")
            return

        out_dir = self.dir_a.parent / "output"
        out_dir.mkdir(parents=True, exist_ok=True)

        self.copy_files(self.dir_a, out_dir)
        self.copy_files(self.dir_b, out_dir)

        QMessageBox.information(self, "Success", "Merged files are in: " + str(out_dir))

    def chop_file(self, path: Path) -> FileData:
        d = FileData(0, dict())

        with open(path, "r", encoding="utf-8-sig") as f:
            # Obtener padding
            ln = f.readline().rstrip()

            k, v = ln.split(":", maxsplit=1)

            left_pad = len(k)
            left_pad += len(v) - len(v.lstrip(" "))

            d.key_align = left_pad + 1
            f.seek(0)

            # Extraer datos
            while line := f.readline():
                key, val = line.rstrip().split(":", maxsplit=1)
                val = val.lstrip(" ")

                if val.startswith('"'):
                    val = val[1:]  # quitamos la comilla inicial
                    while True:
                        ln = f.readline().rstrip()
                        if ln == "":
                            val = val[:-1]  # quitamos la comilla final
                            break
                        val += "\n" + ln.lstrip(" ")

                val = val.replace("\\\\", "\\").replace('\\"', '"')

                # Comprobar que no haya claves duplicadas (sanity check)
                if key in d.data:
                    raise ValueError

                d.data[key] = val

        return d

    def save_file(self, path: Path, fdata: FileData) -> None:
        with open(path, "w", encoding="utf-8-sig") as file:
            align = fdata.key_align
            for k, v in fdata.data.items():
                key = k + ":"
                text = v.replace("\\", "\\\\").replace('"', '\\"')

                if "\n" in text:
                    text = '"' + text + '"'

                    lines = text.split("\n")
                    file.write(f"{key: <{align}}{lines[0]}\n")

                    for line in lines[1:]:
                        file.write((" " * align) + f"{line}\n")

                    file.write("\n")
                else:
                    file.write(f"{key: <{align}}{text}\n")

    def copy_files(self, src_dir: Path, dst_dir: Path) -> None:
        for src_file in src_dir.rglob("*.*"):
            dst_file = dst_dir / src_file.relative_to(src_dir)

            dst_file.parent.mkdir(parents=True, exist_ok=True)
            if src_file.suffix == ".txt":
                if dst_file.exists():
                    src_data = self.chop_file(src_file)
                    dst_data = self.chop_file(dst_file)

                    # Unir los datos, tomar el padding más grande
                    if src_data.key_align > dst_data.key_align:
                        dst_data.key_align = src_data.key_align

                    dst_data.data |= src_data.data

                    # Guardar
                    self.save_file(dst_file, dst_data)
                    continue
            
            shutil.copy(src_file, dst_file)


if __name__ == "__main__":
    app = QApplication([])
    ex = FileMerger()
    ex.show()
    app.exec_()
