import logging
from logging import handlers

###########
# loggers #
###########

# Logging out of RedditBotCephalonWiki
cephalon = logging.getLogger('cephalon-wiki')
cephalon.setLevel(logging.DEBUG)

# Logging out of warframeWikiScrapper
scrapper = logging.getLogger('scrapper')
scrapper.setLevel(logging.DEBUG)

# Logging out of warframeWikiItemComparer
comparison = logging.getLogger('comparison')
comparison.setLevel(logging.DEBUG)

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
comment_log = logging.handlers.TimedRotatingFileHandler("../../logs/comments-log", 'midnight')
comment_log.suffix = "%Y-%m-%d.txt"
comment_log.setLevel(logging.INFO)

# when not responding to a comment, will log a WARNING
warning_log = logging.handlers.TimedRotatingFileHandler("../../logs/warning-log", 'midnight')
warning_log.suffix = "%Y-%m-%d.txt"
warning_log.setLevel(logging.WARNING)

# will log spelling corrections as warnings
spell_checker_log = logging.handlers.TimedRotatingFileHandler("../../logs/spell-checker-log", 'midnight')
spell_checker_log.suffix = "%Y-%m-%d.txt"
spell_checker_log.setLevel(logging.WARNING)

exception_log = logging.handlers.TimedRotatingFileHandler("../../logs/exceptions-log", 'midnight')
exception_log.suffix = "%Y-%m-%d.txt"
exception_log.setLevel(logging.ERROR)


##########################
# Add filters to handlers #
##########################

# filters on list given as input
class LevelFilter(object):
    def __init__(self, levels):
        self.levels = levels

    def filter(self, record):
        return record.levelno in self.levels

comment_log.addFilter(LevelFilter([logging.INFO]))
warning_log.addFilter(LevelFilter([logging.WARNING]))

##############################
# Add formatters to handlers #
##############################

formatter = logging.Formatter('%(asctime)s - %(name)22s - %(funcName)20s -  %(message)s')

# all files have the same format
console.setFormatter(formatter)
comment_log.setFormatter(formatter)
warning_log.setFormatter(formatter)
exception_log.setFormatter(formatter)
spell_checker_log.setFormatter(formatter)

###########################
# Add handlers to loggers #
###########################

# all events are handled by the console

# bot will log to every file/handler
cephalon.addHandler(console)
cephalon.addHandler(comment_log)
cephalon.addHandler(warning_log)
cephalon.addHandler(exception_log)

# spelling corrections are logged
spell_checker.addHandler(console)
spell_checker.addHandler(spell_checker_log)

# scrapper will only log exceptions
scrapper.addHandler(console)
scrapper.addHandler(exception_log)

# comparison will only log exceptions, as with scrapper
comparison.addHandler(console)
comparison.addHandler(exception_log)

