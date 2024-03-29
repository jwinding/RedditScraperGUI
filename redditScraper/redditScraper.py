#reddit image scraper2, using praw

import os, sys
import requests
import praw
from prawcore import NotFound, OAuthException

try:
    import redditScraper.reddit_secrets as secrets
except ImportError:
    print("You need to setup the reddit_secrets.py file with your reddit information!")
    sys.exit(1)

class redditScraper:
    """Utility class that interfaces with PRAW, the python bindings for the reddit api."""
    def __init__(self):
        self.reddit = praw.Reddit(client_id = secrets.client_id,
                         client_secret = secrets.client_secret,
                         user_agent = secrets.user_agent,
                        check_for_updates=False,
                        comment_kind="t1",
                        message_kind="t4",
                        redditor_kind="t2",
                        submission_kind="t3",
                        subreddit_kind="t5",
                        trophy_kind="t6",
                        oauth_url="https://oauth.reddit.com",
                        reddit_url="https://www.reddit.com",
                        short_url="https://redd.it",
                        ratelimit_seconds=5,
                        timeout=16,
                    )

        #dictionary for switching between the sorting options:
        self.sorting_options = {"Top all time": self.top_all_posts,
                           "Top this month": self.top_month_posts,
                            "Top past year":self.top_year_posts,
                            "New": self.new_posts,
                            "Controversial": self.controversial_posts,
                           "Hot": self.hot_posts }


###### All the various options for sorting ############
    def controversial_posts(self, sub:str, num:int):
        subreddit=self.reddit.subreddit(sub)
        return subreddit.controversial(limit=num)
    def new_posts(self, sub:str, num:int):
        subreddit=self.reddit.subreddit(sub)
        return subreddit.new(limit=num)
    def top_year_posts(self, sub:str, num:int):
        subreddit=self.reddit.subreddit(sub)
        return subreddit.top(limit=num,time_filter='year')
    def top_all_posts(self, sub:str, num:int):
        subreddit=self.reddit.subreddit(sub)
        return subreddit.top(limit=num)
    def top_month_posts(self,sub:str, num:int):
        subreddit=self.reddit.subreddit(sub)
        return subreddit.top(time_filter='month', limit=num)
    def hot_posts(self,sub:str, num:int):
        subreddit=self.reddit.subreddit(sub)
        return subreddit.hot( limit = num)
#######################################################
    def sub_exists(self, sub:str) -> bool:
        """Tests if a given subreddit exists."""
        exists = True
        try:
            self.reddit.subreddits.search_by_name(sub, exact=True)
        except NotFound:
            exists = False
        return exists
    def valid_login(self)-> bool:
        """Tests if the provided login information works for logging into reddit."""
        try:
            next(self.reddit.subreddit('news').hot())
        except OAuthException:
            return False
        return True

    def handle_imgur_links(self, imgur_link: str) -> str:
        """A way of extracting the image from an imgur link, which works most of the time.
        A more proper way would be to use imgur API, but for now I'm too lazy. """
        l = imgur_link.split('/')
        return '/'.join([x if x != 'imgur.com' else 'i.imgur.com' for x in l]) + '.jpg'

    def get_image_urls(self, sub: str, sorting:str, num: int, limit: int)-> list :
        """returns a list of up to num links to images."""
        posts = self.sorting_options[sorting](sub, limit)

        urls = [x.url for x in posts]

        image_urls = []
        for i in range(len(urls)):
            if len(image_urls) >= num: break

            if urls[i][-4:] == '.jpg' or urls[i][-4:] == '.png' or urls[i][-4:] == '.gif':
                image_urls.append(urls[i])
            elif 'imgur.com' in urls[i].split('/'):
                image_urls.append(self.handle_imgur_links(urls[i]))
        return image_urls

    def download_image(self, url: str, filename: str, folder: str):
        """Downloads the image, saves it as 'filename'+('.jpg' or '.png'), in the specified folder"""
        if not os.path.exists(folder):
            os.makedirs(folder)
        if url[-4:] == '.jpg' or url[-4:] == '.png' or url[-4:] == '.gif':
            try:
                img_data = requests.get(url).content
                with open(folder + '\\' + filename + url[-4:], 'wb') as handler:
                    handler.write(img_data)
            except Exception as e:
                print("Failed to download {}".format(url))
                print("Exception: {}".format(e))

    def download_images_print(self, sub: str, sorting:str, num: int, limit:int, base_folder:str):
        """Downloads the selected images into base_folder/subreddit.
        Can be used in the console to test that this redditScraper class works as intended. """
        img_urls = self.get_image_urls(sub, sorting, num, limit)

        folder = os.path.join(base_folder, sub)

        print( 'Downloading '+ str(len(img_urls)) + ' images from ' + sub +', sorted by ' +sorting  )
        for i, url in enumerate(img_urls):
            filename = sub + str(i + 1)
            self.download_image(url, filename, folder)
            print(str(i), end=" ")
        print('Finished!' )
