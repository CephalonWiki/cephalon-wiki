import re
from lxml import html
import requests

import warframeWikiScrapper


from CephalonWikiLogger import scrapper
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
        scrapper.warning("Fetching failed.  Searching for summary with main scrapper...")
        return warframeWikiScrapper.get_article_summary(title, info = title_article_info)


def get_subsection_summary(url, title, subsection_title):
    scrapper.info("Searching for subsection " + subsection_title + ".")

    # First, try to search directly by id
    try:
        id_summary = get_summary_by_id(url, title, subsection_title).strip()
        if id_summary not in ["", title, subsection_title]:
            scrapper.info("id search for " + subsection_title + " succeeded!")
            scrapper.info(id_summary)
            return id_summary
    except Exception:
        scrapper.error("id search for " + subsection_title + " failed.")

    # If that fails, try a text search by title
    try:
        title_summary = get_summary_by_title(url, title, subsection_title).strip()
        if title_summary not in ["", title, subsection_title]:
            scrapper.info("Title search for " + subsection_title + " succeeded!")
            scrapper.info(title_summary)
            return title_summary
    except Exception:
        scrapper.error("Title search for " + subsection_title + " failed.")

    # If all else fails, return nothing
    scrapper.warning("id and title searches for " + subsection_title + " were not successful!")
    return ""


def get_summary_by_id(url, title, subsection_id="mw-content-text"):
    # TO DO:  Fetch html with html5lib?
    article_tree = html.fromstring(requests.get(url).content)

    # Start search from tag with id specified in method call
    current_subsection = [];
    try:
        current_subsection = article_tree.get_element_by_id(subsection_id.replace(' ', '_'))
    except Exception:
        scrapper.error("id {} not found on {} page".format(subsection_id, title))
        return ""

    subsection_summary = ""
    found_summary = False

    # Exclusions
    string_blacklist = ["", "Edit", "Passive", "Passive, Way-Bound", "CODEX", title, subsection_id]
    tag_blacklist = ["figure", "table", "aside"]
    class_blacklist = ["codexflower", "cquote", "warframeNavBox"]
    element_blacklist = [];

    # Main loop
    while not found_summary:
        scrapper.info("Searching for summary in {}".format(current_subsection))

        # Drop extraneous tags
        if current_subsection.tag in tag_blacklist or current_subsection.get("class") in class_blacklist:
            scrapper.info("Current subsection in blacklist.  Moving up one level.")
            current_subsection = current_subsection.getparent()
            continue

        for r in current_subsection.getiterator(tag_blacklist):
            r.drop_tree()
            scrapper.info("Dropped tag {}".format(r))

        for c in class_blacklist:
            for r in current_subsection.xpath("//*[@class='{}']".format(c)):
                r.drop_tree()
                scrapper.info("Dropped class {}".format(r))

        # get list of descendants
        subsection_children = list(current_subsection.iter())

        # For a general article summary, take the first non-trivial tag containing the title
        for t in subsection_children:
            if title.lower() in t.text_content().lower() and t.text_content().strip() not in string_blacklist:
                subsection_summary = t.text_content().split(".\n")[0].strip() + "."
                scrapper.info("Found element {}".format(t))
                scrapper.info(subsection_summary)

                found_summary = True
                break

        if not found_summary:
            scrapper.info("No summary found.  Moving up one level.")
            element_blacklist.append(current_subsection)
            current_subsection = current_subsection.getparent()

    return subsection_summary


def get_summary_by_title(url, title, subsection_title):
    article_tree = html.fromstring(requests.get(url).content)

    # Find tag for article title
    title_tag = None
    found_title = False
    if subsection_title != "mw-content-text":
        content = article_tree.find('.//*[@id="mw-content-text"]')
        for t in content.iter():
            try:
                if t.get("id") == 'mw-content-text':
                    continue
                elif t.get("class") == 'pi-theme-ModBox Infobox_Parent':
                    t.drop_tree()
                    continue

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
        #scrapper.info("Title not found")
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

    scrapper.setLevel(CephalonWikiLogger.logging.WARNING)
    for t in test_cases:
        scrapper.warning("{}:  {}".format(t[0], t[1]))
        scrapper.warning(get_article_subsection(t[0], t[1]))
        scrapper.warning("==================")