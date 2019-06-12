import traceback

import praw

import RedditBot

import CephalonWikiLogger

import tagParser

import warframeWikiScrapper
import warframeWikiItemComparer
import warframeWikiSubsectionFetcher

import random

# For responding to comments
header = "Hello Tenno.  Here is the information you requested.\n"
footer = "\n\n*****\n\n Want a summary of a subsection?  Try {Vazarin#Protective Dash} or {Fishing#Mortus Lungfish} | [Github](https://github.com/CephalonWiki/cephalon-wiki) | [Subreddit](/r/CephalonWiki) | "

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


    # clean up the nested ifs yuck
    def should_respond(self, comment):

        # Prepare 4 criteria:  Match brackets, human author, no previous reply, not on blacklist
        matches_brackets = ("{" in comment.body and comment.body.find("}", comment.body.rfind("{")) > 0)
        if not matches_brackets:
            # most comments will not invoke the bot, so take no action
            return False
        else:
            # Now that the comment is likely a candidate, do more processing
            human_author = comment.author != "CephalonWiki"

            # Given updates to reply author code, blacklist should not be necessary
            no_blacklist = str(comment) not in ['e7fnpxb', 'e5d8sl2']

            if not human_author:
                self.logger.debug("Comment authored by CephalonWiki")
                return False
            elif not no_blacklist:
                self.logger.error("Attempted to reply to blacklisted comment %s", comment)
                return False
            else:
                # Now that the comment is human-authored and contains matching braces...
                # ...refresh comment and check replies
                comment.refresh()
                comment.replies.replace_more(limit=0)
                reply_authors = list(map(lambda c: c.author, comment.replies.list()))
                no_reply = "CephalonWiki" not in reply_authors
                if not no_reply:
                    self.logger.debug("Already replied to comment %s", comment)
                    return False
                else:
                    # Comment meets minimum criteria.
                    self.logger.debug("Should respond to comment %s", comment)
                    self.logger.info("***** NEW COMMENT *****")
                    return True


    # prepare summary of article, as a string
    # scrapping modules used here
    def format_article_summary(self, tag, detail=False):
        try:
            summary_details = ""
            if "," in tag:
                self.logger.info("Routing to Item Comparison module.")
                summary_details = warframeWikiItemComparer.compare_items(map(lambda tag: warframeWikiScrapper.get_title(tag), tag.split(",")))

                if not summary_details:
                    self.logger.info("Comparison retrieval failed.  Routing list of articles to scrapper module.")
                    summary_details = sum(map(lambda tag: warframeWikiScrapper.get_article_summary(tag), tag.split(",")), [])

            else:
                title = ""
                redirected_title = warframeWikiScrapper.get_article_info(tag)["title"]
                if "#" in tag or "#" in redirected_title:
                    t, subsection = redirected_title.split("#") if "#" in redirected_title else tag.split("#")
                    title = warframeWikiScrapper.get_title(t)
                    self.logger.info("Routing to Subsection Fetcher module.")
                    summary_details = warframeWikiSubsectionFetcher.get_article_subsection(t, subsection.replace("_", " "))
                else:
                    title = warframeWikiScrapper.get_title(tag)
                    self.logger.info("Routing to Scrapper module.")
                    summary_details = warframeWikiScrapper.get_article_summary(title)

            if summary_details:
                self.logger.info("Retrieval for tag %s succeeded.", tag)
                return "\n\n".join(["*****"] + summary_details)
            else:
                self.logger.warning("No details retrieved for tag %s", tag)
                return ""
        except Exception:
            self.logger.error("Retrieval for tag %s failed.", tag)
            self.logger.error(traceback.format_exc())

            if detail:
                self.logger.warning("Trying to retrieve simple version of tag %s.", tag)
                return self.format_article_summary(tag)
            else:
                self.logger.error("No details retrieved for tag %s", tag)
                return ""

    def response(self, comment):
        try:
            article_tags = tagParser.get_tagged_articles(comment.body)
            article_summaries = "\n".join(map(lambda p: self.format_article_summary(*p), article_tags)).strip()

            return article_summaries
        except Exception as e:
            self.logger.error("No response to comment %s", comment)
            return ""