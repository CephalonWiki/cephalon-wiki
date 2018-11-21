#To Dos

Will be updated with ongoing goals, tasks, updates, etc.

16.11.2018

- The bot uses a now out-of-date article list that needs to be updated.
- Current list of articles for which retrieval fails:
  ~~- Excalibur Umbra:  Generalize treatment of Warframe names~~ Covered through overhaul of image-to-text replacement
  - Io:  No such article exists
  - Fire Prosecutor:  No such article exists
  - Adaptation:  Update article list for us in spell chcker
  - Lambeo Moa
  - Due to Redirects:  Requires new feature.  Can generalize code used to retrieve an article summary
    - Protective Dash: Vazarin#Protective_Dash
    - Arid Eviscertar:  Eviscerator#Variants
   

6.11.2018

~~- Retrieval for {Excalibur Umbra} failed.  Should redirect to Excalibur/Umbra.  Check details in scrapper.~~ 11.16.18 - Rolled up into list of articles

23.10.2018

~~ - Raspberry Pi has been freezing and exception log has been filling up with the following:  ~~

~~2018-10-23 00:00:28,792 - cephalon -  Exception raised:  error with request HTTPSConnectionPool(host='www.reddit.com', port=443): Max retries exceeded with url: /api/v1/access_token (Caused by NewConnectionError('<urllib3.connection.VerifiedHTTPSConnection object at 0xb54e42d0>: Failed to establish a new connection: [Errno -2] Name or service not known',))~~ 16.11.18 Changed reddit API configuration to create unique user agents for each instance of the bot. Increased sleep time to 5 minutes.
~~- Start and Recovery scripts not working on reboot?  Investigate file-paths~~ 16.11.18 - Updated file paths used in scripts.

13.10.2018

~~- Failure to retrieve details for {Protective Dash}.  scrapper routes request to http://warframe.wikia.com/wiki/Focus/Vazarin#Protective_Dash but no details were retrieved.  Write general scrapper to search 1 level down from url location for info.~~ - 11.16.18 Rolled up into list of articles


~~8.10.2018~~

~~- Bot does not respond to comment that contains {Sands of Inaros}~~ 8.10.2018 - This was a real clusterfuck.  So the format_comment method from tagParser changed "Sands of Inaros" to "Sands Of Inaros" (thanks to python's title() string method).  The wiki does not recognize the title with a capital O for of, so the request was sent to the error correction clauses in get_article_info from warframeWikiScrapper.  BUT, because "Sands" contains the word "and", the bot replaced it with %26 (code for the ampersand, because that's what the wiki uses), and sent "S%26s Of Inaros" to the spell checker which would try and try and eventually give up after several minutes.  format_comment() and get_article_info() have been updated to address this.  The moral of the story?  String replacement is dangerous.


6.10.2018

- Need to setup better delimiters on log entries


~~3.10.2018~~

~~- New log files are not being created; all logging is done into a file from September 30th.~~ Changed FileHandler to TimedRotatingFileHandler.  New log files should be formatted with the correct date


27.9.2018

~~The spell checker failed to correct "dna stabilizers" to "DNA Stabilizer".  Need to add some .lower() to the comparisons.~~ Added a dictionary to spell_checkery.py, and check spelling but not case.
~~- Exceptions are logged into no-response log.  Check description in CephalonWikiLog.py~~ 16.11.18 - Updated logger to filter messages
~~Articles not found:  Isolator Bursa~~ - Not replicated.  Currently works like a charm.
- Write a script to pull the current list of article_names (used in all_articles.py -> spell_checker.py) periodically.  Could save some API calls in warframeWikiScrapper


##16.9.2018

- Bot throws an exception when responding to a deleted comment.  Add clause to check for deletion in should_respond(comment)
- Standarize naming for python files
- Bot still responds to comments multiple times.  
  - Added extra logging to should_respond() to facilitate diagnosing the issue


##15.9.2018

~~Create git repository~~
~~Clone repository on Raspberry Pi~~
~~Create Dev Branch~~
~~Run Bot off of clone~~
- Write git script
