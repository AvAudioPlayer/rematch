from django.db.models import Q


class StrategyStep(object):
  def __init__(self, matcher):
    self.matcher = matcher

  def get_source_filters(self):
    return Q(type=self.matcher.vector_type)

  def get_target_filters(self):
    return Q(type=self.matcher.vector_type)
