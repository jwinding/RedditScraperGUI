import os
from sys import exit
from PyQt5.QtCore import QItemSelection, Qt, pyqtSlot, QModelIndex
from .redditScraper import redditScraper
from .downloadThread import RedditDownloadThread
import configparser
from PyQt5.QtGui import QPalette, QPixmap, QIntValidator, QIcon
from PyQt5.QtWidgets import (QCheckBox, QScrollArea, QVBoxLayout, QWidget, QGridLayout, QLabel,
                             QPushButton,QAction,
                             QLineEdit, QMessageBox,
                             QFileDialog, QTextEdit,
                             QFileSystemModel, QTreeView,
                             QHBoxLayout, QMenuBar,
                             QComboBox, QSizePolicy)
MAX_IMAGE_HEIGHT = 1200
LOOKUP_LIMIT_MULTIPLIER = 3

class RedditScraperWindow(QWidget):
    """The main window of the program."""

    ########### Setup ##################################
    def __init__(self):
        super().__init__()

        self.read_user_config()
        self.load_assets()
        self.initialize_ui()

    def load_assets(self):
        script_folder = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        asset_folder = os.path.join(script_folder, "assets")
        if os.path.isdir(asset_folder):
            self.download_icon = QIcon(os.path.join(asset_folder, 'download_icon.png'))
            self.stop_icon = QIcon(os.path.join(asset_folder, 'stop_icon.png'))
            self.reddit_icon = QIcon(os.path.join(asset_folder, 'reddit_icon.png'))
        else:
            self.download_icon = QIcon(os.path.join("assets", 'download_icon.png'))
            self.stop_icon = QIcon(os.path.join("assets", 'stop_icon.png'))
            self.reddit_icon = QIcon(os.path.join("assets", 'reddit_icon.png'))        

    def initialize_ui(self):
        """sets up the user interface, connects all the signals and shows the window. """

        self.init_components()
        self.read_settings_config()
        self.connect_signals()

        self.setGeometry(100, 100, 1000, 800)
        self.setWindowTitle('Reddit Image Scraper')
        self.setWindowIcon(self.reddit_icon)

        self.show()

    def init_components(self):
        """initializes all components and sets up the layout"""
        internalWidgetInput = QWidget()
        internalWidgetTree = QWidget() 

        ############ define components ####################
        self.subredditInput = QComboBox()
        self.subredditInput.setEditable(True)
        self.subredditInput.addItems(self.get_downloaded_subreddits())


        self.numInput = QLineEdit()
        self.onlyInt = QIntValidator()
        self.numInput.setValidator(self.onlyInt)
        subredditLabel = QLabel('subreddit')
        numLabel = QLabel('number of images')
        self.dirLabel = QLabel('choose a directory')
        scale_label = QLabel("Scale images?")
        self.imgView = QLabel()

        self.outputText = QTextEdit('')
        self.outputText.setReadOnly(True)
        
        self.scale_cb = QCheckBox()

        self.sortingCb = QComboBox()
        self.sortingCb.addItems(["Hot", "Top all time",
                                 "Top this month", "Top past year",
                                 "New", "Controversial"])
        sortingLabel = QLabel('sorting method')
        self.runButton = QPushButton('Download')
        self.runButton.setIcon(self.download_icon)
        self.chooseDirButton = QPushButton('Save dir')
        self.stopButton = QPushButton('Stop')
        self.stopButton.setIcon(self.stop_icon)

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
        grid.addWidget(self.outputText,7,0,7,2)
        # grid.addWidget(self.tree,1,2, 11,7)

        grid.addWidget(scale_label, 6,0)
        grid.addWidget(self.scale_cb, 6, 1)

        hboxTree = QVBoxLayout()
        hboxTree.addWidget(self.tree)


        #the image viewer, setting how it behaves under resizing.
        self.imgView.setSizePolicy(QSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.MinimumExpanding))
        self.imgView.setMaximumHeight(MAX_IMAGE_HEIGHT)

        self.imgView.setAlignment(Qt.AlignmentFlag.AlignCenter)

        img_scroll_area = QScrollArea()
        img_scroll_area.setMinimumHeight(MAX_IMAGE_HEIGHT)
        img_scroll_area.setMinimumWidth(MAX_IMAGE_HEIGHT)
        img_scroll_area.setWidget(self.imgView)

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
        hbox.addWidget(img_scroll_area)
        self.setLayout(hbox)

    def connect_signals(self):
        """connects all the signals to the right functions"""
        self.chooseDirButton.clicked.connect(self.show_dir_dialog)
        self.runButton.clicked.connect(self.run_download_threaded)
        self.tree.clicked.connect(self.on_treeView_clicked)
        self.stopButton.clicked.connect(self.stop_download)
        self.scale_cb.clicked.connect(self.refresh_image)
        self.exit_action.triggered.connect(exit)

        #self.edit_login_action.triggered.connect(self.edit_login_info)
        self.help_action.triggered.connect(self.show_help)

        self.tree.selectionModel().selectionChanged.connect(self.on_selection_change)

    def read_user_config(self):
        """reads in the users username and password from the config file, or if there is no config file,
        shows an input dialog.
        Also tests so that only valid login information gets saved to the config file. """
        config = configparser.ConfigParser()
        self.redditScraper = redditScraper()
        if os.path.exists('redditScraper.ini'):
            config.read('redditScraper.ini')

            if 'DIR' in config:
                self.folder = config['DIR']['root_folder']

        else:
            config['REDDIT'] = {
                'subreddit': "wallpapers",
                'num': 10,
                'sorting': "Hot",
                'downloaded_subreddits': ""
            }


            with open('redditScraper.ini', 'w') as configfile:
                config.write(configfile)

        self.config=config

    def read_settings_config(self):
        """reads the saved settings from the config file, if they're there."""
        if 'DIR' in self.config:
            self.folder = self.config['DIR']['root_folder']
            idx = self.fileModel.setRootPath(str(self.folder))
            self.tree.setRootIndex(idx)
            self.dirLabel.setText(self.folder)

        if 'REDDIT' in self.config:
            self.subredditInput.setCurrentText(self.config['REDDIT']['subreddit'])
            self.numInput.setText(self.config['REDDIT']['num'])
            self.sortingCb.setCurrentText(self.config['REDDIT']['sorting'])




    ################### Actions: ##################
    @pyqtSlot(QModelIndex)
    def on_treeView_clicked(self, index):
        """triggers when the user clicks on a file item shown in the treeView, and shows that file in the picture viewer."""
        index = self.fileModel.index(index.row(),0,index.parent() )
        self.show_image(index)

    def on_selection_change(self, selected: QItemSelection, deselected: QItemSelection):
        """ Triggers when the selected item in the treeview changes, and updates the shown picture. """
        self.refresh_image()

    def refresh_image(self):
        selected_image_index = self.tree.selectedIndexes()[0]
        self.show_image(selected_image_index)

    def show_image(self, index: QModelIndex):
        filePath = self.fileModel.filePath(index)
        if os.path.isfile(filePath) and filePath.split(".")[-1] in ["jpg","gif","png","jpeg"]:
            pixmap=QPixmap(filePath)
            if self.scale_cb.isChecked():
                self.imgView.setFixedHeight(MAX_IMAGE_HEIGHT)
                scaled_img = pixmap.scaledToHeight(MAX_IMAGE_HEIGHT)
                self.imgView.setFixedWidth(scaled_img.width())
                self.imgView.setPixmap(scaled_img)
            else:
                self.imgView.setFixedHeight(pixmap.height())
                self.imgView.setFixedWidth(pixmap.width())
                self.imgView.setPixmap(pixmap)

    def show_dir_dialog(self):
        """lets the user select the root folder, and saves the choice to the config file."""

        self.folder =QFileDialog.getExistingDirectory(self,'Choose base directory','/home')
        self.dirLabel.setText(self.folder)

        self.config['DIR']={ 'root_folder' : self.folder }
        with open('redditScraper.ini', 'w') as configfile:
            self.config.write(configfile)

        idx = self.fileModel.setRootPath(self.folder)
        self.tree.setRootIndex(idx)


        return self.folder


    @pyqtSlot(str)
    def update_output_text(self, message:str):
        """updates the output text area, to show progress on downloads."""
        self.outputText.setText(message+self.outputText.toPlainText() )

    def save_subreddit(self, subreddit: str, num: int, sorting: str):
        """helper function to save the current settings to the config file."""
        downloaded_subreddits = self.get_downloaded_subreddits()
        if subreddit not in downloaded_subreddits:
            downloaded_subreddits.append(subreddit)
            self.subredditInput.addItem(subreddit)

        downloaded_subreddits = ','.join(downloaded_subreddits)
        self.config['REDDIT'] = {
            'subreddit': subreddit,
            'num': str(num),
            'sorting':sorting,
            'downloaded_subreddits': downloaded_subreddits
        }

        
        with open('redditScraper.ini', 'w') as configfile:
            self.config.write(configfile)

    def get_downloaded_subreddits(self) -> list:
        if 'downloaded_subreddits' in self.config['REDDIT'].keys():
            subreddits = self.config['REDDIT']['downloaded_subreddits'].split(',')
            return subreddits     
        return []

    def run_download_threaded(self):
        """downloads the pictures. Runs in a QThread, so that the program does not freeze.
        Also checks whether the specified subreddit exists. """
        subreddit = self.subredditInput.currentText()
        num = int(self.numInput.text())
        sorting = self.sortingCb.currentText()

        if self.redditScraper.sub_exists(subreddit):

            if not hasattr(self, "folder"):
                msgBox = QMessageBox()
                msgBox.setText('You need to set a download folder!')
                msgBox.setWindowTitle("Pick a download folder")
                msgBox.exec_()
                return


            self.save_subreddit(subreddit,num,sorting)
            self.get_thread = RedditDownloadThread(self.redditScraper, subreddit, num,
                                                    num*LOOKUP_LIMIT_MULTIPLIER,
                                                   sorting, self.folder)
            self.get_thread.changeText.connect(self.update_output_text)
            self.get_thread.start()
        else:
            msgBox = QMessageBox()
            msgBox.setText('That subreddit does not exist, please try again')
            msgBox.setWindowTitle("Invalid subreddit")
            msgBox.exec_()


        pass

    def stop_download(self):
        """Stops the download thread and prints a message to the output."""
        try:
            if self.get_thread.isRunning():
                self.get_thread.terminate()
                self.outputText.setText(self.outputText.toPlainText() + ' Aborted!\n')
        except Exception:
            pass

    ############### Menu actions: ###############
    

    def show_help(self):
        msgBox = QMessageBox()

        msgBox.setWindowIcon(self.reddit_icon)
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

