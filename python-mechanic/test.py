import sys
sys.path.append('../python-bot')
args = sys.argv

from pprint import pprint

import CephalonWikiLogger
import RedditBotCephalonWiki
import logging


test_bot = RedditBotCephalonWiki.RedditBotCephalonWiki(name="test-cephalon-wiki", subreddit="cephalonwiki")

if __name__ == "__main__":
    if "full" in args:
        for l in CephalonWikiLogger.loggers:
            l.setLevel(logging.WARNING)
        test_cases = ["Mirage",
                      "Hall of Mirrors",
                      "Vazarin",  # FIXED:  redirects with "Focus/Vazarin" to scrapper
                      "Protective Dash",
                      "Lex Prime",
                      "Lex, Lex Prime",
                      "Mirage, Mirage Prime",
                      "Vigor, Primed Vigor",
                      "Freezing Step",
                      "Landing Craft",
                      "Critical Hit",  # FIXED:  Missing p tag, weird capitalization
                      "Crit Tiers",  # NOT FIXED:  Table tag at top of section; moved after first paragraph
                      "Mortus Lungfish"]

        for t in test_cases:
            pprint("\n")
            pprint("==================")
            if test_bot.format_article_summary(t):
                pprint("%s:  OK!".format(t))
            else:
                pprint("%s:  FAILURE :(".format(t))
            pprint("++++++++++++++")

        for l in CephalonWikiLogger.loggers:
            l.setLevel(logging.DEBUG)

    test_bot.scan()

