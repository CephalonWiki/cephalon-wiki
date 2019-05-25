import traceback
import time
import subprocess

import praw

import RedditBotCephalonWiki

import CephalonWikiLogger

import tagParser

import warframeWikiScrapper
import warframeWikiItemComparer

class RedditBotCephalonWikiInbox(RedditBotCephalonWiki.RedditBotCephalonWiki):

    def __init__(self):
        super().__init__(name="Cephalon Wiki Inbox")

    # clean up the nested ifs yuck
    def should_respond(self, message):
        # Prepare 4 criteria:  Match brackets, human author, no previous reply, not on blacklist
        matches_brackets = ("{" in message.body and message.body.find("}", message.body.rfind("{")) > 0)
        human_author = message.author != "CephalonWiki"
        if not matches_brackets or not human_author or message.was_comment:
            # most message will not invoke the bot, so take no action
            return False
        else:
            # Now that the message is likely a candidate, do more processing
            reply_authors = list(map(lambda c: c.author, message.replies))
            no_reply = "CephalonWiki" not in reply_authors
            if not no_reply:
                return False
            else:
                # Comment meets minimum criteria.
                self.logger.debug("Should respond to message %s", message)
                self.logger.info("***** NEW MESSAGE *****")
                return True

    def response(self, message):
        try:
            article_titles = tagParser.get_tagged_articles(message.body)
            article_summaries = "\n".join(map(lambda p: self.format_article_summary(*p), article_titles)).strip()

            return article_summaries
        except Exception as e:
            self.logger.error("No response to message %s", message)
            return ""

    def respond(self, message):
        self.logger.info("Message ID:  t4_%s", str(message))
        self.logger.info("Message text:  %s", message.body.strip().replace("\n", "\t"))

        # preparing response using the module
        response = self.response(message)
        if response:
            self.logger.info("Message response:")
            for s in response.strip().split("\n"):
                self.logger.info(s)

            message.reply(self.header + response + self.footer)
            self.logger.info("Replied to message.")

    def scan(self, stream = None, reboot = 0):
        try:
            # Stream set-up
            # Messages stream must be re-initialized after exception
            scan_stream = None
            if not stream:
                scan_stream = self.reddit.inbox.stream()

            for message in scan_stream:
                self.logger.debug("Reading message %s", message)

                # check if we should respond
                if self.should_respond(message):
                    # 30 s window for redditor to edit message
                    nap_time = max(31 - int(time.time() - message.created_utc), 0)
                    self.logger.debug("Waiting %s seconds to respond to message %s", nap_time, message)
                    time.sleep(nap_time)

                    self.respond(message)

        except KeyboardInterrupt:
            self.logger.debug("Interrupting...")

        except Exception as e:
            self.logger.error("Exception raised:  " + str(e))

            # take a nap and start again
            self.logger.debug("Napping...")
            time.sleep(30)

            self.scan()