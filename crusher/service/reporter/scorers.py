from bs4 import BeautifulSoup, element
import re
from matplotlib.cm import ScalarMappable, RdYlGn

from core import *
from selectors import *
from actors import *
from evaluators import *
from autocues import *

# Triggers:








policy = ScoringPolicy()

policy.append((ScoreAggregator(), EVAL_CONTAINER))
policy.append((RegExCounter(",", 1), EVAL_PARAGRAPH))
policy.append((Limiter(RegExCounter("(\w)+(['`]\w)?", 1), 20), EVAL_PARAGRAPH))
policy.append((CSSSelector("a", Scorer(FixedValue(-50))), PRE_TRAVERSAL))
policy.append((ScoreSelector(Pruner()), POST_TRAVERSAL))

#policy['parent'] = (ParentScorer(), EVAL_CONTAINER) # aggregates scores from children
#policy['commas'] = (RegExCountScorer(",", 1), EVAL_PARAGRAPH)
#policy['words'] = (RegExCountScorer("(\w)+(['`]\w)?", 1), EVAL_PARAGRAPH)
#policy['children'] = (CountChildrenScorer("p", 10), EVAL_CONTAINER)
#policy['paragraph'] = (FixedValueScorer(1), EVAL_PARAGRAPH)
#policy['container'] = (FixedValueScorer(1), EVAL_CONTAINER)

if __name__ == '__main__':

    html_doc = """ <html><head><title>The Dormouse's story</title></head><body><div><p class="title"><b>The Dormouse's story</b></p> <p class="story">Once upon a time there were three little sisters; and their names were <a href="http://example.com/elsie" class="sister" id="link1">Elsie</a>, <a href="http://example.com/lacie" class="sister" id="link2">Lacie</a> and <a href="http://example.com/tillie" class="sister" id="link3">Tillie</a>; and they lived at the bottom of a well.</p> <p class="story">...</p></div></body></html>"""

    soup = BeautifulSoup(html_doc)

    for tag in reversed(soup.find_all(["p","a","b"])):
        policy.execute(tag, EVAL_PARAGRAPH)

    policy.execute(soup, PRE_TRAVERSAL)

    policy.execute(soup.find("body"), EVAL_CONTAINER)

    for tag in soup.find_all():
        print tag.name, "=", tag.scores

    container = get_tag_with_max_score(soup)

    style_all_tags(soup, container)

    html_styled = soup.find("body").prettify(formatter="html")

    policy.execute(container, POST_TRAVERSAL)
    print container.get_text()
