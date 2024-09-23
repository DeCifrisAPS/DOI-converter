#!/usr/bin/env python3
from PyQt5 import QtWidgets

class ConverterWizard(QtWidgets.QWizard):
    def __init__(self, parent=None):
        super(ConverterWizard, self).__init__(parent)
        self.addPage(InputPage(self))
        self.addPage(ValidationPage(self))
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
    def __init__(self, parent=None):
        super(ValidationPage, self).__init__(parent)
        self.label1 = QtWidgets.QLabel()
        self.fileLabel = QtWidgets.QLabel()
        self.selectFileButton = QtWidgets.QPushButton("Browse")
        self.selectFileButton.clicked.connect(self.chooseFile)
        gl = QtWidgets.QGridLayout()
        gl.addWidget(self.label1, 0, 0, 1, 2)
        gl.addWidget(self.fileLabel, 1, 0)
        gl.addWidget(self.selectFileButton, 1, 1)
        self.setLayout(gl)

    def initializePage(self):
        self.label1.setText("Page two")
        self.fileLabel.setText("Select a file")

    def chooseFile(self):
        path = QtWidgets.QFileDialog.getOpenFileName(self,
            "Open Image", "./", "CSV Files (*.csv)")
        print(path)


if __name__ == '__main__':
    import sys
    app = QtWidgets.QApplication(sys.argv)
    wiz= ConverterWizard()
    wiz.show()
    sys.exit(app.exec())

