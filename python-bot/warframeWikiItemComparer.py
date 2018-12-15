import itertools
import collections

import requests

from lxml import html

import warframeWikiScrapper

import CephalonWikiLogger


# filter terms for aside by type
weapon_filters = ["Mastery", "Average DPS", "Fire Rate", "Charge Time", "Crit Chance",
                  "Crit Multiplier", "Status Chance", "Polarities", "Total Damage", "Stance Polarity", "Attack Speed",
                  "Block Resist."]
warframe_filters = ["Mastery Rank", "Health", "Shield", "Armor", "Energy", "Power", "Sprint Speed",
                    "Polarities", "Aura Polarity"]
comp_filters = ["Health", "Shield Capacity", "Armor", "Power", "Slash", "Crit Chance", "Crit Multiplier",
                "Status Chance", "Polarities", "Default Weapon", "Exclusive Mods"]
aside_filters = {"Weapon": weapon_filters,
                 "Warframe": warframe_filters,
                 "Archwing": warframe_filters,
                 "Sentinel": comp_filters,
                 "Kubrow": comp_filters,
                 "Kavat": comp_filters}


def get_item_stats(title):
    article_info = collections.OrderedDict(warframeWikiScrapper.get_article_info(title))

    # aside_table = ""
    if int(article_info["id"]) > 0 and article_info["type"] in ["Weapon", "Warframe", "Archwing", "Sentinel", "Kubrow", "Kavat"]:

        # formatting for reddit comment
        # url_fm = "###[" + article_info["title"] + "](" + article_info["url"] + ")"

        # main processing #
        article_main = requests.get(article_info["url"])
        article_tree = html.fromstring(article_main.content)

        # processing for the aside
        article_asides = list(filter(lambda a: a.findall('./h2')[0].text_content().strip() == article_info["title"],
                                     article_tree.findall('.//aside')))
        # aside_titles = [""]
        # aside_line = [""]
        # aside_info = [""]
        # aside_table = ""

        if article_asides:

            # entire side table in an HTML format
            article_aside = article_asides[0]

            # DEPRECATED
            # aside_titles = []
            # aside_line = []

            # List to collect lines of response
            aside_info = []

            # load the appropriate filter based on item type
            aside_filter = aside_filters[article_info["type"]]

            # keep track of current sub-header/sub-section in the aside, stats are added to a new dictionary using
            # current_subheader as key
            current_subheader = None

            # list of sub-sections (different from sub-headers)
            aside_sections = list(itertools.chain(*map(lambda tag: tag.getchildren(), article_aside.findall('./section'))))

            # loop through tags under the main section
            for t in article_aside.getchildren() + aside_sections:

                # For headers, we collect some general data under a new, generic "Main" section, or multiple Attack
                # sections under the "Normal Attacks" section
                if t.tag == "h2":
                    current_subheader = t.text_content().strip()

                    if current_subheader == article_info["title"] or current_subheader in ["Statistics", "Utility", "Miscellaneous"]:
                        current_subheader = "Main"
                    elif current_subheader == "Other Attacks":
                        current_subheader = "Normal Attacks"
                    elif "Semi-Auto" in current_subheader:
                        current_subheader = "Normal Attacks"
                    else:
                        pass

                    if current_subheader not in article_info:
                        article_info[current_subheader] = collections.OrderedDict()

                    # aside_titles.append(div_title.strip())
                    # aside_line.append(":----------:")
                    # aside_info.append(div_info.strip())

                # Otherwise, we're looking at a div.
                elif t.tag == "div":
                    div = t
                    div_headers = div.findall('./h3')

                    if div_headers:
                        div_title = div_headers[0].text_content().strip()
                    else:
                        # print("Empty header")
                        continue

                    # filter for specific entries
                    if div_title not in aside_filter:
                        # print("Skipping ", div_title)
                        continue

                    div_text = div.text_content().strip()[len(div_title):].strip()
                    div_info = ""

                    if "Polarit" in div_title:
                        if "None" in div_text:
                            div_info = "None"
                            aside_info.append(div_title + "|" + div_info)
                            continue

                        polarity_list = list(map(lambda tag: tag.get("alt").replace(" Pol", ""),
                                                 div.findall('./div/a/img')))
                        polarity_mults = div_text.strip().split()
                        if not polarity_mults:
                            polarity_mults = [""] * len(polarity_list)

                        for i in range(len(polarity_list)):
                            if polarity_mults[i] != "":
                                div_info += polarity_list[i] + " " + polarity_mults[i] + ", "
                            else:
                                div_info += polarity_list[i] + ", "
                        div_info = div_info[:-2]
                    elif "Total Damage" == div_title:
                        damage_type = div.findall('./div//a/img')[0].get("alt").replace(" b", "")
                        if "(" in div_text:
                            div_info = div_text.replace("(", "(" + damage_type)
                        else:
                            div_info = damage_type + " " + div_text
                    elif div_title in ["Exclusive Mods", "Variants"]:
                        div_links = list(map(lambda a: a.text_content(),
                                             div.findall("./div/a") + div.findall("./div/span/a")))
                        div_info = ", ".join(div_links)
                    # elif "Fire Rate" == div_title and "Charge Time" in article_info[current_subheader]:
                    #     div_info = article_info[current_subheader]["Charge Time"].strip()[0]
                    else:
                        div_info = div_text

                    # aside_titles.append(div_title.strip())
                    # aside_line.append(":----------:")
                    # aside_info.append(div_info.strip())

                    article_info[current_subheader][div_title] = div_info

            # if aside_titles:
            #     # aside_dict = {aside_titles[i]: aside_info[i] for i in len(aside_titles)}
            #     aside_table = "|" + "|\n|".join(map(lambda l: "|".join(l), [aside_titles, aside_line, aside_info])) + "|"

        article_info.__delitem__("tags")
        article_info.__delitem__("codex")
        article_info.__delitem__("id")
        if "Charged Shot" in article_info:
            article_info["Main Attack"] = article_info["Charged Shot"]
            del article_info["Charged Shot"]

            if "Uncharged Shot" in article_info:
                del article_info["Uncharged Shot"]
        if "Charge Attacks" in article_info:
            article_info["Main Attack"] = article_info["Charge Attacks"]
            del article_info["Charge Attacks"]
            if "Normal Attacks" in article_info:
                del article_info["Normal Attacks"]
        if "Normal Attacks" in article_info:
            article_info["Main Attack"] = article_info["Normal Attacks"]
            del article_info["Normal Attacks"]
        # if "Main" in article_info and article_info["title"] in article_info:
        #     article_info["Main"] = article_info[article_info["title"]]
        #     del article_info[article_info["title"]]

        # processing to remove units and unnecessary text from weapon stats
        if article_info["type"] == "Weapon":
            if "Fire Rate" in article_info["Main"]:
                fire_rate = float(article_info["Main"]["Fire Rate"].split()[0])
                article_info["Main"]["Fire Rate"] = str(fire_rate)
            elif "Attack Speed" in article_info["Main"]:
                fire_rate = float(article_info["Main"]["Attack Speed"].split()[0])
                article_info["Main"]["Attack Speed"] = str(fire_rate)
            # article_info["Main"]["Magazine Size"] = article_info["Main"]["Magazine Size"].split()[0]
            # article_info["Main"]["Max Ammo"] = article_info["Main"]["Max Ammo"].split()[0]

            if "Main Attack" in article_info:

                total_damage = article_info["Main Attack"]["Total Damage"].split()
                damage = 0
                if len(total_damage) == 2:
                    damage = float(total_damage[1])
                elif len(total_damage) == 3:
                    damage = float(total_damage[0])

                crit_chance = float(article_info["Main Attack"]["Crit Chance"][:-1])/100
                crit_damage = float(article_info["Main Attack"]["Crit Multiplier"][:-1])

                if "Fire Rate" in article_info["Main Attack"]:
                    fire_rate = float(article_info["Main Attack"]["Fire Rate"].split()[0])

                    if "Charge Time" in article_info["Main Attack"]:
                        charge_time = float(article_info["Main Attack"]["Charge Time"].split()[0])
                        article_info["Main Attack"]["Charge Time"] = str(charge_time)

                        if int(fire_rate) == 0:
                            fire_rate = int(1/charge_time)

                    article_info["Main"]["Fire Rate"] = str(fire_rate)
                    article_info["Main Attack"].__delitem__("Fire Rate")

                adps = damage * fire_rate * (crit_chance * (crit_damage - 1) + 1)
                article_info["Main Attack"]["Average DPS"] = str(int(adps))
                
        return article_info
    else:
        article_info.__delitem__("id")
        return article_info


