import datetime
import time
import traceback
import logging

class RedditBot:

    def __init__(self, reddit):

        # Reddit instance
        self.reddit = reddit

        # Subreddit instance
        self.subreddit = self.reddit.subreddit('all')

        # bot manager
        self.mechanic = None

        self.header = ""
        self.footer = ""

        # bot name
        self.name = ""
        
        # logging object
        self.logger = logging.getLogger(self.name)
        self.logger.setLevel(logging.DEBUG)

    # getter/setters
    def set_subreddit(self, subreddit_name):
        self.subreddit = self.reddit.subreddit(subreddit_name)

    def set_mechanic(self, mechanic_name):
        self.mechanic = self.reddit.redditor(mechanic_name)
        
    def set_logger(self, logger):
        self.logger = logger

    def set_header(self, h):
        self.header = h

    def set_footer(self, f):
        self.footer = f

    def set_name(self, bot_name):
        self.name = bot_name

    # should be overridden by parent, return True if comment bears response
    @staticmethod
    def should_respond(comment):
        return False

    # should be overridden by parent, returns response to comment
    @staticmethod
    def response(comment):
        return ""

    def reply(self, comment):
        self.logger.info("******************************")
        self.logger.info("Comment JSON:  https://www.reddit.com/api/info.json?id=t1_%s", str(comment))
        self.logger.info("Comment text:  %s", comment.body.strip().replace("\n", "\t"))

        # preparing response using the module
        response = self.response(comment)

        if response:
            self.logger.info("Response text:")
            for s in response.strip().split("\n"):
                self.logger.info(s)
            self.logger.info("*****")

            comment.reply(self.header + response + self.footer)
            self.logger.info("Response posted to Reddit.")
        else:
            self.logger.warning("No response to " + str(comment))

    def check(self, comment):
        self.logger.debug("Reading comment %s", comment)

        # check if we should respond
        if self.should_respond(comment):
            self.logger.debug("Should respond to comment %s", comment)
            # 30 s window for redditor to edit comment
            nap_time = max(31 - int(time.time() - comment.created_utc), 0)
            self.logger.debug("Waiting %s seconds to respond to comment %s", nap_time, comment)
            time.sleep(nap_time)
            self.reply(comment)

    def scan(self, stream=None):
        try:
            scan_stream=None
            if not stream:
                scan_stream = self.subreddit.stream.comments()
            else:
                scan_stream = stream.copy()

            for comment in scan_stream:
                self.check(comment)

        except KeyboardInterrupt:
            self.logger.debug("Interrupting...")
            self.logger.error(traceback.format_exc())

        except Exception as e:
            error_msg = "Exception raised:  " + str(e)

            self.logger.error(error_msg)
            #self.logger.error(traceback.format_exc())

            # take a nap and start again
            self.logger.debug("Napping...")
            time.sleep(300)

            self.scan(stream)
