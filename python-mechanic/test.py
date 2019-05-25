import sys
sys.path.append('../python-bot')

import RedditBotCephalonWiki

test_bot = RedditBotCephalonWiki.RedditBotCephalonWiki(name = "test-cephalon-wiki", subreddit = "cephalonwiki")

if __name__ == "__main__":

    test_bot.scan()