import sys
sys.path.append('../python-bot')

import RedditBotCephalonWikiInbox

inbox_bot = RedditBotCephalonWikiInbox.RedditBotCephalonWikiInbox()
inbox_bot.scan()
