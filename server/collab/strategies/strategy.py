class Strategy(object):
  def __init__(self, source_file, source_start, source_end,
               source_file_version, target_project, target_file, matchers):
    self.source_filter = {'file_version__file': source_file,
                          'file_version_id': source_file_version}
    if source_start:
      self.source_filter['instance__offset__gte'] = source_start
    if source_end:
      self.source_filter['instance__offset__lte'] = source_end
    self.source_vectors = Vector.objects.filter(**source_filter)

    self.target_filter = {}
    if target_project:
      self.target_filter = {'file_version__file__project_id': target_project}
    elif target_file:
      self.target_filter = {'file_version__file': target_file}
    self.target_exclude = {'file_version__file': source_file}
    self.target_vectors = Vector.objects.filter(**self.target_filter)
    self.target_vectors = self.target_vectors.exclude(**self.target_exclude)

    self.matchers = set(json.loads(matchers))

  @classmethod
  def is_abstract(cls):
    return not (hasattr(cls, 'strategy_type') and
                hasattr(cls, 'strategy_description') and
                hasattr(cls, 'strategy_name'))
