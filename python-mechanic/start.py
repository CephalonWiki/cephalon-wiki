import sys
sys.path.append('../python-bot')

import RedditBotCephalonWiki

wiki_bot = RedditBotCephalonWiki.RedditBotCephalonWiki()
wiki_bot.scan(wiki_bot.subreddit.stream.comments())
