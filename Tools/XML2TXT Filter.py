from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QPushButton,
    QStatusBar,
    QVBoxLayout,
    QWidget,
    QFileDialog,
    QProgressBar,
)
from PyQt5.QtCore import Qt
import xml.etree.ElementTree as ET
from pathlib import Path


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()

        self.setWindowTitle("PyQt5 App")

        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)

        self.select_folder_button = QPushButton("Select folder")
        self.select_folder_button.clicked.connect(self.select_folder)

        self.process_button = QPushButton("Process")
        self.process_button.clicked.connect(self.process_files)

        self.progress_bar = QProgressBar()
        self.progress_bar.hide()

        layout = QVBoxLayout()
        layout.addWidget(self.select_folder_button)
        layout.addWidget(self.process_button)
        layout.addWidget(self.progress_bar)

        central_widget = QWidget()
        central_widget.setLayout(layout)

        self.setCentralWidget(central_widget)

    def select_folder(self):
        folder_path = QFileDialog.getExistingDirectory(self, "Select Folder")

        # No hay carpeta no hay fiesta
        if folder_path == "":
            return

        self.folder_path = Path(folder_path)
        self.status_bar.showMessage(f"Selected folder: {self.folder_path.stem}")

    def is_line_valid(self, line) -> bool:
        if line and not line.lower().startswith(("(unused)", "(scripted)", "$")):
            return True
        else:
            return False

    def process_files(self):
        self.status_bar.hide()
        self.progress_bar.show()
        files = list(self.folder_path.rglob("*.xml"))
        total_files = len(files)
        self.progress_bar.setMaximum(total_files)
        out_dir = self.folder_path.parent / "data"
        out_dir.mkdir(exist_ok=True)

        for i, file in enumerate(files):
            new_path = out_dir / file.relative_to(self.folder_path)
            new_path = new_path.parent / "localization" / new_path.name
            new_path = new_path.with_suffix(".en_us.txt")

            tree = ET.parse(file)
            title_elements = tree.findall(".//title")
            desc_elements = tree.findall(".//description")
            title_text = [t.text for t in title_elements if self.is_line_valid(t.text)]
            desc_text = [d.text for d in desc_elements if self.is_line_valid(d.text)]
            if title_text or desc_text:
                new_path.parent.mkdir(parents=True, exist_ok=True)
                with open(
                    new_path,
                    "w",
                    encoding="utf-8",
                ) as f:
                    for text in title_text:
                        f.write(f"{'header.title:': <25}{text}\n")
                    for text in desc_text:
                        f.write(f"{'header.description:': <25}{text}\n")
            self.progress_bar.setValue(i)
            self.status_bar.showMessage(f"Processed files: {i} of {total_files}")

        self.progress_bar.hide()
        self.status_bar.showMessage(f"Processed {total_files} XML files.")


app = QApplication([])
window = MainWindow()
window.show()
app.exec_()
