import sys
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, \
    QMessageBox, QDesktopWidget, QHBoxLayout, QVBoxLayout, QAction, QMainWindow
from PyQt5.QtGui import QIcon


# review = QLabel('Review')
# titleEdit = QLineEdit()

class MainWindow(QMainWindow):

    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)

        self.toolbar_init()

        self.main_screen = MainScreen(self)
        self.setCentralWidget(self.main_screen)

        self.resize(700, 700)
        self.setWindowTitle('Center')

    def toolbar_init(self):
        # Calibrate Gauge
        calibrate_act = QAction(QIcon('../icons/calibrate.png'), 'Calibrate Gauge', self)
        calibrate_act.setShortcut('Ctrl+1')

        toolbar = self.addToolBar('Calibrate')
        toolbar.addAction(calibrate_act)

        # Get Reading


class MainScreen(QWidget):

    def __init__(self, parent):
        super(MainScreen, self).__init__(parent)
        self.initUI()

    def initUI(self):

        # Buttons
        okButton = QPushButton("OK")
        cancelButton = QPushButton("Cancel")

        # Screen

        hbox = QHBoxLayout()
        hbox.addStretch(1)
        hbox.addWidget(okButton)
        hbox.addWidget(cancelButton)

        vbox = QVBoxLayout()
        vbox.addStretch(1)
        vbox.addLayout(hbox)

        self.setLayout(vbox)

        self.center()

    def center(self):

        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def closeEvent(self, event):

        reply = QMessageBox.question(self, 'Message',
                                     "Are you sure to quit?", QMessageBox.Yes |
                                     QMessageBox.No, QMessageBox.No)

        if reply == QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
