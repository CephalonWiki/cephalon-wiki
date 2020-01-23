import sys
sys.path.append('../python-bot')
import time
import subprocess

import RedditBotCephalonWiki
import articles_list

recovery_bot = None
reboot = 0

while True:
    try:
        # Regenerate articles list
        articles_list.generate()

        recovery_bot = RedditBotCephalonWiki.RedditBotCephalonWiki(name="recovery-cephalon-wiki")
        recovery_bot.logger.info("Reviewing comments from hot and new posts.")

        post_list = [recovery_bot.subreddit.hot(), recovery_bot.subreddit.new()]
        comments = []

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
    except KeyboardInterrupt:
        recovery_bot.logger.debug("Interrupting...")
        break
    except Exception as e:
        recovery_bot.logger.error("Exception raised:  " + str(e))

        if reboot < 5:
            reboot += 1
            recovery_bot.logger.debug("%s retries attempted.", reboot)

            # take a nap and start again
            recovery_bot.logger.debug("Napping...")
            time.sleep(30)
        else:
            recovery_bot.logger.error("Five retries attempted.  Rebooting...")
            subprocess.run('reboot')