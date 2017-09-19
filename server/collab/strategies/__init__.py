from .strategy import Strategy
from .all_strategy import AllStrategy


strategies_list = [AllStrategy]


def strategy_choices():
  return [(s.strategy_type, s.strategy_name) for s in strategies_list
            if not s.is_abstract()]


def get_strategy(strategy_name):
  for s in strategies_list:
    if s.strategy_name == strategy_name:
      return s

  strategy_names = [s.strategy_name for s in strategies_list]
  raise ValueError("Couldn't find requested strategy {} out of available "
                   "strategies: {}".format(strategy_name, strategy_names))

__all__ = ['Strategy', 'AllStrategy', 'strategies_list']
