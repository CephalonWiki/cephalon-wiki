import sys
sys.path.append('../python-bot')

import RedditBotCephalonWiki

test_bot = RedditBotCephalonWiki.RedditBotCephalonWiki(name = "CephalonWikiTestBot")

test_bot.set_subreddit("cephalonwiki")
test_bot.logger.name = 'test-cephalon'

test_bot.scan()
