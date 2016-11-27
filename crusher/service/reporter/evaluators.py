import re

import core
from core import *
from selectors import *
from actors import *

class Evaluator(object):
    """Evaluates one tag"""

    def __init__(self, name="evaluator", factor=1.0, threshold=None, vmin=None, vmax=None):
        self.name = name
        self.factor = factor
        self.threshold = threshold
        self.vmin = vmin
        self.vmax = vmax

    def evaluate(self, tag):
        return None

    def process(self, value):

        value *= self.factor

        if self.threshold is not None:
            if value > self.threshold:
                if self.vmax is not None:
                    value = self.vmax
                else:
                    value = 1
            else:
                if self.vmin is not None:
                    value = self.vmin
                else:
                    value = 0

        else:
            if self.vmin is not None:
                value = max(value, self.vmin)

            if self.vmax is not None:
                value = min(value, self.vmax)

        return value



class FixedValue(Evaluator):

    def __init__(self, value=0, name="fixed_value", **kwargs):

        super(FixedValue, self).__init__(name, **kwargs)
        self.value = value

    def evaluate(self, tag):
        return self.value


class RegExMatcher(Evaluator):

    def __init__(self, pattern="\w+", name="regex_counter", **kwargs):

        super(RegExMatcher, self).__init__(name, **kwargs)

        if isinstance(pattern, str):
            self.pattern = re.compile(pattern, flags=re.UNICODE)
        else:
            self.pattern = pattern

    def evaluate(self, tag):

        text = tag.get_text()
        num_matches = len(re.findall(self.pattern, text))
        return self.process(num_matches)


class ScoreAggregator(Evaluator):

    def __init__(self, start_score=0, name="score_aggregator", **kwargs):

        super(ScoreAggregator, self).__init__(name, **kwargs)
        self.start_score = start_score

    def evaluate(self, tag):

        score = self.start_score

        for child in tag.children:
            score += core.get_total_score(child)

        return self.process(score)


class ChildrenCounter(Evaluator):

    def __init__(self, selector=None, only_direct_children=True, name="children_counter", **kwargs):

        super(ChildrenCounter, self).__init__(name, **kwargs)
        self.selector = selector
        self.points_per_child = points_per_child
        self.only_direct_children = only_direct_children

        self.selector.actor = Yielder()

    def evaluate(self, tag):

        child_count = 0
        for child in self.selector.select(tag):
            if self.only_direct_children:
                if not child in tag.children:
                    continue

            child_count += 1

        return child_count * self.points_per_child

