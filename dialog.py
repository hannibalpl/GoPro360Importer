# dialog.py
from qgis.PyQt.QtWidgets import QDialog, QFileDialog, QMessageBox
from qgis.PyQt.QtCore import QCoreApplication
from qgis.PyQt.uic import loadUi
import os
from .processing import process_gopro_360_video

class GoproCsvDialog(QDialog):
    def __init__(self, iface):
        super().__init__()
        ui_path = os.path.join(os.path.dirname(__file__), 'ui', 'gopro_csv_dialog.ui')
        loadUi(ui_path, self)
        self.iface = iface

        # Połączenia przycisków
        self.videoBrowseButton.clicked.connect(self.browse_video_file)
        self.outputBrowseButton.clicked.connect(self.browse_output_folder)
        self.runButton.clicked.connect(self.run_processing)

        # Przypisanie domyślnej wartości dla pola odległości
        self.distanceSpinBox.setMinimum(1.0)
        self.distanceSpinBox.setValue(10.0)

    def log(self, message):
        self.logOutput.appendPlainText(message)
        QCoreApplication.processEvents()

    def browse_video_file(self):
        path, _ = QFileDialog.getOpenFileName(self, "Wybierz plik .360", '', "GoPro 360 (*.360)")
        if path:
            self.videoLineEdit.setText(path)

    def browse_output_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Wybierz folder wyjściowy", '')
        if folder:
            self.outputLineEdit.setText(folder)

    def run_processing(self):
        video_path = self.videoLineEdit.text().strip()
        output_folder = self.outputLineEdit.text().strip()
        distance = float(self.distanceSpinBox.value())

        if not os.path.isfile(video_path):
            QMessageBox.warning(self, "Brak wideo", "Wybierz poprawny plik wideo .360.")
            return
        if not os.path.isdir(output_folder):
            QMessageBox.warning(self, "Brak folderu", "Wybierz istniejący folder wyjściowy.")
            return

        try:
            # Wywołujemy pipeline zawsze z log_widget, by w okienku pojawiały się logi
            gpkg_path = process_gopro_360_video(video_path, output_folder, distance,log_widget=self.log)
            #gpkg_path = process_video_with_csv(video_path, output_folder, distance,log_widget=self.log)
            reply = QMessageBox.question(self, "Import ukończony","Dodać warstwę do projektu?",QMessageBox.Yes | QMessageBox.No)
            if reply == QMessageBox.Yes:self.iface.addVectorLayer(gpkg_path, os.path.basename(gpkg_path), 'ogr')

        except Exception as e:
            QMessageBox.critical(self, "Błąd", f"Wystąpił błąd:\n{str(e)}")
