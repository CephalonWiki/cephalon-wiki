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
        
        # logging object
        self.logger = logging.getLogger("reddit bot")
        self.logger.setLevel(logging.DEBUG)

        self.header = ""
        self.footer = ""

        # bot name
        self.name = ""

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
        # preparing response using the module
        response = self.response(comment)
        response_log = ""

        if response and self.should_respond(comment):
            comment.reply(self.header + response + self.footer)
            
            self.logger.info("******************************")
            self.logger.info("Comment id:  %s", str(comment))
            self.logger.info("Comment text:  %s", comment.body.strip().replace("\n", "\t"))
            
            response_log = "Response:  " + response.strip().replace("\n", "\t")
            self.logger.info(response_log)

        else:
            response_log = "Not responding to comment " + str(comment)
            self.logger.warning(response_log)
        
        

    def check(self, comment):
        self.logger.debug("Reading comment %s", comment)

        # check if we should respond
        if self.should_respond(comment):
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

        except Exception as e:
            error_msg = "Exception raised:  " + str(e)

            self.logger.exception(error_msg)

            # take a nap and start again
            self.logger.debug("Napping...")
            time.sleep(60)
            self.scan(stream)
