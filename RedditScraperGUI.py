import os
import datetime
from PyQt5.QtCore import QItemSelection, Qt, QThread, pyqtSignal, pyqtSlot, QModelIndex
import redditScraper
from loginWindow import LoginInfoWindow
import configparser
from PyQt5.QtGui import QPixmap, QIntValidator, QIcon
from PyQt5.QtWidgets import (QWidget, QGridLayout, QLabel,
                             QPushButton,QAction,
                             QLineEdit, QMessageBox,
                             QFileDialog, QTextEdit,
                             QFileSystemModel, QTreeView,
                             QHBoxLayout, QMenuBar,
                             QComboBox, QSizePolicy)
MAX_IMAGE_HEIGHT = 1200

class RedditScraperWindow(QWidget):
    """The main window of the program."""

    ########### Setup ##################################
    def __init__(self):
        super().__init__()

        self.readUserConfig()
        self.initUI()

    def initUI(self):
        """sets up the user interface, connects all the signals and shows the window. """

        self.init_components()
        self.readSettingsConfig()
        self.connect_signals()

        self.setGeometry(100, 100, 1000, 800)
        self.setWindowTitle('Reddit Image Scraper')
        self.setWindowIcon(QIcon('redditIcon.png'))

        self.show()

    def init_components(self):
        """initializes all components and sets up the layout"""
        internalWidgetInput = QWidget()
        internalWidgetTree = QWidget() 

        ############ define components ####################
        self.subredditInput = QLineEdit()
        self.numInput = QLineEdit()
        self.onlyInt = QIntValidator()
        self.numInput.setValidator(self.onlyInt)
        subredditLabel = QLabel('subreddit')
        numLabel = QLabel('number of images')
        self.dirLabel = QLabel('base download dir')

        self.imgView = QLabel()

        self.outputText = QTextEdit('')
        self.outputText.setReadOnly(True)

        self.sortingCb = QComboBox()
        self.sortingCb.addItems(["Hot", "Top all time",
                                 "Top this month", "Top past year",
                                 "New", "Controversial"])
        sortingLabel = QLabel('sorting method')
        self.runButton = QPushButton('Download')
        self.chooseDirButton = QPushButton('download dir')
        self.stopButton = QPushButton('Stop')

        self.fileModel = QFileSystemModel()
        self.tree = QTreeView()

        self.tree.setModel(self.fileModel)
        self.tree.setColumnHidden(1, True)
        self.tree.setColumnHidden(2, True)
        self.tree.setColumnHidden(3, True)


        ############## Menu stuff ###################
        menu_bar = QMenuBar()
        file_menu = menu_bar.addMenu('File')
        help_menu = menu_bar.addMenu('Help')
        self.edit_login_action = QAction('Edit reddit login', self)
        file_menu.addAction(self.edit_login_action)

        self.exit_action = QAction('Exit', self)

        file_menu.addAction(self.exit_action)
        self.help_action = QAction('Help', self)
        help_menu.addAction(self.help_action)
        menu_bar.setFixedHeight(30)
        

        ############# Setup the grid layout###############################
        grid = QGridLayout()
        # grid.addWidget(menu_bar, 1, 0, 1, 4)
        grid.setSpacing(4)
        grid.addWidget(subredditLabel, 1,0)
        grid.addWidget(self.subredditInput, 1,1)
        grid.addWidget(numLabel, 2,0)
        grid.addWidget(self.numInput,2,1)
        grid.addWidget(sortingLabel, 3,0)
        grid.addWidget(self.sortingCb,3,1)

        grid.addWidget(self.chooseDirButton,4,0)
        grid.addWidget(self.dirLabel,4,1)
        grid.addWidget(self.stopButton,5,0)
        grid.addWidget(self.runButton,5,1)
        grid.addWidget(self.outputText,6,0,6,2)
        # grid.addWidget(self.tree,1,2, 11,7)

        hboxTree = QHBoxLayout()
        hboxTree.addWidget(self.tree)

        #the image viewer, setting how it behaves under resizing.
        self.imgView.setSizePolicy(QSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.MinimumExpanding))
        self.imgView.setMaximumHeight(MAX_IMAGE_HEIGHT)

        self.imgView.setAlignment(Qt.AlignmentFlag.AlignCenter)

        internalWidgetInput.setLayout(grid)
        # internalWidgetInput.setMinimumWidth(300)
        internalWidgetInput.setFixedWidth(300)
        internalWidgetInput.setSizePolicy(QSizePolicy(QSizePolicy.Fixed, QSizePolicy.MinimumExpanding))

        internalWidgetTree.setLayout(hboxTree)
        internalWidgetTree.setFixedWidth(360)
        internalWidgetTree.setSizePolicy(QSizePolicy(QSizePolicy.Fixed, QSizePolicy.MinimumExpanding))

        #construct layout of main window. 
        hbox = QHBoxLayout()
        hbox.setSpacing(0)
        hbox.setContentsMargins(0,0,0,0)
        hbox.setMenuBar(menu_bar)
        hbox.addWidget(internalWidgetInput)
        hbox.addWidget(internalWidgetTree)
        hbox.addWidget(self.imgView)
        self.setLayout(hbox)

    def connect_signals(self):
        """connects all the signals to the right functions"""
        self.chooseDirButton.clicked.connect(self.showDirDialog)
        self.runButton.clicked.connect(self.runDownloadThreaded)
        self.tree.clicked.connect(self.on_treeView_clicked)
        self.stopButton.clicked.connect(self.stopDownload)

        self.exit_action.triggered.connect(exit)

        self.edit_login_action.triggered.connect(self.edit_login_info)
        self.help_action.triggered.connect(self.helpClicked)

        self.tree.selectionModel().selectionChanged.connect(self.on_selection_change)

    def readUserConfig(self):
        """reads in the users username and password from the config file, or if there is no config file,
        shows an input dialog.
        Also tests so that only valid login information gets saved to the config file. """
        config = configparser.ConfigParser()

        if os.path.exists('redditScraper.ini'):
            config.read('redditScraper.ini')

            self.username = config['USER']['username']
            self.password = config['USER']['password']
            self.redditScraper = redditScraper.redditScraper(self.username,
                                                             self.password)
            if 'DIR' in config:
                self.folder = config['DIR']['root_folder']

        else:
            while True:
                LoginInfoWindow(self)
                self.redditScraper = redditScraper.redditScraper(self.username,
                                                                 self.password)
                if self.redditScraper.valid_login():
                    break
                else:
                    msgBox = QMessageBox()
                    msgBox.setText('Please provide a valid username and password.')
                    msgBox.setWindowTitle("Invalid information")
                    msgBox.exec_()



            config['USER'] = {
                'username' : self.username,
                'password' : self.password
            }

            with open('redditScraper.ini', 'w') as configfile:
                config.write(configfile)

        self.config=config

    def readSettingsConfig(self):
        """reads the saved settings from the config file, if they're there."""
        if 'DIR' in self.config:
            self.folder = self.config['DIR']['root_folder']
            idx = self.fileModel.setRootPath(str(self.folder))
            self.tree.setRootIndex(idx)
            self.dirLabel.setText(self.folder)

        if 'REDDIT' in self.config:
            self.subredditInput.setText(self.config['REDDIT']['subreddit'])
            self.numInput.setText(self.config['REDDIT']['num'])
            self.sortingCb.setCurrentText(self.config['REDDIT']['sorting'])




    ################### Actions: ##################
    @pyqtSlot(QModelIndex)
    def on_treeView_clicked(self, index):
        """triggers when the user clicks on a file item shown in the treeView, and shows that file in the picture viewer."""

        indexItem = self.fileModel.index(index.row(),0,index.parent() )
        filePath = self.fileModel.filePath(indexItem)
        pixmap=QPixmap(filePath)
        height = self.imgView.geometry().height()
        self.imgView.setPixmap(pixmap.scaledToHeight(height))

    def on_selection_change(self, selected: QItemSelection, deselected: QItemSelection):
        """ Triggers when the selected item in the treeview changes, and updates the shown picture. """
        selected_image_index = self.tree.selectedIndexes()[0]
        filePath = self.fileModel.filePath(selected_image_index)
        pixmap=QPixmap(filePath)
        height = self.imgView.geometry().height()
        self.imgView.setPixmap(pixmap.scaledToHeight(height))


    def showDirDialog(self):
        """lets the user select the root folder, and saves the choice to the config file."""

        self.folder =QFileDialog.getExistingDirectory(self,'Choose base directory','/home')
        self.dirLabel.setText(self.folder)

        self.config['DIR']={ 'root_folder' : self.folder }
        with open('redditScraper.ini', 'w') as configfile:
            self.config.write(configfile)

        idx= self.fileModel.setRootPath(self.folder)
        self.tree.setRootIndex(idx)


        return self.folder


    @pyqtSlot(str)
    def update_output_text(self, message:str):
        """updates the output text area, to show progress on downloads."""
        self.outputText.setText(message+self.outputText.toPlainText() )

    def saveSubreddit(self, subreddit, num, sorting):
        """helper function to save the current settings to the config file."""
        self.config['REDDIT'] = {
            'subreddit': subreddit,
            'num': str(num),
            'sorting':sorting
        }
        with open('redditScraper.ini', 'w') as configfile:
            self.config.write(configfile)

    def runDownloadThreaded(self):
        """downloads the pictures. Runs in a QThread, so that the program does not freeze.
        Also checks whether the specified subreddit exists. """
        subreddit = self.subredditInput.text()
        num = int(self.numInput.text())
        sorting = self.sortingCb.currentText()

        if self.redditScraper.sub_exists(subreddit):
            self.saveSubreddit(subreddit,num,sorting)
            self.get_thread = RedditDownloadThread(self.redditScraper, subreddit, num,
                                                   sorting, self.folder)
            self.get_thread.changeText.connect(self.update_output_text)
            self.get_thread.start()
        else:
            msgBox = QMessageBox()
            msgBox.setText('That subreddit does not exist, please try again')
            msgBox.setWindowTitle("Invalid subreddit")
            msgBox.exec_()


        pass

    def stopDownload(self):
        """Stops the download thread and prints a message to the output."""
        if self.get_thread.isRunning():
            self.get_thread.terminate()
            self.outputText.setText(self.outputText.toPlainText() + ' Aborted!\n')
        pass

    ############### Menu actions: ###############
    def edit_login_info(self):
        """let's the user change the reddit login information. Checks so that only valid logins gets saved
        to the config file. """
        while True:
            LoginInfoWindow(self)
            self.redditScraper = redditScraper.redditScraper(self.username,
                                                             self.password)
            if self.redditScraper.valid_login():
                break
            else:
                msgBox = QMessageBox()
                msgBox.setText('Please provide a valid username and password.')
                msgBox.setWindowTitle("Invalid information")
                msgBox.exec_()

        self.config['USER'] = {
            'username': self.username,
            'password': self.password
        }

        with open('redditScraper.ini', 'w') as configfile:
            self.config.write(configfile)

    def helpClicked(self):
        msgBox = QMessageBox()

        msgBox.setWindowIcon(QIcon('redditIcon.png'))
        msgBox.setText('This program downloads images posted to reddit.com, or more specifically, to subreddits' +
                       '(i.e. sub-forums). To use it, one needs a valid reddit account, which one can sign up for ' +
                       'on reddit.com. One also needs to know some names of subreddits. \n Some suggestions for subreddits: ' +
                       'wallpapers , earthporn , nature , and pics . \n \n '
                       + "This program will download up to the specified number of images. It can handle png, jpg and gif,"
                        +  "so links to gyf-files, videos or anything else will be ignored. Therefore the number of images actually "
                         +"downloaded will usually be less than the specified number. So if you want a lot of images, just put"
                       + " a large limit.\n The images will be placed in a subfolder of the chosen base folder, named after the subreddit. This folder will be created if it does not exist.\n \n "
                        + "To view the images, click on them in the tree-view, and they will appear on the right" )
        msgBox.setWindowTitle("Help")
        msgBox.exec_()


class RedditDownloadThread(QThread):
    """Defines the thread that runs the download."""

    changeText = pyqtSignal(str)

    def __init__(self, redditInstance, sub: str, num: int, sort: str, base_folder:str):
        QThread.__init__(self)
        self.reddit=redditInstance
        self.subreddit = sub
        self.num = num
        self.sorting = sort
        self.base_folder=base_folder

        # self.changeText = pyqtSignal(str)

    def __del__(self):
        self.wait()

    def run(self):
        """Runs the actual download, using various helper functions from the redditScraper class."""
        self.changeText.emit('Downloading ...\n ------------------------------------------ \n')
        img_urls = self.reddit.get_image_urls(self.subreddit, self.sorting, self.num)
        folder = os.path.join(self.base_folder, self.subreddit)
        date = str(datetime.datetime.now().date())

        self.changeText.emit( '\n'+ str(len(img_urls)) + ' images from /r/' + self.subreddit + ', sorted by ' + self.sorting + '\n')

        for i, url in enumerate(img_urls):
            filename = date +' '+self.sorting + ' ' + str(i + 1)
            self.reddit.download_image(url, filename, folder)
            self.changeText.emit(str(i+1) + ' ')
            self.msleep(500)


        self.changeText.emit("Finished! \n")
