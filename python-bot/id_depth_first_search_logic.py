from lxml import html
import requests
from pprint import pprint

def get_summary_by_id(url, subsection_title):
    article_tree = html.fromstring(requests.get(url).content)

    try:
        title_tag = article_tree.get_element_by_id(subsection_title.replace(' ', '_'))
    except Exception:
        print("id search:  Exception encountered with " + subsection_title)
        return ""

    current_subsection = title_tag
    subsection_summary = ""
    found_summary = False
    blacklist = ["", "Edit", "Passive", "Passive, Way-Bound", subsection_title]

    while not subsection_summary:
        subsection_children = list(current_subsection.iter())
        for t in subsection_children[subsection_children.index(title_tag):]:
            if t.text_content().strip() not in blacklist:
                subsection_summary = t.text_content().strip()
                found_summary = True
                break

        if found_summary:
            break
        else:
            current_subsection = current_subsection.getparent()

    return subsection_summary

def get_summary_by_title(url, subsection_title):
    article_tree = html.fromstring(requests.get(url).content)

    # Find tag for article title
    title_tag = None
    found_title = False
    for t in article_tree.find('.//*[@id="mw-content-text"]').iter():
        try:
            #print(t.text_content().strip(), t.text_content().strip() == subsection_title)
            if t.text_content().strip() == subsection_title:
                #print(t.text_content().strip() == subsection_title)
                title_tag = t
                found_title = True
                break
        except Exception:
            continue

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
    blacklist = ["", "Edit", "Passive", "Passive, Way-Bound", subsection_title]

    while not subsection_summary:
        subsection_children = list(current_subsection.itertext())
        #print(subsection_children)
        for t in subsection_children[subsection_children.index(title_tag.text_content().strip()) + 1:]:
            if t.strip() not in blacklist:
                subsection_summary += t
                found_summary = True

                if t.endswith("\n"):
                    break

        if found_summary:
            break
        else:
            current_subsection = current_subsection.getparent()

    return subsection_summary.strip()

test_cases = [("https://warframe.fandom.com/wiki/Mirage", "Hall of Mirrors"),
              ("https://warframe.fandom.com/wiki/Mirage/Abilities", "Hall of Mirrors"),
              ("https://warframe.fandom.com/wiki/Focus/Vazarin", "Protective Dash"),
              ("https://warframe.fandom.com/wiki/Ephemera", "Freezing Step")]

for t in test_cases:
    print("\n")
    print(t[1])
    print("==================")
    print(get_summary_by_id(t[0], t[1]))
    print("++++++++++++++")
    print(get_summary_by_title(t[0], t[1]))
    print("++++++++++++++")