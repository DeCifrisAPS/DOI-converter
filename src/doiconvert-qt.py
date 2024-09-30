#!/usr/bin/env python3
import os
import sys
import json
from PyQt5 import QtWidgets
from PyQt5 import QtCore

from converter import ParserV10, read_raw_data

global_parser = ParserV10()

class ConverterWizard(QtWidgets.QWizard):
    def __init__(self, parent=None):
        super(ConverterWizard, self).__init__(parent)
        self.addPage(InputPage(self))
        self.addPage(ValidationPage(self))
        self.addPage(OutputPage(self))
        self.addPage(FinishPage(self))
        self.setWindowTitle("PyQt5 Wizard")
        self.resize(640, 480)

class InputPage(QtWidgets.QWizardPage):
    def __init__(self, parent=None):
        super(InputPage, self).__init__(parent)
        self.label1 = QtWidgets.QLabel()
        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self.label1)
        self.setLayout(layout)

    def initializePage(self):
        self.label1.setText("Hello there")

class ValidationPage(QtWidgets.QWizardPage):
    pathChanged = QtCore.pyqtSignal()

    def __init__(self, parent=None):
        super(ValidationPage, self).__init__(parent)
        self.chosen_path = None
        self.pathChanged.connect(self.completeChanged)
        self.label1 = QtWidgets.QLabel()
        self.file_label = QtWidgets.QLabel()
        self.selectFileButton = QtWidgets.QPushButton("Browse")
        self.selectFileButton.clicked.connect(self.chooseFile)
        self.message_label = QtWidgets.QLabel()
        gl = QtWidgets.QGridLayout()
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
        path = QtWidgets.QFileDialog.getOpenFileName(self,
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


class OutputPage(QtWidgets.QWizardPage):
    pathChanged = QtCore.pyqtSignal()

    def __init__(self, parent=None):
        super(OutputPage, self).__init__(parent)
        self.chosen_path = None
        self.pathChanged.connect(self.completeChanged)
        self.label1 = QtWidgets.QLabel()
        self.file_label = QtWidgets.QLabel()
        self.selectFileButton = QtWidgets.QPushButton("Browse")
        self.selectFileButton.clicked.connect(self.chooseFile)
        gl = QtWidgets.QGridLayout()
        gl.addWidget(self.label1, 0, 0, 1, 2)
        gl.addWidget(self.file_label, 1, 0)
        gl.addWidget(self.selectFileButton, 1, 1)
        self.setLayout(gl)

    def initializePage(self):
        self.label1.setText("Select output")
        self.file_label.setText("Select a file")

    def chooseFile(self):
        path = QtWidgets.QFileDialog.getSaveFileName(self,
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

class FinishPage(QtWidgets.QWizardPage):
    def __init__(self, parent=None):
        super(FinishPage, self).__init__(parent)
        self.label1 = QtWidgets.QLabel()
        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self.label1)
        self.setLayout(layout)

    def initializePage(self):
        self.label1.setText("Conclusion")


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    wiz = ConverterWizard()
    wiz.show()
    sys.exit(app.exec())

