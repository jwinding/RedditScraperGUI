# RedditScraperGUI

A program that downloads images from reddit, it find posts from the specified
subreddit, and downloads images to the specified folder. This is done through
a GUI which also lets you view the images.

The user needs to have a valid reddit login, which will be saved in plain
text in the config file, so perhaps one should be a little careful with that.
Or one can make a new reddit account to use with this app. In the future I
might implement some simple encryption for the user info.

The reddit scraping is done using the PRAW API, and the user interface is
implemented using PyQt5. The redditScraper.py file deals with the interfacing with
reddit, and the redditScraperGUI.py implements the GUI, logically enough.

# Running it:

clone the repo, then create a virtual environment somewhere (with virtualenv, venv or pipenv) and activate it. Then install the requirements with pip, and finally run the run_scraper script.

Explicitly:

```
git clone git@github.com:jwinding/RedditScraperGUI.git
cd RedditScraperGUI
python -m virtualenv env
.\env\Scripts\activate
pip install -r requirements.txt
python run_scraper.py
```
