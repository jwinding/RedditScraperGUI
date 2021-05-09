import os
import datetime
from PyQt5.QtCore import QThread, pyqtSignal

class RedditDownloadThread(QThread):
    """Defines the thread that runs the download."""

    changeText = pyqtSignal(str)

    def __init__(self, redditInstance, sub: str, num: int, limit:int, sort: str, base_folder:str):
        QThread.__init__(self)
        self.reddit = redditInstance
        self.subreddit = sub
        self.num = num
        self.limit = limit
        self.sorting = sort
        self.base_folder = base_folder

    def __del__(self):
        self.wait()

    def run(self):
        """Runs the actual download, using various helper functions from the redditScraper class."""
        self.changeText.emit('Downloading ...\n ------------------------------------------ \n')
        img_urls = self.reddit.get_image_urls(self.subreddit, self.sorting, self.num, self.limit)
        folder = os.path.join(self.base_folder, self.subreddit)
        date = str(datetime.datetime.now().date())

        self.changeText.emit( '\n'+ str(len(img_urls)) + ' images from /r/' + self.subreddit + ', sorted by ' + self.sorting + '\n')

        for i, url in enumerate(img_urls):
            filename = date +' '+self.sorting + ' ' + str(i + 1)
            self.reddit.download_image(url, filename, folder)
            self.changeText.emit(str(i+1) + ' ')
            self.msleep(500)
        if len(img_urls) == 0:
            self.changeText.emit('Searched {} posts, but could not find any images.\nPerhaps try a different subreddit?\n'.format(self.limit))
        elif len(img_urls) < self.num:
            self.changeText.emit('Searched {} posts, but could only find {} images...\n'.format(self.limit, len(img_urls)))

        self.changeText.emit("Finished! \n")