import sys
sys.path.append('../python-bot')

import RedditBotCephalonWiki
import CephalonWikiLogger

recovery_bot = RedditBotCephalonWiki.RedditBotCephalonWiki(name = "recovery-cephalon-wiki")

# deprecated :(
# get posts from last 36 hours
# recent_posts = recovery_bot.subreddit.submissions(time.time()-1.1*86400, time.time())

post_list = [recovery_bot.subreddit.hot(), recovery_bot.subreddit.new()]

# aggregate comments
comments = []

recovery_bot.logger.info("Reviewing comments from hot and new posts.")
for posts in post_list:    
    for submission in posts:
        submission.comments.replace_more(limit=0)
        comments += list(filter(recovery_bot.should_respond, submission.comments.list()))
        recovery_bot.logger.debug("Gathered comments from submission \"" + submission.title + "\"")

if comments:
    # using set as duplicate comments found in queue?
    recovery_bot.logger.info("Found the following comments:  %s", set(comments))
    recovery_bot.scan(set(comments))
else:
    recovery_bot.logger.warning("No comments found during recovery.  Terminating.")
