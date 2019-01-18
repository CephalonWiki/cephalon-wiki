import traceback

import praw

import RedditBot

import CephalonWikiLogger

import tagParser

import warframeWikiScrapper
import warframeWikiItemComparer

import random

# For responding to comments
header = "Hello Tenno.  Here is the information you requested.\n"
footer = "\n\n*****\n\nCode available on [github](https://github.com/CephalonWiki/cephalon-wiki) | Bot by /u/1st_transit_of_venus"

blacklist = ['e7fnpxb', 'e5d8sl2']

class RedditBotCephalonWiki(RedditBot.RedditBot):

    def __init__(self, name="cephalon-wiki", subreddit="warframe"):

        # create Reddit instance
        with open("../../data/credentials.txt", 'r') as login_credentials:
            credentials = login_credentials.readline().split(',')
            reddit_instance = praw.Reddit(client_id=credentials[0], client_secret=credentials[1],
                                          user_agent=credentials[2] + ":%s".format(random.random()),
                                          username=credentials[3], password=credentials[4])
            super().__init__(reddit_instance)

        super().set_name(name)
        super().set_logger(CephalonWikiLogger.cephalon)
        self.logger.name = name

        super().set_subreddit(subreddit)
        super().set_mechanic("1st_transit_of_venus")

        # for responding to messages
        super().set_header(header)
        super().set_footer(footer)

        self.vorologue = "Look at them, they come to this place when they know they are not pure. Tenno use the keys, but they are mere trespassers. Only I, Vor, know the true power of the Void. I was cut in half, destroyed, but through it's Janus Key, the Void called to me. It brought me here and here I was reborn. We cannot blame these creatures, they are being led by a false prophet, an impostor who knows not the secrets of the Void. Behold the Tenno, come to scavenge and desecrate this sacred realm. My brothers, did I not tell of this day? Did I not prophesize this moment? Now, I will stop them. Now I am changed, reborn through the energy of the Janus Key. Forever bound to the Void. Let it be known, if the Tenno want true salvation, they will lay down their arms, and wait for the baptism of my Janus key. It is time. I will teach these trespassers the redemptive power of my Janus key. They will learn it's simple truth. The Tenno are lost, and they will resist. But I, Vor, will cleanse this place of their impurity."



    def should_respond(self, comment):
        if ("{" in comment.body and comment.body.find("}", comment.body.rfind("{")) > 0):
            self.logger.debug("Comment contains matching braces")

            if comment.author != "CephalonWiki":
                self.logger.debug("Comment not authored by CephalonWiki")

                reply_authors = list(map(lambda c: c.author, comment.replies.list()))
                if "CephalonWiki" not in reply_authors:
                    if str(comment) not in blacklist:
                        self.logger.debug("Have not replied to comment %s", comment)
                        return True
                    else:
                        self.logger.info("Attempted to reply to blacklisted comment %s", comment)
                        return False
                else:
                    self.logger.warning("Already replied to comment %s", comment)
                    return False
            else:
                self.logger.warning("Comment authored by CephalonWiki")
                return False
        elif "look at them" in comment.body.lower():
            return True
        else:
            # most comments will not contain matching braces
            return False

    # prepare summary of article, as a string
    # scrapping modules used here
    def format_article_summary(self, title, detail=False):
        try:
            if "," in title:
                summary_details = warframeWikiItemComparer.compare_items(*title.split(","))
            else:
                summary_details = warframeWikiScrapper.get_article_summary(title, detail)

            if summary_details:
                self.logger.info("Retrieval for title %s succeeded.", title)
                return "\n\n".join(["*****"] + summary_details)
            else:
                self.logger.warning("No details retrieved for title %s", title)
                return ""
        except Exception:
            self.logger.error("Retrieval for title %s failed.", title)
            self.logger.error(traceback.format_exc())

            if detail:
                self.logger.warning("Trying to retrieve simple version of title %s.", title)
                return self.format_article_summary(title)
            else:
                self.logger.error("No details retrieved for title %s", title)
                return ""

    def response(self, comment):
        try:
            if "look at them" in comment.body.lower():
                return "*****" + "\n\n" + self.vorologue
            article_titles = tagParser.get_tagged_articles(comment.body)
            article_summaries = "\n".join(map(lambda p: self.format_article_summary(*p), article_titles)).strip()

            return article_summaries
        # Error catching for parsing layer and below
        except Exception as e:
            error_msg = "Parsing Exception raised - " + str(e) + " - in comment " + str(comment)
            self.logger.error(error_msg)

            # if problem not with reddit, send mechanic a message
            # deprecate this
            #self.mechanic.message("Parsing Exception Raised", traceback.format_exc())

            return ""
