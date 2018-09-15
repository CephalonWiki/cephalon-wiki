import datetime
import time
import traceback


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

    # getter/setters
    def set_subreddit(self, subreddit_name):
        self.subreddit = self.reddit.subreddit(subreddit_name)

    def set_mechanic(self, mechanic_name):
        self.mechanic = self.reddit.redditor(mechanic_name)

    def set_header(self, h):
        self.header = h

    def set_footer(self, f):
        self.footer = f

    def set_name(self, bot_name):
        self.name = bot_name

    # for logging
    def console_log(self, message):
        print(str(datetime.datetime.now()) + ":  " + self.name + "  ]]]", message)

    def log_event(self, lines, event="other"):
        with open("../logs/" + event + "-log-" + str(datetime.date.today()) + ".txt", 'a') as log:
            log.write("\n".join(["*"*27, str(datetime.datetime.now()) + ":  " + self.name] + lines + [""]))

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

        if response and self.should_respond(comment):
            self.console_log("Responding to comment " + str(comment))
            comment.reply(self.header + response + self.footer)
            event = "comment"
        else:
            self.console_log("Not responding to comment " + str(comment))
            event = "null-response"

        # log reply
        self.log_event(["Comment id:  " + str(comment),
                        "Comment text:  " + comment.body.strip().replace("\n", "\t"),
                        "Response text:  " + response.strip().replace("\n", "\t")], event)

    def check(self, comment):
        self.console_log("Reading comment " + str(comment))

        # check if we should respond
        if self.should_respond(comment):
            # 30 s window for redditor to edit comment
            nap_time = max(31 - int(time.time() - comment.created_utc), 0)
            self.console_log("Waiting " + str(nap_time) + " seconds to respond to comment " + str(comment))
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
            self.console_log("Interrupting...")

        # except (praw.exceptions.PRAWException, prawcore.exceptions.PrawcoreException) as e:
        #     error_msg = "Reddit exception raised:  " + str(e)
        #
        #     self.console_log(error_msg)
        #     self.log_event([traceback.format_exc()], "exception")
        #
        #     # take a nap and start again
        #     self.console_log("Napping...")
        #     time.sleep(15)
        #     self.scan(stream)

        except Exception as e:
            error_msg = "Exception raised:  " + str(e)

            self.console_log(error_msg)
            self.log_event([traceback.format_exc()], "exception")

            # take a nap and start again
            self.console_log("Napping...")
            time.sleep(60)
            self.scan(stream)
