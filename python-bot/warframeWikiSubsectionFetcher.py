import re
from lxml import html
import requests
from pprint import pprint

import warframeWikiScrapper
import CephalonWikiLogger

def get_article_subsection(title, subsection= "mw-content-text"):
    title_article_info = warframeWikiScrapper.get_article_info(title)
    url_fm = "###[{2}](https://warframe.fandom.com{1}#{2})".format(title_article_info["title"], title_article_info["url"], subsection)

    subsection_summary = get_subsection_summary("https://warframe.fandom.com" + title_article_info["url"], title, subsection)

    if subsection_summary:
        # Text processing
        subsection_summary = subsection_summary.strip().replace("\xa0", " ").replace("  ", " ")

        if subsection_summary.startswith("CODEX"):
            subsection_summary = subsection_summary[5:]

        return [url_fm, subsection_summary]
    else:
        # If we find nothing, stick with the old logic and return the page summary
        CephalonWikiLogger.scrapper.warning("Fetching failed.  Searching for summary with main scrapper...")
        return warframeWikiScrapper.get_article_summary(title, info = title_article_info)

def get_subsection_summary(url, title, subsection_title):
    CephalonWikiLogger.scrapper.info("Searching for subsection " + subsection_title + ".")

    # First, try to search directly by id
    try:
        if get_summary_by_id(url, title, subsection_title).strip() not in ["", title, subsection_title]:
            CephalonWikiLogger.scrapper.info("id search for " + subsection_title + " succeeded!")
            return get_summary_by_id(url, subsection_title)
    except Exception:
        CephalonWikiLogger.scrapper.error("id search for " + subsection_title + " failed.")

    # If that fails, try a text search by title
    try:
        if get_summary_by_title(url, title, subsection_title).strip() not in ["", title, subsection_title]:
            CephalonWikiLogger.scrapper.info("Title search for " + subsection_title + " succeeded!")
            return get_summary_by_title(url, subsection_title)
    except Exception:
        CephalonWikiLogger.scrapper.error("Title search for " + subsection_title + " failed.")

    # If all else fails, return nothing
    CephalonWikiLogger.scrapper.warning("id and title searches for " + subsection_title + " were not successful!")
    return ""


def get_summary_by_id(url, title, subsection_title):
    article_tree = html.fromstring(requests.get(url).content)

    title_tag = article_tree.get_element_by_id(subsection_title.replace(' ', '_'))

    current_subsection = title_tag
    subsection_summary = ""
    status = False
    blacklist = ["", "Edit", "Passive", "Passive, Way-Bound", title, subsection_title]
    tag_blacklist = ["figure", "table", "aside"]

    while not subsection_summary:
        for r in current_subsection.getiterator(tag_blacklist):
            r.drop_tree()

        subsection_children = list(current_subsection.iter())

        if subsection_title == 'mw-content-text':
            for t in subsection_children[subsection_children.index(title_tag)+1:]:
                if t.tag == 'p' and title.lower() in t.text_content().lower() and t.text_content().strip() not in blacklist:
                    subsection_summary = t.text_content().strip()
                    status = True
                    break

            if status == True:
                break

        for t in subsection_children[subsection_children.index(title_tag)+1:]:
            if t.text_content().strip() not in blacklist:
                subsection_summary = t.text_content().strip()
                status = True
                break

        if status == True:
            break
        elif status == False:
            current_subsection = current_subsection.getparent()

    return subsection_summary

def get_summary_by_title(url, title, subsection_title):
    article_tree = html.fromstring(requests.get(url).content)

    # Find tag for article title
    title_tag = None
    found_title = False
    if subsection_title != "mw-content-text":
        for t in article_tree.find('.//*[@id="mw-content-text"]').iter():
            try:
                if t.text_content().strip() == subsection_title or subsection_title in t.text_content().strip().split("\n\n"):
                    title_tag = t
                    found_title = True
                    break
            except Exception:
                continue
    else:
        title_tag = article_tree.get_element_by_id("mw-content-text")
        found_title = True


    # If we find nothing, no point in continuing
    if not found_title:
        #print("Title not found")
        return ""

    # Will start looking one level above the title.  We consider all children occurring after the title,
    # in depth-first order.  As a check for shitty HTML, at the end we will trim current_subsection to try
    # and obtain a summary
    current_subsection = title_tag.getparent()
    subsection_summary = ""
    found_summary = False

    # Filters to skip non-summaries
    blacklist = ["", "Edit", "Passive", "Passive, Way-Bound", title, subsection_title]
    tag_blacklist = ["figure", "table", "aside"]

    while not subsection_summary:
        for r in current_subsection.getiterator(tag_blacklist):
            r.drop_tree()

        subsection_children = list(current_subsection.itertext())
        child_list = []
        if subsection_title != "mw-content-text":
            child_list = subsection_children[subsection_children.index(title_tag.text_content().strip())+1:]
        else:
            child_list = subsection_children

        for t in child_list:
            if t.strip() not in blacklist:
                subsection_summary += t
                found_summary = True

                if t.endswith(".\n"):#?????????????
                    break

        if found_summary:
            break
        else:
            current_subsection = current_subsection.getparent()

    return subsection_summary.strip()

if __name__ == "__main__":
    test_cases = [("Mirage", "Hall of Mirrors"),
                  ("Mirage/Abilities", "Hall of Mirrors"),
                  ("Focus/Vazarin", "Protective Dash"),
                  ("Vazarin", "Protective Dash"),
                  ("Focus", "Protective Dash"),
                  ("Ephemera", "Freezing Step"),
                  ("Ephemera", "Smoking Body"),
                  ("Orbiter", "Landing Craft"),
                  ("Critical Hit", "Crit Tiers"),
                  ("Fishing", "Mortus Lungfish")]

    for t in test_cases:
        pprint("\n")
        pprint(t[1])
        pprint("==================")
        pprint(get_article_subsection(t[0], t[1]))
        pprint("++++++++++++++")