import itertools
import datetime

import requests

import json
from lxml import html

import spell_checker

import tagParser

import CephalonWikiLogger


# Given an article title, searches for article on wiki
def get_article_info(title):
    CephalonWikiLogger.scrapper.info("Searching for info on %s.", title)

    # access article json and convert to a dictionary
    article_json = requests.get("http://warframe.wikia.com/api.php?action=query&titles=" + title.replace(" ", "_")
                                + "&prop=revisions&rvprop=content&format=json")
    article_dict = json.loads(article_json.content.decode('utf-8'))['query']['pages']

    # dictionary to populate and return
    article_info = dict()

    # extract article id for look-up and error checking
    article_info["id"] = list(article_dict.keys())[0]

    # positive id means article found
    if int(article_info["id"]) > 0:
        article_info["title"] = title.replace("%26", "&").replace("/", " ").replace(" Main", "").strip()
        article_info["url"] = "http://warframe.wikia.com/wiki/" + title.replace(" ", "_").replace("/Main", "")
    else:
        # If article is not found on first run, alter title and look up again, otherwise try search suggestions
        if "&" in title:
            return get_article_info(title.replace("&", "%26"))
        elif " and " in title:
            return get_article_info(title.replace(" and ", " %26 "))
        else:
            CephalonWikiLogger.scrapper.warning("Article info not found for %s.  Checking spelling.", title)

            # Use search suggestions to correct query, otherwise return blank dict
            suggestions_json = requests.get("http://warframe.wikia.com/api/v1/SearchSuggestions/List?query="
                                            + title.replace(" ", "_"))
            suggestions_dict = json.loads(suggestions_json.content.decode('utf-8'))["items"]

            if suggestions_dict:
                corrected_title = suggestions_dict[0]["title"]
                CephalonWikiLogger.spell_checker.warning("Search suggestion corrected %s to %s", title, corrected_title)

                return get_article_info(corrected_title)
            if spell_checker.correction(title) != title and len(title) > 2:
                corrected_title = spell_checker.correction(title)
                CephalonWikiLogger.spell_checker.warning("Spell checker corrected %s to %s", title, corrected_title)
                
                return get_article_info(corrected_title)
            else:
                CephalonWikiLogger.scrapper.warning("No spelling correction found for %s.", title)
                return article_info

    # attempt to determine article type and codex entry
    article_type = ""
    codex_entry = ""
    article_tags = {}
    try:
        # article_dump contains codex entry and useful tags for classification of article type
        article_dump = article_dict[article_info["id"]]["revisions"][0]['*'].strip()
        if article_dump.lower().startswith("#redirect"):
            return get_article_info(article_dump[article_dump.index("[[") + 2:article_dump.index("]]")])
        else:
            article_tags = tagParser.get_tags(article_dump, "{{", "}}")

        # Determining type and codex
        for i in sorted(article_tags):
            t = article_tags[i]
            if t == ":" + title + "/Main":
                # redirect for Warframes and Archwings
                return get_article_info(t[1:])
            elif "\n| name" in t:
                article_type = t[:t.find("\n| name")].strip()
            elif "ModBox" in t:
                article_type = "ModBox"
            elif t == "WeaponNav":
                #  or "|Weapons" in t or
                article_type = "Weapon"
            elif t.lower().startswith("codex|"):
                codex_entry = t.split("|")[1].strip()
                if not codex_entry.endswith("."):
                    codex_entry += "."
    except KeyError as e:
        CephalonWikiLogger.scrapper.error("KeyError: with " + str(e) + " for title " + title)

    # Assemble look up information into dictionary
    article_info["type"] = article_type
    article_info["codex"] = codex_entry
    article_info["tags"] = article_tags

    return article_info


def format_polarity(mod_polarity):
    polarity_letter = ""
    if mod_polarity == "Madurai":
        polarity_letter = "V"
    elif mod_polarity == "Vazarin":
        polarity_letter = "D"
    elif mod_polarity == "Naramon":
        polarity_letter = "-"
    elif mod_polarity == "Unairu":
        polarity_letter = "R"
    elif mod_polarity == "Zenurik":
        polarity_letter = "="
    elif mod_polarity == "Penjaga":
        polarity_letter = "Y"

    return "  Polarity:  " + mod_polarity + " (" + polarity_letter + ").  "


