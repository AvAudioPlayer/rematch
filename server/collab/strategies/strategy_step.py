from django.db.models import Q


class StrategyStep(object):
  def __init__(self, matcher):
    self.matcher = matcher

  def get_match_type(self):
    return self.matcher.match_type

  def get_results_filter(self):
    return Q(type=self.matcher.vector_type)

  def get_source_filters(self):
    return Q(type=self.matcher.vector_type)

  def get_target_filters(self):
    return Q(type=self.matcher.vector_type)

  def gen_matches(self, source_vectors, target_vectors):
    return self.matcher.match(source_vectors, target_vectors)