def compare_items(item1, item2):
    item1_dict = get_item_stats(item1.strip())
    item2_dict = get_item_stats(item2.strip())

    titles = ["Item"]
    url_fm1 = "[" + item1_dict["title"] + "](" + item1_dict["url"] + ")"
    url_fm2 = "[" + item2_dict["title"] + "](" + item2_dict["url"] + ")"
    item1_info = [url_fm1]
    item2_info = [url_fm2]

    if not (item1_dict or item2_dict) or item1_dict["type"] != item2_dict["type"]:
        return None
    elif item1_dict["type"] == "ModBox":
        return warframeWikiScrapper.get_article_summary(item1, True) + ["*****"] \
               + warframeWikiScrapper.get_article_summary(item2, True)
    else:
        common_keys = [k for k in item1_dict.keys() if k in item2_dict.keys()]

        for header in common_keys[::-1]:
            if header in ["url", "type", "title"]:
                continue
            else:
                stat_names = [name for name in item1_dict[header].keys() if name in item2_dict[header].keys()]
                if header == "Main Attack":
                    stat_names = [stat_names[-1]] + stat_names[:-1]

                for stat_name in stat_names:
                    if stat_name == "Total Damage":
                        titles.append(header)
                    else:
                        titles.append(stat_name)
                    item1_info.append(item1_dict[header][stat_name])
                    item2_info.append(item2_dict[header][stat_name])

        lines = [":---------:"] * len(titles)
        aside_table = "|" + "|\n|".join(map(lambda l: "|".join(l), [titles, lines, item1_info, item2_info])) + "|"
        return [aside_table]



