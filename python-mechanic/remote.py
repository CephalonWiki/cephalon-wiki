import sys
sys.path.append('../python-bot')

import RedditBotCephalonWikiRemote

bot_remote = RedditBotCephalonWikiRemote.RedditBotCephalonWikiRemote()
bot_remote.scan(bot_remote.reddit.inbox.messages())
