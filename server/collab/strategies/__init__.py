from .strategy import Strategy
from .all_strategy import AllStrategy

strategies_list = [AllStrategy]

def strategy_choices():
  return [(s.strategy_type, s.strategy_name) for s in strategies_list
            if not s.is_abstract()]

__all__ = ['Strategy', 'AllStrategy', 'strategies_list']
