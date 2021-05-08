
import sys
from PyQt5.QtWidgets import (QGridLayout, QLabel,
                             QPushButton,QAction,
                             QLineEdit, QMessageBox,
                             QDialog)

class LoginInfoWindow(QDialog):
    """An input form to get the users reddit login information."""
    def __init__(self, parent):
        super().__init__()
        self.parent = parent

        self.initUI()

    def initUI(self):
        # define components
        nameInput = QLineEdit()
        passwordInput = QLineEdit()
        infoLabel = QLabel('To use the scraper, you need to have a valid reddit account.')
        nameLabel = QLabel('username')
        passwordLabel = QLabel('password')


        self.nameInput=nameInput
        self.passwordInput=passwordInput

        submitButton = QPushButton('Submit')
        exitButton = QPushButton('Quit')

        # setup the grid layout
        grid = QGridLayout()
        grid.setSpacing(4)
        grid.addWidget(infoLabel, 1, 0, 1,2)
        grid.addWidget(nameLabel, 2, 0)
        grid.addWidget(nameInput, 2, 1)
        grid.addWidget(passwordLabel, 3, 0)
        grid.addWidget(passwordInput, 3, 1)
        grid.addWidget(submitButton,4,0)
        grid.addWidget(exitButton, 4,1)

        self.setLayout(grid)



        submitButton.clicked.connect(self.submitData)
        exitButton.clicked.connect(self.closeOrExit)

        self.setGeometry(100, 300, 400, 170)
        self.setWindowTitle('Reddit Image Scraper')
        self.exec()

    def submitData(self):
        if self.nameInput.text() and self.passwordInput.text():
            self.parent.username = self.nameInput.text()
            self.parent.password = self.passwordInput.text()
            self.close()
        else:
            msgBox = QMessageBox()
            msgBox.setText('Please provide a valid username and password.')
            msgBox.setWindowTitle("Invalid information")
            msgBox.exec_()
        pass

    def closeOrExit(self):
        if 'USER' in self.parent.config:
            self.close()
        else:
            sys.exit()