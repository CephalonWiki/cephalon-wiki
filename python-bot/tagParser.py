from CephalonWikiLogger import cephalon

# delimiters
detailed_delimiters = ["{{", "}}"]
simple_delimiters = ["{", "}"]

curly_delimiters = detailed_delimiters
square_delimiters = ["[", "]"]

# no one can request more than n articles at a time
article_request_limit = 10


# All-purpose parser for nested delimited statements
def get_tags(comment_string, open_del, close_del):

    edited_string = comment_string

    tags = {}
    while edited_string.rfind(open_del) >= 0:
        tag_start = edited_string.rfind(open_del)
        tag_end = edited_string.find(close_del, tag_start)
        if tag_end < tag_start:
            # no matching tags, truncate string and continue
            edited_string = edited_string[:tag_start]
        else:
            # found a matching tag
            tag = edited_string[tag_start+len(open_del):tag_end].strip()
            tags[edited_string.rfind(open_del + tag + close_del)] = tag

            # remove delimiters and continue
            edited_string = edited_string[:tag_start] + edited_string[tag_start+len(open_del):]
            edited_string = edited_string[:tag_end-len(open_del)] + edited_string[tag_end+len(close_del)-len(open_del):]

    return tags


# Formatting for scanning
def format_comment(comment_string):
    comment_paragraphs = comment_string.split("\n\n")

    for p in comment_paragraphs:
        if p.strip().startswith(">"):
            cephalon.warning("Ignoring paragraph in comment.  Reply Block:  " + p.replace("\n", "\t"))
            comment_paragraphs.remove(p)
        else:
            lines = p.split("\n")
            is_code = False
            for l in lines:
                if l.startswith("    "):
                    is_code = True
                    continue
                else:
                    # not a code block
                    is_code = False
                    break

            if is_code:
                cephalon.warning("Ignoring paragraph in comment.  Indented Block:  " + p.replace("\n", "\t"))
                comment_paragraphs.remove(p)

    return "\n\n".join(comment_paragraphs)


def format_tag(tag_string):
    return tag_string.replace("And", "and")\
                     .replace("Of","of")\
                     .strip()


# scan message, identify tags, and return a string containing all summaries
def get_tagged_articles(comment_string):
    comment_fm = format_comment(comment_string)

    ##############
    # DEPRECATED #
    ##############

    # detailed_tags = get_tags(comment_fm, *detailed_delimiters)
    # detailed_article_titles = {i: (detailed_tags[i], True) for i in detailed_tags if detailed_tags[i]}
    #
    # # need to remove detailed delimiters before checking for simple delimiters
    # comment_fm_rep = comment_fm.replace(detailed_delimiters[0], "").replace(detailed_delimiters[1], "")
    #
    # simple_tags = get_tags(comment_fm, *simple_delimiters)
    # simple_article_titles = {i: (simple_tags[i], False) for i in simple_tags if simple_tags[i]}
    #
    # contains only article titles
    # article_titles_bag = {**simple_article_titles, **detailed_article_titles}
    #
    # only keep article_request_limit many titles
    # article_titles = [article_titles_bag[i] for i in sorted(article_titles_bag.keys())[:article_request_limit]]

    #############
    # REVISIONS #
    #############

    # LEGACY:  extract (index, tag) pairs
    curly_tags = get_tags(comment_fm, *curly_delimiters)

    # LEGACY:  extract tags only
    curly_titles = [curly_tags[i] for i in sorted(curly_tags.keys()) if curly_tags[i]]

    # only keep article_request_limit many titles
    article_titles = [format_tag(t) for t in curly_titles[:article_request_limit]]

    return article_titles
