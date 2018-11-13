import traceback

import praw

import RedditBot

import CephalonWikiLogger

import tagParser

import warframeWikiScrapper
import warframeWikiItemComparer


# For responding to comments
header = "Hello Tenno.  Here is the information you requested.\n"
footer = "\n\n*****\n\nBot by /u/1st_transit_of_venus | " \
         "Code available on [github](https://github.com/CephalonWiki/cephalon-wiki)"


class RedditBotCephalonWiki(RedditBot.RedditBot):

<<<<<<< HEAD
    def __init__(self, name = "Cephalon Wiki"):
        super().__init__(reddit_instance)
        super().set_subreddit("warframe")
        super().set_mechanic("1st_transit_of_venus")
        super().set_header(header)
        super().set_footer(footer)
        super().set_name(name)
        super().set_logger(CephalonWikiLogger.cephalon)
=======
    def __init__(self, name="cephalon-wiki", subreddit="warframe"):

        super().set_name(name)
        super().set_logger(CephalonWikiLogger.cephalon)
        self.logger.name = name

        # create Reddit instance
        with open("../../data/credentials.txt", 'r') as login_credentials:
            credentials = login_credentials.readline().split(',')
            reddit_instance = praw.Reddit(client_id=credentials[0], client_secret=credentials[1],
                                          user_agent=credentials[2] + ":%s".format(name), username=credentials[3], password=credentials[4])
            super().__init__(reddit_instance)

        super().set_subreddit(subreddit)
        super().set_mechanic("1st_transit_of_venus")

        # for responding to messages
        super().set_header(header)
        super().set_footer(footer)

>>>>>>> dev

    def should_respond(self, comment):
        if ("{" in comment.body and comment.body.find("}", comment.body.rfind("{")) > 0):
            self.logger.debug("Comment contains matching braces")

            if comment.author != "CephalonWiki":
                self.logger.debug("Comment not authored by CephalonWiki")

                reply_authors = list(map(lambda c: c.author, comment.replies.list()))
                if "CephalonWiki" not in reply_authors:
                    self.logger.debug("Have not replied to comment %s", comment)
                    return True
                else:
                    self.logger.warning("Already replied to comment %s", comment)
                    return False
            else:
                self.logger.warning("Comment authored by CephalonWiki")
                return False
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
<<<<<<< HEAD
=======
            self.logger.error(traceback.format_exc())
>>>>>>> dev
            if detail:
                self.logger.warning("Trying to retrieve simple version of title %s.", title)
                return self.format_article_summary(title)
            else:
                self.logger.error("No details retrieved for title %s", title)
                return ""

    def response(self, comment):
        try:
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
