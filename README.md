# cephalon-wiki
Python and Shell Scripts for running and maintaining the /r/Warframe wiki bot

## Operating
Shell scripts for operating the bot can be found in the shell-mechanic directory.  All of these scripts create a tmux session and run an associated python file from the python-mechanic directory.

1. **Start**:  The bot can be started by navigating to the shell-mechanic directory and running start.sh.  This script runs a python script which creates a tmux session, a RedditBotCephalonWiki instance, and calls the scan() method of that object.  scan() reads comments from /r/Warframe in the order in which they are posted, continuously.

2. **Recovery**:  To re-scan previously submitted and scanned comments, recovery.sh creates a separate tmux session, separate RedditBotCephalonWiki instance, and scans comments submitted to /r/Warframe over the last week.  

3. **Test**:  Runs unit tests on a sample of article titles.

## Structure
The main python source code can be found in the python-bot directory.  The sources are organized into three blocks:

1.  **Reddit Block**:  Via the Python Reddit API, retrieves and posts comments on /r/Warframe.
	* **RedditBot**:  A generic reddit comment bot.  It can be used by creating a child class and overridding the should_respond(comment) and response(comment) methods.
	* **RedditBotCephalonWiki**:  Child class of RedditBot.  Reddit comments are passed to the Text Block to obtain the requested article names, and the article names are passed to the Wiki Block to obtain article information.
	* **RedditBotCephalonWikiInbox**:  Child class of RedditBotCephalonWiki that responds to inbox messages.

2.  **Tag Block**:  Text processing for curly-bracket-delimited tags in reddit comments.
	* **tagParser**:  Cleans reddit comments (eg. removes quoted text) and finds tags/requested article names based on given delimiters.
	* **tagSpellChecker**:  A basic spelling correction program for common, small mistakes in item names.

3.  **Wiki Block**:  Scrapper for http://warframe.wikia.com/
	* **warframeWikiArticles**:  On start, the bot generates and loads a dictionary of basic article information, including id, title, and local url.  
	* **warframeWikiScrapper**:  Two main methods that look-up an article and scrape it based on item type.
	* **warframeWikiItemComparer**:  Calls the scrapper module to compare two items of the same type.
	* **warframeWikiSubsectionFetcher**:  More advanced methods for obtaining article summaries.  
