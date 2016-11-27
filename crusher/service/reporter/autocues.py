import re

from bs4 import element, Comment

from core import *
from selectors import *
from actors import *
from evaluators import *

# Triggers:
(
        HTML,
        PRE_TRAVERSAL,
        EVAL_PARAGRAPH,
        EVAL_CONTAINER,
        POST_TRAVERSAL,
        NEWS_CONTAINER,
        NEWS_TEXT,
) = tuple(2**i for i in range(0,7))


class Autocue(list):

    def execute(self, tag, trigger):

        if isinstance(tag, element.Tag):
            # apply to tag

            for (s, t) in self:
                if trigger & t != 0:
                    if isinstance(s, Selector):
                        s.select(tag)
                    elif isinstance(s, Actor):
                        SingleTagSelector(s).select(tag)
                    elif isinstance(s, Evaluator):
                        SingleTagSelector(Scorer(s)).select(tag)
                    else:
                        pass

        else:
            # apply to text

            text = tag
            for (s, t) in self:
                if trigger & t != 0:
                    text = s.act(text)
            return text




# An Autocue is a list of tuples ( [[[Selector] Actor] Evaluator] , Trigger )
default_autocue = Autocue()


# Split a paragraph with two consecutive line breaks into two paragraphs
default_autocue.append((RegExReplacer(pattern='<br */? *>[ \r\n]*<br */? *>', repl='</p><p>'), HTML))


# Get rid of scripts, styles and comments
default_autocue.append((CSSSelector("script", Pruner()), PRE_TRAVERSAL))
default_autocue.append((CSSSelector("body > style", Pruner()), PRE_TRAVERSAL))
default_autocue.append((CommentSelector(Pruner()), PRE_TRAVERSAL))

default_autocue.append((CSSSelector("footer", Pruner()), PRE_TRAVERSAL))
default_autocue.append((CSSSelector("aside", Pruner()), PRE_TRAVERSAL))

default_autocue.append((CSSSelector("div#comments", Pruner()), PRE_TRAVERSAL))
default_autocue.append((CSSSelector("div.blogComments", Pruner()), PRE_TRAVERSAL))
default_autocue.append((CSSSelector("div.reacties", Pruner()), PRE_TRAVERSAL))
default_autocue.append((CSSSelector("div#ngn-footer", Pruner()), PRE_TRAVERSAL))
default_autocue.append((CSSSelector("div#section-footer-fn", Pruner()), PRE_TRAVERSAL))
default_autocue.append((CSSSelector("div#footer2010", Pruner()), PRE_TRAVERSAL))

#default_autocue.append((CSSSelector("footer > *", Scorer(FixedValue(-100, "footer"))), PRE_TRAVERSAL))
#default_autocue.append((BeautifulSelector(id=re.compile("credit|copyright|comment|meta|footer|footnote|foot"), actor=Scorer(FixedValue(-100, "negative_id"))), PRE_TRAVERSAL))
# Assign prior scores
#default_autocue.append((BeautifulSelector(name=re.compile("^h1|h2|post|hentry|entry|content|article$"), actor=Scorer(FixedValue(100, "positive_name"))), PRE_TRAVERSAL))
#default_autocue.append((BeautifulSelector(id=re.compile("caption|post|hentry|entry|content|article"), actor=Scorer(FixedValue(100, "positive_id"))), PRE_TRAVERSAL))
#default_autocue.append((BeautifulSelector(attrs=re.compile("caption|post|hentry|entry|content|body|article"), actor=Scorer(FixedValue(100, "positive_class"))), PRE_TRAVERSAL))
#default_autocue.append((BeautifulSelector(name=re.compile("footer|aside"), actor=Scorer(FixedValue(-100, "negative_name"))), PRE_TRAVERSAL))
#default_autocue.append((BeautifulSelector(id=re.compile("credit|copyright|comment|meta|footer|footnote|foot"), actor=Scorer(FixedValue(-100, "negative_id"))), PRE_TRAVERSAL))
#default_autocue.append((BeautifulSelector(attrs=re.compile("credit|copyright|comment|meta|footer|footnote|foot"), actor=Scorer(FixedValue(-100, "negative_class"))), PRE_TRAVERSAL))

default_autocue.append((CSSSelector("p", actor=Scorer(FixedValue(50, "paragraph"))), PRE_TRAVERSAL))
default_autocue.append((CSSSelector("h1", actor=Scorer(FixedValue(40, "header"))), PRE_TRAVERSAL))
default_autocue.append((CSSSelector("h2", actor=Scorer(FixedValue(50, "header"))), PRE_TRAVERSAL))
default_autocue.append((CSSSelector("h3", actor=Scorer(FixedValue(40, "header"))), PRE_TRAVERSAL))
default_autocue.append((CSSSelector("h4", actor=Scorer(FixedValue(30, "header"))), PRE_TRAVERSAL))

default_autocue.append((CSSSelector("div", actor=Scorer(FixedValue(-100, "div"))), PRE_TRAVERSAL))

# A paragraph is scored based on the number of words and comma's
default_autocue.append((Scorer(RegExMatcher(',', factor=10, name="comma"), reset_children=True), EVAL_PARAGRAPH))
default_autocue.append((Scorer(RegExMatcher("(\w)+(['`]\w)?", factor=2, name="word"), reset_children=True), EVAL_PARAGRAPH))
# Too many CAPITALIZED WORDS is usually a bad thing
default_autocue.append((Scorer(RegExMatcher('[A-Z]{4,}', factor=-10, name="caps")), EVAL_PARAGRAPH))
# This is a rather specific example
#default_autocue.append((Scorer(RegExMatcher('Photo credit:', factor=-50, name="photo_credit"), reset_children=True), EVAL_PARAGRAPH))
# Sum up the scores of the tags that are inside the paragraph
default_autocue.append((ScoreAggregator(start_score=0), EVAL_PARAGRAPH))

# Penalize containers
default_autocue.append((ScoreAggregator(start_score=-70, vmin=0), EVAL_CONTAINER))


# We don't like divs too much :-)
default_autocue.append((CSSSelector("div", Scorer(FixedValue(-60))), NEWS_CONTAINER))
# Get rid of any tags that have a score below -50
default_autocue.append((ScoreSelector(threshold=-50, mode="upper", actor=Pruner()), NEWS_CONTAINER))


# Put all text on one line
default_autocue.append((RegExReplacer(pattern='\s+', repl=' '), NEWS_TEXT))
# Trim left and right whitespace
default_autocue.append((RegExReplacer(pattern='^\s+|\s+$', repl=''), NEWS_TEXT))