def get_article_summary(title, detail=False):
    article_info = get_article_info(title)

    if int(article_info["id"]) > 0:

        # formatting for reddit comment
        url_fm = "###[" + article_info["title"] + "](" + article_info["url"] + ")"

        # If we don't need the detail, don't bother looking it up
        if not detail and article_info["codex"] and article_info["type"] not in ["Warframe", "Archwing"]:
                return [url_fm, article_info["codex"]]

        # main processing
        article_main = requests.get(article_info["url"])
        article_tree = html.fromstring(article_main.content)

        #
        # find general article summary
        #
        article_summary = ""
        if not article_summary or len(article_summary) > 400 or title not in article_summary:
            for p in article_tree.findall('.//*[@id="mw-content-text"]/p'):
                if article_info["title"] in p.text_content():

                    # Set the text of all the /a/img objects (e.g. Polarities, Currency)
                    for i in p.findall('./a/img'):
                        i.text = i.get('alt').replace(' Pol', '')

                    article_summary = p.text_content().strip().replace("\xa0", " ")
                    CephalonWikiLogger.scrapper.debug(article_summary)
                    break

            # if we do not find an article summary from p tags, take first text paragraph
            if not (article_summary and article_info["title"] in article_summary):
                try:
                    paragraph = filter(lambda s: title in s and title != s,
                                       article_tree.find('.//*[@id="mw-content-text"]').text_content().split(
                                           "\n")).__next__()
                    article_summary = paragraph.strip().replace("\xa0", "")
                except Exception:
                    article_summary = "Sorry, no summary is availablebleblebleble... Hmm... I will attempt to bypass this fault."
                    CephalonWikiLogger.scrapper.error("No summary available for %s", article_info["title"])

        #
        # processing for the aside
        #
        article_asides = list(filter(lambda a: a.findall('./h2')[0].text_content().strip() == article_info["title"],
                                     article_tree.findall('.//aside')))
        aside_titles = [""]
        aside_line = [""]
        aside_info = [""]
        aside_table = ""

        if article_asides:
            article_aside = article_asides[0]
            aside_titles = []
            aside_line = []
            aside_info = []

            # filter terms for aside by type
            weapon_filters = ["Mastery", "Type", "Polarities", "Total Damage", "Stance Polarity"]
            warframe_filters = ["Mastery Rank", "Polarities", "Aura Polarity"]
            comp_filters = ["Polarities", "Default Weapon", "Exclusive Mods"]
            mod_filters = ["Polarity"]
            aside_filters = {"": [],
                             "Weapon": weapon_filters,
                             "Warframe": warframe_filters,
                             "Archwing": warframe_filters,
                             "Sentinel": comp_filters,
                             "Kubrow": comp_filters,
                             "Kavat": comp_filters,
                             "ModBox": mod_filters,
                             "Quest": [],
                             "Component": []}
            aside_filter = []
            try:
                aside_filter = aside_filters[article_info["type"]]
            except KeyError as e:
                CephalonWikiLogger.scrapper.error("KeyError " + str(e) + " with title " + title + " and type " + article_info["type"])

            current_subheader = None
            aside_sections = list(itertools.chain(*map(lambda tag: tag.getchildren(), article_aside.findall('./section'))))
            for t in article_aside.getchildren() + aside_sections:
                if t.tag == "h2":
                    current_subheader = t
                    continue

                elif t.tag == "div":
                    div = t
                    div_headers = div.findall('./h3')

                    if div_headers:
                        div_title = div_headers[0].text_content().strip()
                    else:
                        continue

                    # filter for specific entries
                    if div_title not in aside_filter:
                        continue

                    # Replace images with their alt text
                    for tag in div.findall('.//a/img'):
                        if "Pol" in tag.get('alt'):
                            tag.text = tag.get('alt').replace('Pol', '')
                        elif " b" in tag.get('alt'):
                            tag.text = tag.get('alt').replace(' b', '')

                    div_info = div.text_content().strip()[len(div_title):].strip()

                    if "Polarit" in div_title:
                        if "None" in div_info:
                            div_info = "None"
                            aside_info.append(div_title + "|" + div_info)
                            continue

                    elif "Total Damage" == div_title:
                        div_title = current_subheader.text_content().strip()

                    elif div_title in ["Exclusive Mods", "Variants"]:
                        div_links = list(map(lambda a: a.text_content(),
                                             div.findall("./div//a")))
                        div_info = ", ".join(div_links)

                    aside_titles.append(div_title.strip())
                    aside_line.append(":----------:")
                    aside_info.append(div_info.strip())

            if article_info["type"] in ["Kubrow", "Kavat"]:
                # find ability mods and add to aside_table
                pass

            if aside_titles:
                aside_table = "|" + "|\n|".join(map(lambda l: "|".join(l), [aside_titles, aside_line, aside_info])) + "|"

        #
        # summary prep by type
        #

        # Warframes and Archwings
        if article_info["type"] in ["Warframe", "Archwing"]:
            if detail:
                # find and process abilities for non-Umbras
                ability_summaries_fm = ""
                if "Umbra" not in article_info["title"]:
                    ability_tags = get_article_info(article_info["title"].replace(" Prime", "") + "/Abilities")["tags"]
                    ability_list = [ability_tags[i][1:] for i in sorted(ability_tags) if ":" in ability_tags[i]]
                    ability_summaries = list(map(get_article_summary, ability_list))
                    ability_summaries_fm = "Abilities:  " + ", ".join(list(map(lambda l: l[0][3:], ability_summaries)))

                # find acquisition info for non-primes
                acquisition_summary = ''
                if "Prime" not in article_info["title"]:
                    for p in article_tree.findall('.//*[@id="mw-content-text"]/div/div/div/p'):
                        acquisition_info = p.text_content().strip()
                        if "component" in acquisition_info.lower() and "blueprint" in acquisition_info.lower():
                            acquisition_summary = acquisition_info.split(". ")[0] + "."
                            break

                return [url_fm, article_summary, ability_summaries_fm, aside_table, acquisition_summary]
            else:
                return [url_fm, article_summary]
        # ABILITIES
        elif "AbilityU" in article_info["type"]:
            ability_summary = article_tree.findall('.//*[@id="mw-content-text"]/table/tr[1]/td[3]')[0].text_content().replace(article_info["title"], "", 1).replace("s−1", "per second.  ").strip()
            energy_cost = "Energy Cost:  " + article_tree.findall('.//*[@id="mw-content-text"]/table/tr[1]/td[2]/span[1]')[0].text_content()

            if ability_summary[-1] != ".":
                ability_summary += "."

            return [url_fm, ability_summary, energy_cost]

        # Mods and Arcanes
        elif article_info["type"] == "Component" and "Arcane" in article_info["title"] or article_info["type"] == "ModBox":

            if not detail:
                return [url_fm, article_summary]

            # Gather data from table
            stats_tables = article_tree.findall('.//*[@class="emodtable"]')
            stats_string = ""

            if len(stats_tables) > 0:
                stats_table = stats_tables[0]
                rows = stats_table.getchildren()
                no_columns = len(rows[0].getchildren())

                stats_strings = []
                for i in [0, .5, 1, -1]:
                    if i == .5:
                        row_string = (":---------:|" * no_columns)[:-1]
                    else:
                        row = rows[i].getchildren()
                        row_string = "|".join([s.text_content().strip() for s in row])

                    stats_strings.append(row_string)

                stats_string = "\n".join(stats_strings)

            # package and return
            if "Arcane" in article_info["title"]:
                return [url_fm, article_summary, stats_string]
            else:
                mod_polarity = aside_info[-1]
                mod_summary = article_summary + format_polarity(mod_polarity)
                return [url_fm, mod_summary, stats_string]

        elif article_info["type"] == "Quest":
            spoiler_summary = "[Spoiler:](#s '" + article_summary + "')"
            return [url_fm, spoiler_summary, aside_table]

        # CATCH ALL:  Companions, etc.
        else:
            return [url_fm, article_summary, aside_table]
    else:
        return []
