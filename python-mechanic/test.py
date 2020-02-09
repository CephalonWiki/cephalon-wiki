import sys
sys.path.append('../python-bot')
args = sys.argv

from pprint import pprint

import RedditBotCephalonWiki


test_bot = RedditBotCephalonWiki.RedditBotCephalonWiki(name = "test-cephalon-wiki", subreddit = "cephalonwiki")

if __name__ == "__main__":
    if "full" in args:
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
            pprint(t)
            pprint("==================")
            pprint(test_bot.format_article_summary(t))
            pprint("++++++++++++++")

    test_bot.scan()

