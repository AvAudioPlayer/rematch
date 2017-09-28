from .strategy import Strategy
from .all_strategy import AllStrategy


strategies_list = [AllStrategy]


def strategy_choices():
  return [(s.strategy_type, s.strategy_name) for s in strategies_list
            if not s.is_abstract()]


def get_strategy(strategy, **kwargs):
  for strategy_cls in strategies_list:
    if strategy_cls.strategy_type == strategy:
      return strategy_cls(**kwargs)

  strategy_types = [s.strategy_type for s in strategies_list]
  raise ValueError("Couldn't find requested strategy {} out of available "
                   "strategies: {}".format(strategy, strategy_types))


__all__ = ['Strategy', 'AllStrategy', 'strategies_list']
