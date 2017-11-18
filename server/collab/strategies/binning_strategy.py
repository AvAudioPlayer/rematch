from .strategy import Strategy
from .strategy_step import BinningStrategyStep

from django.db.models import Max, Min


class BinningStrategy(Strategy):
  strategy_name = 'Binning'
  strategy_type = 'binning_strategy'
  strategy_description = ("divide functions to bins by function size, and "
                          "only attempt to match functions in the same bin.")

  @staticmethod
  def get_bins(matcher, source_vectors, target_vectors):
    del matcher

    source_sizes = source_vectors.aggregate(Min('instance__size'),
                                            Max('instance__size'))
    target_sizes = target_vectors.aggregate(Min('instance__size'),
                                            Max('instance__size'))

    # find the common denomenator of sizes
    min_size = max(source_sizes['instance__size__min'],
                   target_sizes['instance__size__min'])
    max_size = min(source_sizes['instance__size__max'],
                   target_sizes['instance__size__max'])
    print("sizes", min_size, max_size)
    return sizes

  def get_ordered_steps(self, source_vectors, target_vectors):
    ordered_steps = list()

    for matcher in self.ordered_matchers:
      matcher_bins = self.get_bins(matcher, source_vectors, target_vectors)
      for bin_min, bin_max in matcher_bins:
        step = BinningStrategyStep(matcher, bin_min, bin_max)
        ordered_steps.append(step)

    return ordered_steps
