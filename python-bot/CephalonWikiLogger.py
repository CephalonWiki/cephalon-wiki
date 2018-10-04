import logging
from logging import handlers
import datetime


###########
# loggers #
###########

# Logging out of RedditBotCephalonWiki
cephalon = logging.getLogger('cephalon')
cephalon.setLevel(logging.DEBUG)

# Logging out of warframeWikiScrapper
scrapper = logging.getLogger('scrapper')
scrapper.setLevel(logging.DEBUG)

# Logging specifically for spelling correction
spell_checker = logging.getLogger('spell_checker')
spell_checker.setLevel(logging.DEBUG)


############
# handlers #
############

# display all messages on console
console = logging.StreamHandler()
console.setLevel(logging.DEBUG)

# comment events will be logged with level INFO
comment_log = logging.handlers.TimedRotatingFileHandler("../../logs/comments-", 'midnight')
comment_log.setLevel(logging.INFO)

# when not responding to a comment, will log a WARNING
no_response_log = logging.handlers.TimedRotatingFileHandler("../../logs/no-response-", 'midnight')
no_response_log.setLevel(logging.WARNING)

exception_log = logging.handlers.TimedRotatingFileHandler("../../logs/exceptions-", 'midnight')
exception_log.setLevel(logging.ERROR)

# will log spelling corrections as warnings
spell_checker_log = logging.handlers.TimedRotatingFileHandler("../../logs/spell-checker-", 'midnight')
spell_checker_log.setLevel(logging.WARNING)


##############
# formatters #
##############

console_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(funcName)s -  %(message)s')
log_formatter = logging.Formatter('%(asctime)s - %(name)s -  %(message)s')


#############################
# Add formatteres, handlers #
#############################

# add formatters
console.setFormatter(console_formatter)

comment_log.setFormatter(log_formatter)
no_response_log.setFormatter(log_formatter)
exception_log.setFormatter(log_formatter)
spell_checker_log.setFormatter(log_formatter)

# add handlers to loggers
cephalon.addHandler(console)
cephalon.addHandler(comment_log)
cephalon.addHandler(no_response_log)
cephalon.addHandler(exception_log)

scrapper.addHandler(console)
scrapper.addHandler(exception_log)

spell_checker.addHandler(console)
spell_checker.addHandler(spell_checker_log)