#To Dos

Will be updated with ongoing goals, tasks, updates, etc.

6.10.2018
- Need to setup better delimiters on log entries

3.10.2018
~~- New log files are not being created; all logging is done into a file from September 30th.~~ Changed FileHandler to TimedRotatingFileHandler.  New log files should be formatted with the correct date

27.9.2018
~~The spell checker failed to correct "dna stabilizers" to "DNA Stabilizer".  Need to add some .lower() to the comparisons.~~ Added a dictionary to spell_checkery.py, and check spelling but not case.
- Exceptions are logged into no-response log.  Check description in CephalonWikiLog.py
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
