import sys
from RedditScraperGUI import RedditScraperWindow
from PyQt5.QtWidgets import QApplication

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = RedditScraperWindow()
    sys.exit(app.exec_())