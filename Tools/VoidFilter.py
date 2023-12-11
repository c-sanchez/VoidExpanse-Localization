import os
import logging
import shutil
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QPushButton, QLabel, QInputDialog, QMessageBox, QComboBox, QStatusBar, QWidget, QFileDialog

class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()

        self.setWindowTitle("VoidFilter")
        self.resize(320, 120)
        self.setMinimumSize(320, 150)
        self.setMaximumSize(320, 150)

        self.centralWidget = QWidget()
        self.setCentralWidget(self.centralWidget)

        self.layout = QVBoxLayout()
        self.centralWidget.setLayout(self.layout)

        self.pathLabel = QLabel("No folder selected")
        self.layout.addWidget(self.pathLabel)

        self.folderButton = QPushButton("Select Folder")
        self.folderButton.clicked.connect(self.selectFolder)
        self.layout.addWidget(self.folderButton)

        self.comboBox = QComboBox()
        languages = {
            'en_us': 'English',
            'af_za': 'Afrikaans',
            'ar_ae': 'Arabic',
            'eu_es': 'Basque',
            'be_by': 'Belarusian',
            'bg_bg': 'Bulgarian',
            'ca_es': 'Catalan',
            'zh_ch': 'Chinese Simplified',
            'zh_tw': 'Chinese Traditional',
            'cs_cz': 'Czech',
            'da_dk': 'Danish',
            'nl_be': 'Dutch',
            'en_uk': 'English UK',
            'et_ee': 'Estonian',
            'fo_fo': 'Faroese',
            'fi_fi': 'Finnish',
            'fr_fr': 'French',
            'de_de': 'German',
            'el_gr': 'Greek',
            'he_il': 'Hebrew',
            'hu_hu': 'Hungarian',
            'is_is': 'Icelandic',
            'id_id': 'Indonesian',
            'it_it': 'Italian',
            'jp_jp': 'Japanese',
            'ko_kr': 'Korean',
            'lv_lv': 'Latvian',
            'lt_lt': 'Lithuanian',
            'nb_no': 'Norwegian',
            'pl_pl': 'Polish',
            'pt_pt': 'Portuguese',
            'pt_br': 'Portuguese Brazilian',
            'ro_ro': 'Romanian',
            'ru_ru': 'Russian',
            'sr_sp': 'Serbian',
            'sk_sk': 'Slovak',
            'sl_sl': 'Slovenian',
            'es_es': 'Spanish',
            'sv_se': 'Swedish',
            'th_th': 'Thai',
            'tr_tr': 'Turkish',
            'uk_ua': 'Ukrainian',
            'vi_vn': 'Vietnamese'
        }
        for code, name in languages.items():
            self.comboBox.addItem(f"{code} - {name}", code)
        self.layout.addWidget(self.comboBox)

        self.startButton = QPushButton("Start")
        self.startButton.clicked.connect(self.start)
        self.layout.addWidget(self.startButton)

        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)

        self.folder_path = None
        self.texts_to_keep = None

    def selectFolder(self):
        self.folder_path = QFileDialog.getExistingDirectory(self, 'Select Folder')
        self.pathLabel.setText(self.folder_path)

    def start(self):
        self.texts_to_keep = [self.comboBox.currentData()]

        logger_deleted = logging.getLogger('deleted')
        logger_deleted.setLevel(logging.INFO)
        handler_deleted = logging.FileHandler('log_deleted.txt')
        logger_deleted.addHandler(handler_deleted)

        logger_kept = logging.getLogger('kept')
        logger_kept.setLevel(logging.INFO)
        handler_kept = logging.FileHandler('log_kept.txt')
        logger_kept.addHandler(handler_kept)

        count_deleted = 0
        count_kept = 0

        for root, dirs, files in os.walk(self.folder_path, topdown=False):
            for file in files:
                file_path = os.path.join(root, file)
                if not any(text in file for text in self.texts_to_keep):
                    os.remove(file_path)
                    logger_deleted.info(f'Deleted: {file_path}')
                    count_deleted += 1
                else:
                    logger_kept.info(f'Kept: {file_path}')
                    count_kept += 1

            if not os.listdir(root):
                os.rmdir(root)

        self.statusBar.showMessage(f'Deleted {count_deleted} files. Kept {count_kept} files.')

if __name__ == "__main__":
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec_()
