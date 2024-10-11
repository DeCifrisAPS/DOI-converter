#!/usr/bin/env python3
import os
import sys
import json
from PyQt5.QtWidgets import QWizard, QWizardPage
from PyQt5.QtWidgets import QLabel, QVBoxLayout, QPushButton, QGridLayout
from PyQt5.QtWidgets import QFileDialog, QApplication
from PyQt5.QtGui import QPixmap, QIcon
from PyQt5 import QtCore

from converter_site import ParserV10, read_raw_data

from converter_doi import convert_to_xml, save_xml_to_file

version = "10"

global_parser = ParserV10()

class ConverterWizard(QWizard):
    def __init__(self, parent=None):
        super(ConverterWizard, self).__init__(parent)
        self.setOption(QWizard.DisabledBackButtonOnLastPage)
        self.addPage(InputPage(self))
        self.addPage(ValidationPage(self))
        self.addPage(OutputPage(self))
        self.addPage(FinishPage(self))

        self.setPixmap(QWizard.LogoPixmap, # Classic or Modern
                QPixmap("./decifris_logo.jpg"))
        self.setWizardStyle(QWizard.ModernStyle)
        # ClassicStyle ModernStyle MacStyle AeroStyle

        self.setWindowTitle(f"DOI Converter {version}")
        self.resize(640, 480)

class InputPage(QWizardPage):
    def __init__(self, parent=None):
        super(InputPage, self).__init__(parent)
        self.setTitle("Convertitore da CSV in JSON")
        self.setSubTitle(f"Versione {version}")
        self.label1 = QLabel()
        layout = QVBoxLayout()
        layout.addWidget(self.label1)
        self.setLayout(layout)

    def initializePage(self):
        self.label1.setText("Questo programma serve a convertire"
            + " una tabella CSV (o TSV)"
            + " nel formato JSON per la generazione delle pagine sul sito"
            + " e nel formato XML (ONIX) per la generazione dei DOI.")
        self.label1.setWordWrap(True)

class ValidationPage(QWizardPage):
    pathChanged = QtCore.pyqtSignal()

    def __init__(self, parent=None):
        super(ValidationPage, self).__init__(parent)
        self.chosen_path = None
        self.pathChanged.connect(self.completeChanged)
        self.setTitle("Selezionare file da convertire")
        self.setSubTitle("Verrà anche validato il file prima di continuare")
        self.file_label = QLabel()
        self.selectFileButton = QPushButton("Browse")
        # self.selectFileButton.setIcon(QIcon("./logo.png"))
        self.selectFileButton.clicked.connect(self.chooseFile)
        self.message_label = QLabel()
        self.message_label.setWordWrap(True)
        gl = QGridLayout()
        gl.setRowStretch(1, 1)
        gl.addWidget(self.file_label, 0, 0)
        gl.addWidget(self.selectFileButton, 0, 1)
        gl.addWidget(self.message_label, 2, 0, 1, 2)
        self.setLayout(gl)

    def initializePage(self):
        self.file_label.setText("Select a file")

    def chooseFile(self):
        path = QFileDialog.getOpenFileName(self,
            "Open File", "./", "CSV Files (*.csv *.tsv)")
        self.chosen_path = path[0]
        self.wizard().input_file = self.chosen_path
        self.file_label.setText(self.chosen_path)
        self.pathChanged.emit()

    def check_file(self):
        raw_data = read_raw_data(self.chosen_path)
        ok, error_messages = global_parser.sanity_check(raw_data)
        if not error_messages:
            self.message_label.setText("OK: ready to continue")
        else:
            self.message_label.setText("Error(s)\n\n" + '\n'.join(error_messages))
        return ok

    def isComplete(self):
        return (self.chosen_path != None
            and os.path.isfile(self.chosen_path)
            and os.access(self.chosen_path, os.R_OK)
            and self.check_file())


class OutputPage(QWizardPage):
    pathChanged = QtCore.pyqtSignal()

    def __init__(self, parent=None):
        super(OutputPage, self).__init__(parent)
        self.chosen_path = None
        self.pathChanged.connect(self.completeChanged)
        self.setTitle("Selezionare file da generare")
        self.setSubTitle("Verranno creati o sovrascritti i file JSON e XML."
                        + " Selezionare il file JSON."
                        + " Il file XML verrà creato con lo stesso nome,"
                        + " ma estensione diversa.")
        self.file_label = QLabel()
        self.selectFileButton = QPushButton("Browse")
        self.selectFileButton.clicked.connect(self.chooseFile)
        gl = QGridLayout()
        gl.addWidget(self.file_label, 0, 0)
        gl.addWidget(self.selectFileButton, 0, 1)
        self.setLayout(gl)

    def initializePage(self):
        self.file_label.setText("Selezionare un file JSON")

    def chooseFile(self):
        path = QFileDialog.getSaveFileName(self,
            "Select destination", "./", "JSON Files (*.json)")
        self.chosen_path = path[0]
        if len(self.chosen_path.split('.json')) == 1:
            self.chosen_path += ".json"
        self.file_label.setText(self.chosen_path)
        self.pathChanged.emit()

    def isComplete(self):
        if self.chosen_path == None:
            return False
        fn = self.chosen_path
        dn = os.path.dirname(fn)
        # Either shall be able to write in directory
        # Or shall be able to write existing file
        return ((not os.path.exists(fn)
                    and os.path.isdir(dn)
                    and os.access(dn, os.W_OK))
                or (os.path.exists(fn)
                    and os.path.isfile(fn)
                    and os.access(fn, os.W_OK)))

    def validatePage(self):
        raw_data = read_raw_data(self.wizard().input_file)
        volume_data = global_parser.convert_data(raw_data)
        with open(self.chosen_path, "w") as ofile:
            json.dump(volume_data, ofile, ensure_ascii=False)
            try:
                filename_xml = self.chosen_path.split('.')[0] + '.xml'
                save_xml_to_file(filename_xml, convert_to_xml(volume_data))
            except Exception as e:
                print("Could not create XML file")
                print(e)
                return False
            return True
        return False

class FinishPage(QWizardPage):
    def __init__(self, parent=None):
        super(FinishPage, self).__init__(parent)
        self.setTitle("Operazione completata")
        self.setSubTitle("Il file è stato convertito con successo")
        layout = QVBoxLayout()
        self.setLayout(layout)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    wiz = ConverterWizard()
    wiz.show()
    wiz.setWindowIcon(QIcon("./logo.png"))
    sys.exit(app.exec())

