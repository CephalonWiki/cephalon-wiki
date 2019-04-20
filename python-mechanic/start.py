import time
import subprocess
import sys
sys.path.append('../python-bot')

import RedditBotCephalonWiki

reboot = 0
wiki_bot = None

while True:
    try:
        wiki_bot = RedditBotCephalonWiki.RedditBotCephalonWiki()
        wiki_bot.scan()
    except KeyboardInterrupt:
        wiki_bot.logger.debug("Interrupting...")
        break
    except Exception as e:
        if reboot < 5:
            reboot += 1
            wiki_bot.logger.debug("%s retries attempted.", reboot)

            # take a nap and start again
            wiki_bot.logger.debug("Napping...")
            time.sleep(30)
        else:
            wiki_bot.logger.error("Five retries attempted.  Rebooting...")
            subprocess.run('reboot')
