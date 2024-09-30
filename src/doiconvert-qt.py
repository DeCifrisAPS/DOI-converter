#!/usr/bin/env python3
import os
import sys
import json
from PyQt5.QtWidgets import QWizard, QWizardPage
from PyQt5.QtWidgets import QLabel, QVBoxLayout, QPushButton, QGridLayout
from PyQt5.QtWidgets import QFileDialog, QApplication
from PyQt5.QtGui import QPixmap, QIcon
from PyQt5 import QtCore

from converter import ParserV10, read_raw_data

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

        # self.setPixmap(QWizard.BackgroundPixmap, # MacStyle
        #         QPixmap("./decifris_background.jpeg"))
        # self.setPixmap(QWizard.WatermarkPixmap, # Classic or Modern
        #         QPixmap("./decifris_background.jpeg"))
        # self.setPixmap(QWizard.BannerPixmap, # Classic or Modern
        #         QPixmap("./logo.png"))
        self.setWizardStyle(QWizard.ModernStyle)
        # ClassicStyle ModernStyle MacStyle AeroStyle

        self.setWindowTitle(f"DOI Converter {version}")
        self.resize(640, 480)

class InputPage(QWizardPage):
    def __init__(self, parent=None):
        super(InputPage, self).__init__(parent)
        self.setTitle("Hello there")
        self.setPixmap(QWizard.LogoPixmap, # Classic or Modern
                QPixmap("./logo.png"))
        self.label1 = QLabel()
        layout = QVBoxLayout()
        layout.addWidget(self.label1)
        self.setLayout(layout)

    def initializePage(self):
        self.label1.setText("Hello there")

class ValidationPage(QWizardPage):
    pathChanged = QtCore.pyqtSignal()

    def __init__(self, parent=None):
        super(ValidationPage, self).__init__(parent)
        self.chosen_path = None
        self.pathChanged.connect(self.completeChanged)
        self.label1 = QLabel()
        self.file_label = QLabel()
        self.selectFileButton = QPushButton("Browse")
        # self.selectFileButton.setIcon(QIcon("./logo.png"))
        self.selectFileButton.clicked.connect(self.chooseFile)
        self.message_label = QLabel()
        self.message_label.setWordWrap(True)
        gl = QGridLayout()
        gl.setRowStretch(2, 1)
        gl.addWidget(self.label1, 0, 0, 1, 2)
        gl.addWidget(self.file_label, 1, 0)
        gl.addWidget(self.selectFileButton, 1, 1)
        gl.addWidget(self.message_label, 3, 0, 1, 2)
        self.setLayout(gl)

    def initializePage(self):
        self.label1.setText("Select input file")
        self.file_label.setText("Select a file")

    def chooseFile(self):
        path = QFileDialog.getOpenFileName(self,
            "Open File", "./", "CSV Files (*.csv)")
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
        self.label1 = QLabel()
        self.file_label = QLabel()
        self.selectFileButton = QPushButton("Browse")
        self.selectFileButton.clicked.connect(self.chooseFile)
        gl = QGridLayout()
        gl.addWidget(self.label1, 0, 0, 1, 2)
        gl.addWidget(self.file_label, 1, 0)
        gl.addWidget(self.selectFileButton, 1, 1)
        self.setLayout(gl)

    def initializePage(self):
        self.label1.setText("Select output")
        self.file_label.setText("Select a file")

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
        converted = global_parser.convert_data(raw_data)
        with open(self.chosen_path, "w") as ofile:
            json.dump(converted, ofile, ensure_ascii=False)
            return True
        return False

class FinishPage(QWizardPage):
    def __init__(self, parent=None):
        super(FinishPage, self).__init__(parent)
        self.label1 = QLabel()
        layout = QVBoxLayout()
        layout.addWidget(self.label1)
        self.setLayout(layout)

    def initializePage(self):
        self.label1.setText("Conclusion")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    wiz = ConverterWizard()
    wiz.show()
    wiz.setWindowIcon(QIcon("./logo.png"))
    sys.exit(app.exec())

