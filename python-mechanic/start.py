import sys
sys.path.append('../python-bot')

import RedditBotCephalonWiki

wiki_bot = RedditBotCephalonWiki.RedditBotCephalonWiki(name = "CephalonWiki")
wiki_bot.scan()
