from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog, QGridLayout, QPushButton, QWidget, QComboBox, QLabel
import os
import sys

class Renamer(QMainWindow):
  def __init__(self):
    super().__init__()
    self.initUI()

  def initUI(self):
    self.setWindowTitle("VoidRenamer")
    self.resize(320, 120)
    self.setMinimumSize(320, 120)
    self.setMaximumSize(320, 120)
    centralWidget = QWidget()
    self.layout = QGridLayout(centralWidget)

    self.label_source = QLabel('Source')
    self.label_target = QLabel('Target')
    self.layout.addWidget(self.label_source, 0, 0)
    self.layout.addWidget(self.label_target, 0, 1)

    self.combo_source = QComboBox(self)
    self.combo_target = QComboBox(self)

    self.languages = {
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

    for code, language in self.languages.items():
      self.combo_source.addItem(f"{code} - {language}", code)
      self.combo_target.addItem(f"{code} - {language}", code)

    self.layout.addWidget(self.combo_source, 1, 0)
    self.layout.addWidget(self.combo_target, 1, 1)

    self.btn_select_folder = QPushButton('Select Folder', self)
    self.btn_rename_files = QPushButton('Start', self)
    self.layout.addWidget(self.btn_select_folder, 2, 0)
    self.layout.addWidget(self.btn_rename_files, 2, 1)

    self.setCentralWidget(centralWidget)
    self.btn_select_folder.clicked.connect(self.open_folder_dialog)
    self.btn_rename_files.clicked.connect(self.rename_files)
    self.status_bar = self.statusBar()
    self.show()

  def open_folder_dialog(self):
    self.folder_path = QFileDialog.getExistingDirectory(self, 'Select Folder')
    if self.folder_path:
      folder_name = os.path.basename(self.folder_path)
      self.status_bar.showMessage(f"Selected folder: {folder_name}")

  def rename_files(self):
    source_lang = self.combo_source.currentData()
    target_lang = self.combo_target.currentData()
    self.file_count = 0
    for root, dirs, files in os.walk(self.folder_path):
      for name in files:
        if source_lang in name:
          old_name = os.path.join(root, name)
          new_name = old_name.replace(source_lang, target_lang)
          os.rename(old_name, new_name)
          self.file_count += 1
          self.status_bar.showMessage(f"Processed files: {self.file_count}")

if __name__ == "__main__":
  app = QApplication(sys.argv)
  renamer = Renamer()
  sys.exit(app.exec_())

