import sys
sys.path.append('../python-bot')

import RedditBotCephalonWiki

test_bot = RedditBotCephalonWiki.RedditBotCephalonWiki(name = "CephalonWikiTestBot")
test_bot.scan()
