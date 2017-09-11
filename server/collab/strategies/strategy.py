class Strategy(object):
  @classmethod
  def is_abstract(cls):
    return False
    return not (hasattr(cls, 'strategy_type') and
                hasattr(cls, 'strategy_description') and
                hasattr(cls, 'strategy_name'))
