import sys
sys.path.append('../python-bot')

import RedditBotCephalonWiki

test_bot = RedditBotCephalonWiki.RedditBotCephalonWiki(name = "dev-cephalon-wiki", subreddit = "cephalonwiki")
test_bot.scan()
