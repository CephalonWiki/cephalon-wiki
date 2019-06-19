import sys
sys.path.append('../python-bot')

from pprint import pprint

import RedditBotCephalonWiki

test_bot = RedditBotCephalonWiki.RedditBotCephalonWiki(name = "test-cephalon-wiki", subreddit = "cephalonwiki")

if __name__ == "__main__":
    test_cases = ["Mirage",
                  "Hall of Mirrors",
                  "Vazarin", #FIXED:  redirects with "Focus/Vazarin" to scrapper
                  "Protective Dash",
                  "Lex Prime",
                  "Lex, Lex Prime",
                  "Mirage, Mirage Prime",
                  "Vitality, Primed Vitality",
                  "Freezing Step",
                  "Landing Craft",
                  "Critical Hit", #NOT FIXED:  Figure tag at top of page; moved after first paragraph
                  "Crit Tiers", #NOT FIXED:  Table tag at top of section; moved after first paragraph
                  "Mortus Lungfish"]

    for t in test_cases:
        pprint("\n")
        pprint(t)
        pprint("==================")
        pprint(test_bot.format_article_summary(t))
        pprint("++++++++++++++")

    
    test_bot.scan()

