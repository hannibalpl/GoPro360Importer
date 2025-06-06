# main.py
from qgis.PyQt.QtWidgets import QAction, QFileDialog, QMessageBox
from qgis.core import QgsProject
import os

from .dialog import GoproCsvDialog

class GoPro360ImporterPlugin:
    def __init__(self, iface):
        self.iface = iface
        self.plugin_dir = os.path.dirname(__file__)
        self.toolbar = None
        self.dlg = None

    def initGui(self):
        self.action = QAction('Import GoPro 360', self.iface.mainWindow())
        self.action.triggered.connect(self.show_dialog)

        # Add to Plugins menu
        self.iface.addPluginToMenu('GoPro360 Importer', self.action)

        # Add toolbar
        self.toolbar = self.iface.addToolBar('GoPro360Importer')
        self.toolbar.addAction(self.action)

    def unload(self):
        if self.toolbar:
            self.toolbar.removeAction(self.action)
        self.iface.removePluginMenu('GoPro360 Importer', self.action)

    def show_dialog(self):
        if not self.dlg:
            self.dlg = GoproCsvDialog(self.iface)
        self.dlg.show()
