from bs4 import element
from matplotlib.cm import ScalarMappable, RdYlGn

from selectors import *
from actors import *
from evaluators import *

from numpy import log


def score_to_rgb(score, sm, min_score, max_score):
    """Only used for debugging"""

    if score > 0:
        score = log(score)
        val = 0.5 + ((score/float(max_score))/2.5)
    elif score < 0:
        score = -log(-score)
        val = 0.5 - ((score/float(min_score))/2.5)
    else:
        val = 0.5
    r, g, b, a = sm.to_rgba(val)
    return (int(r*255), int(g*255), int(b*255))


def style_all_tags(soup, container, background=True, margin=None, border=False, css=True, images=True, only_container=False):
    """Only used for debugging"""

    #if only_container:
        #soup = container

    (min_score, max_score) = get_min_and_max_scores(soup)
    min_score = -log(-min_score)
    max_score = log(max_score)

    sm = ScalarMappable(cmap=RdYlGn)
    sm.set_clim(0,1)

    if not css:
        for link in soup.find_all("link"):
            link.decompose()

    if not images:
        for img in soup.find_all("img"):
            img.decompose()

    for tag in soup.find_all():

        if not isinstance(tag, element.Tag):
            continue

        if css:
            try:
                style = tag["style"].split(";")
            except:
                style = []
        else:
            style = []

        if margin is not None:
            if margin > 0:
                style.append("margin: %dpx" % margin)

        try:
            score = sum(tag.scores.values())
            rgb = score_to_rgb(score, sm, min_score, max_score)
            tag.scores['total'] = score
        except:
            score = -1
            rgb = (230, 230, 230)

        if background:
            style.append("background-color: rgb(%d,%d,%d)" % rgb)

        try:
            if tag in container.descendants and score > -30:
                style.append("color: #000000")
            else:
                style.append("color: #666666")
        except:
            pass

        if tag == container:
            style.append("border: 3px dashed #0000CC")
            style.append("color: #000000")
        else:
            if border:
                style.append("border: 1px solid #333333")

        try:
            tag['style'] = "; ".join(style)
            tag['scores'] = repr(tag.scores)
            del tag.scores['total']
        except:
            pass


def get_min_and_max_scores(tag):

    min_score = -10
    max_score = 10

    for child in tag.find_all():
        score = get_total_score(child)
        min_score = min(min_score, score)
        max_score = max(max_score, score)

    return (min_score, max_score)


def get_tag_with_max_score(tag):

    max_child = None
    max_score = -10000

    for child in tag.find_all():
        if child is not None:
            score = get_total_score(child)
            if score >= max_score:
                max_score = score
                max_child = child

    return max_child


def get_total_score(tag):
    try:
        return sum(tag.scores.values())
    except:
        return 0
