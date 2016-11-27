from bs4 import element, Comment

from core import *
from actors import *
from evaluators import *
import core

class Selector(object):
    """Selects one or more tags and then calls the Actor"""

    def __init__(self, actor=None):
        self.actor = actor

    def select(self, tag):
        pass


class SingleTagSelector(Selector):

    def __init__(self, actor=None):
        Selector.__init__(self, actor)

    def select(self, tag):
        if isinstance(tag, element.Tag):
            self.actor.act(tag)


class CommentSelector(Selector):

    def __init__(self, actor=None):
        Selector.__init__(self, actor)

    def select(self, tag):
        for child in reversed(tag.find_all(text=lambda text:isinstance(text, Comment))):
            self.actor.act(child)


class ScoreSelector(Selector):

    def __init__(self, threshold=0, mode="upper", actor=None):
        Selector.__init__(self, actor)

        self.threshold = threshold
        self.mode = mode

    def select(self, tag):
        if isinstance(tag, element.Tag):
            for child in reversed(tag.find_all()):
                if not isinstance(tag, element.Tag):
                    continue
                score = core.get_total_score(child)

                if self.mode == "upper":
                    if score < self.threshold:
                        self.actor.act(child)
                else:
                    if score > self.threshold:
                        self.actor.act(child)


class CSSSelector(Selector):

    def __init__(self, select_string, actor=None):

        Selector.__init__(self, actor)
        self.select_string = select_string

    def select(self, tag):

        for child in reversed(tag.select(self.select_string)):
            if isinstance(tag, element.Tag):
                self.actor.act(child)


class BeautifulSelector(Selector):

    def __init__(self, actor=None, **kwargs):

        Selector.__init__(self, actor)
        self.args = kwargs

    def select(self, tag):

        for child in reversed(tag.find_all(**self.args)):
            if isinstance(tag, element.Tag):
                self.actor.act(child)
