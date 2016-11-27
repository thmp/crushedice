from bs4 import element

from core import *
from selectors import *
from evaluators import *

class Actor(object):
    """Acts on one tag"""

    def __init__(self, evaluator=None):
        self.evaluator = evaluator

    def act(self, tag):
        pass


class Scorer(Actor):

    def __init__(self, evaluator, reset_children=False):
        Actor.__init__(self, evaluator)
        self.reset_children = reset_children

    def act(self, tag):

        if tag.scores is None:
            tag.scores = dict()
        tag.scores[self.evaluator.name] = self.evaluator.evaluate(tag)

        if self.reset_children:
            for child in tag.descendants:
                try:
                    del child.scores[self.evaluator.name]
                except:
                    pass


class Pruner(Actor):

    def __init__(self, evaluator=None):
        Actor.__init__(self, evaluator)

    def act(self, tag):
        if self.evaluator is not None:
            if self.evaluator.evaluate(tag) >= 1:
                try:
                    tag.decompose()
                except:
                    tag.replace_with("")

        else:
            try:
                tag.decompose()
            except:
                tag.replace_with("")


class RegExReplacer(Actor):

    def __init__(self, pattern="", repl=""):
        super(RegExReplacer, self).__init__(self)

        if isinstance(pattern, str):
            self.pattern = re.compile(pattern, flags=re.UNICODE)
        else:
            self.pattern = pattern

        self.repl = repl

    def act(self, tag):

        if isinstance(tag, element.Tag):
            tag.string = self.replace(tag.get_text())
        else:
            text = tag
            return self.replace(text)

    def replace(self, text):
        return self.pattern.sub(self.repl, text)
