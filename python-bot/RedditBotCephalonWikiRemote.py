import datetime
import subprocess
import sys
sys.path.append("../python-bot")

import praw

import RedditBotCephalonWiki

# create Reddit instance
with open("../data/credentials.txt", 'r') as login_credentials:
    credentials = login_credentials.readline().split(',')
    reddit_instance = praw.Reddit(client_id=credentials[0], client_secret=credentials[1], user_agent=credentials[2],
                                  username=credentials[3], password=credentials[4])


class RedditBotCephalonWikiRemote(RedditBotCephalonWiki.RedditBotCephalonWiki):

    def __init__(self):
        super().__init__(name="Cephalon Wiki Remote")

    def check(self, message):
        if message.author == self.mechanic and not message.replies:
            message_response = ""

            if "Status" in message.subject:
                for event in ["comment", "exception", "null-response", "article-not-found"]:
                    message_response += "*****\nToday's " + event + " log:\n*****"

                    try:
                        with open("../logs/" + event + "-log-" + str(datetime.date.today()) + ".txt", 'r') as log:
                            message_response += log.read() + "\n"
                    except Exception:
                        continue

                message.reply(message_response)

                self.console_log("Status update sent to mechanic " + str(self.mechanic))
            elif "Restart" in message.subject:
                subprocess.run('../shell-mechanic/start.sh', shell=True)
                run_tmux_ls = subprocess.run(['tmux', 'ls'], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

                message.reply(run_tmux_ls.stdout.decode('utf-8'))

                self.console_log("Bot restarted successfully.")
            elif "Recovery" in message.subject:
                subprocess.run('../shell-mechanic/recovery.sh', shell=True)
                run_tmux_ls = subprocess.run(['tmux', 'ls'], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

                message.reply(run_tmux_ls.stdout.decode('utf-8'))

                self.console_log("Recovery ran successfully.")
