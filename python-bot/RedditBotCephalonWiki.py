import traceback

import praw

import RedditBot

import CephalonWikiLogger

import tagParser

import warframeWikiScrapper
import warframeWikiItemComparer

# create Reddit instance
with open("../../data/credentials.txt", 'r') as login_credentials:
    credentials = login_credentials.readline().split(',')
    reddit_instance = praw.Reddit(client_id=credentials[0], client_secret=credentials[1], user_agent=credentials[2],
                                  username=credentials[3], password=credentials[4])

# For responding to comments
header = "Hello Tenno.  Here is the information you requested.\n"
footer = "\n\n*****\n\nBot by /u/1st_transit_of_venus | " \
         "Code available on [github](https://github.com/CephalonWiki/cephalon-wiki)"


class RedditBotCephalonWiki(RedditBot.RedditBot):

    def __init__(self, name="Cephalon Wiki"):
        super().__init__(reddit_instance)
        super().set_subreddit("warframe")
        super().set_mechanic("1st_transit_of_venus")
        super().set_header(header)
        super().set_footer(footer)
        super().set_name(name)
        super().set_logger(CephalonWikiLogger.cephalon)

    @staticmethod
    def should_respond(comment):
        reply_authors = list(map(lambda c: c.author, comment.replies.list()))
        return ("{" in comment.body and comment.body.find("}", comment.body.rfind("{")) > 0) \
            and comment.author != "CephalonWiki" and "CephalonWiki" not in reply_authors

    # prepare summary of article, as a string
    # scrapping modules used here
    def format_article_summary(self, title, detail=False):
        try:
            if "," in title:
                summary_details = warframeWikiItemComparer.compare_items(*title.split(","))
            else:
                summary_details = warframeWikiScrapper.get_article_summary(title, detail)

            if summary_details:
                return "\n\n".join(["*****"] + summary_details)
            else:
                self.logger.warning("Requested:  %s", title)
                return ""
        except Exception:
            if detail:
                return self.format_article_summary(title)
            else:
                # log response
                self.logger.warning("Requested:  %s", title)
                return ""

    def response(self, comment):
        try:
            article_titles = tagParser.get_tagged_articles(comment.body)
            article_summaries = "\n".join(map(lambda p: self.format_article_summary(*p), article_titles)).strip()

            return article_summaries
        # Error catching for parsing layer and below
        except Exception as e:
            error_msg = "Parsing Exception raised - " + str(e) + " - in comment " + str(comment)
            self.logger.exception("******************************")
            self.logger.exception(error_msg)

            # if problem not with reddit, send mechanic a message
            self.mechanic.message("Parsing Exception Raised", traceback.format_exc())

            return ""
