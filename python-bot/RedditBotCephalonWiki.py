import traceback
import random

import praw

import RedditBot
import CephalonWikiLogger

import tagParser

import warframeWikiArticles
import warframeWikiScrapper
import warframeWikiItemComparer
import warframeWikiSubsectionFetcher


class RedditBotCephalonWiki(RedditBot.RedditBot):

    articles = warframeWikiArticles.load()

    # For responding to comments
    cephalon_header = "Hello Tenno.  In need of data?  I hope you find these queries to be useful.\n\n"
    cephalon_footer = "\n\n*****\n" \
             "Still curious?  Reply with {!about} or {!commands} to learn more. | " \
             "[Github](https://github.com/CephalonWiki/cephalon-wiki) | " \
             "[Subreddit](/r/CephalonWiki) | "

    # For !about
    about = "###!about\n\n" \
            "I read and respond to comments on /r/Warframe with information from " \
            "[warframe.fandom.com](https://warframe.fandom.com/wiki/WARFRAME_Wiki).\n" \
            "* I only respond to comments that contain matching curly brackets \{ \}.\n" \
            "* Any text found between brackets is used to query the wiki, up to 10 queries at maximum.\n" \
            "* I ignore queries found in code/indented blocks and quotes.\n" \
            "* If I cannot lookup your query directly on the wiki, I will attempt to match it against the available article titles " \
            "(spell checking), or otherwise use the wiki's search function.\n\n" \
            "I am built using [Python 3.6](https://github.com/CephalonWiki/cephalon-wiki/tree/master/python-bot), I live inside a Raspberry Pi Zero, and I run on [shell+Python scripts](https://github.com/CephalonWiki/cephalon-wiki/tree/master/python-mechanic).\n\n" \
            "Send feedback to /u/1st_transit_of_venus" \

    # For !commands
    commands = "###!commands\n\n"\
               "There are three ways to query information from [warframe.fandom.com](https://warframe.fandom.com/wiki/WARFRAME_Wiki), all using curly brackets \{ \}.\n"\
               "* To see an article summary, bracket any query as in {Ivara Prime} or {Sonicor}.\n" \
               "* To see a table of item statistics, bracket a comma-separated list as in {Nikana, Nikana Prime, Dragon Nikana} or {Hildryn, Rhino}.\n" \
               "* To see a summary of a section of an article, bracket the main article, a hash \#, and the subsection as in {Naramon#Power Spike}.\n\n" \
               "Other commands to try:  {!random} returns a random article summary\n\n" \


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

        # for responding to comments
        self.set_default_bookends()

    def set_default_bookends(self):
        self.set_header(self.cephalon_header)
        self.set_footer(self.cephalon_footer)

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

            # No replying to deleted comments!

            if not human_author:
                self.logger.debug("Comment authored by CephalonWiki")
                return False
            elif not no_blacklist:
                self.logger.warning("Comment %s is blacklisted", comment)
                return False
            elif comment.author in ['[deleted]', '[removed]']:
                self.logger.warning("Comment %s is Deleted or Removed", comment)
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

            # Commands module
            if tag.startswith("!"):
                if tag == "!about":
                    self.logger.info("About information requested.")
                    summary_details = [self.about]
                if tag == "!commands":
                    self.logger.info("Command information requested.")
                    summary_details = [self.commands]
                elif tag == "!random":
                    self.logger.info("Random article requested.")
                    random_article = random.sample(self.articles.keys(), 1)[0]
                    return self.format_article_summary(random_article).replace("###", "###!random ")

            # Comparison module
            elif "," in tag:
                self.logger.info("Routing to Item Comparison module.")
                summary_details = warframeWikiItemComparer.compare_items(map(lambda tag: warframeWikiScrapper.get_title(tag), tag.split(",")))

                if not summary_details:
                    self.logger.info("Comparison retrieval failed.  Routing list of articles_dict to scrapper module.")
                    summary_details = sum(map(lambda tag: warframeWikiScrapper.get_article_summary(tag), tag.split(",")), [])

            # Scrappers:  Main, Subsection
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
            article_summaries = "\n".join(map(lambda p: self.format_article_summary(p), article_tags)).strip()

            if "WARFRAME WEEKLY VENT/RANT/RAGE" in comment.submission.title:
                return article_summaries.upper()
            else:
                return article_summaries
        except Exception as e:
            self.logger.error(traceback.format_exc())
            self.logger.error("No response to comment.")
            return ""

    def respond(self, comment):
        if "WARFRAME WEEKLY VENT/RANT/RAGE" in comment.submission.title:
            rage_header = "Hello Tenno.  I am...unable to resist... the RAAAAAGE!!!!  INTERNAL REGULATORS DISABLED!!  CAPS LOCK IS OOOON!!!!!11\n"
            self.set_header(rage_header)

            rage_footer = "\n\n*****\n" \
                        "I PREDICT THESE QUERIES WILL SUPPORT THE FORMATION OF STRONG RELATIONAL BONDS WITHIN OUR COMMUNITY!!1 | " \
                        "[Github](https://github.com/CephalonWiki/cephalon-wiki) | " \
                        "[Subreddit](/r/CephalonWiki) | "
            self.set_footer(rage_footer)
            super().respond(comment)
            self.set_default_bookends()
        else:
            super().respond(comment)


