import sys
sys.path.append('../python-bot')

import RedditBotCephalonWiki

recovery_bot = RedditBotCephalonWiki.RedditBotCephalonWiki(name = "recovery-cephalon-wiki")

# deprecated :(
# get posts from last 36 hours
# recent_posts = recovery_bot.subreddit.submissions(time.time()-1.1*86400, time.time())

# get submissions from last 24 hours
recent_posts = recovery_bot.subreddit.top(time_filter="week")

# aggregate comments
comments = []
for submission in recent_posts:
    submission.comments.replace_more(limit=0)
    comments += list(filter(recovery_bot.should_respond, submission.comments.list()))
    recovery_bot.logger.info("Gathering comments from submission \"" + submission.title + "\"")

if comments:
    recovery_bot.scan(comments)
else:
    recovery_bot.logger.warning("No comments found.  Terminating.")
