import sys
sys.path.append('../python-bot')

import RedditBotCephalonWiki

<<<<<<< HEAD
test_bot = RedditBotCephalonWiki.RedditBotCephalonWiki(name = "CephalonWikiTestBot")

test_bot.set_subreddit("cephalonwiki")
test_bot.logger.name = 'test-cephalon'

=======
test_bot = RedditBotCephalonWiki.RedditBotCephalonWiki(name = "dev-cephalon-wiki", subreddit = "cephalonwiki")
>>>>>>> dev
test_bot.scan()
