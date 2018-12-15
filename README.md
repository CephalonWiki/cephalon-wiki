# cephalon-wiki
Python and Shell Scripts for running and maintaining the /r/Warframe wiki bot

## Using
1. **Start**:  The bot can be started by navigating to the shell-mechanic directory and running start.sh.  This script runs a python script which creates a tmux session, a RedditBotCephalonWiki instance, and calls the scan() method of that object.  scan() reads comments from /r/Warframe in the order in which they are posted, continuously.

2. **Recovery**:  To re-scan previously submitted and scanned comments, recovery.sh creates a separate tmux session, separate RedditBotCephalonWiki instance, and scans comments submitted to /r/Warframe over the last week.  

## Structure
The python code for the bot can be organized into three blocks:

1.  **Reddit Block**:  Via the Python Reddit API, retrieves and posts comments on /r/Warframe.
	* **RedditBot**:  A generic reddit comment bot.  It can be used by creating a child class and overridding the should_respond(comment) and response(comment) methods.
	* **RedditBotCephalonWiki**:  Child class of RedditBot.  Reddit comments are passed to the Text Block to obtain the requested article names, and the article names are passed to the Wiki Block to obtain article information.

2.  **Text Block**:  Text processing for reddit comments.
	* **tagParser**:  Cleans reddit comments (eg. removes quoted text) and finds tags/requested article names based on given delimiters.
	* **spell_checker**:  A basic spelling correction program for common, small mistakes in item names.
	* **all_articles**:  Dictionary of article information and list of article titles used in spell_checker module.

3.  **Wiki Block**:  Scrapper for http://warframe.wikia.com/
	* **warframeWikiScrapper**:  Two main methods that lookup an article and scrape it based on item type.
	* **warframeWikiItemComparer**:  Calls the scrapper module to compare two items of the same type.

The Text and Wiki blocks are independent, and the Reddit block imports and calls methods from both blocks.
