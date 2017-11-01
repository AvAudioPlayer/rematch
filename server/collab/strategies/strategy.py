from django.db.models import Q

import json

from collab.matchers import matchers_list


class Strategy(object):
  def __init__(self, source_file, source_start, source_end,
               source_file_version, target_project, target_file, matchers):
    self.source_file = source_file
    self.source_start = source_start
    self.source_end = source_end
    self.source_file_version = source_file_version
    self.target_project = target_project
    self.target_file = target_file

    self.matchers = set(json.loads(matchers))
    self.ordered_matchers = self.get_ordered_matchers()
    self.ordered_steps = self.get_ordered_steps()

    if len(self.matchers) != len(self.ordered_matchers):
      raise ValueError("Requested matchers({}) and ordered matchers({}) have "
                       "different lengths".format(len(self.matchers),
                                                  len(self.ordered_matchers)))

  def get_source_filters(self):
    # make sure vector belongs to the file_version (and therefore the file)
    # of the source
    source_filters = Q(file_version_id=self.source_file_version)

    # if provided with a source start and/or end, add additional limitations
    if self.source_start:
      source_filters &= Q(instance__offset__gte=self.source_start)
    if self.source_end:
      source_filters &= Q(instance__offset__lte=self.source_end)

    return source_filters

  def get_target_filters(self):
    # Exclude source file inputs from the target
    target_filter = ~Q(file_version__file=self.source_file)

    # if provided with a target file make sure to filter by it, else limit to
    # provided project or not at all
    if self.target_file:
      target_filter &= Q(file_version__file=self.target_file)
    elif self.target_project:
      target_filter &= Q(file_version__file__project_id=self.target_project)

    return target_filter

  def get_ordered_matchers(self):
    # return matchers in self.matchers ordered by the order they appear in
    # matchers.matchers_list
    return [m for m in matchers_list if m.match_type in self.matchers]

  def get_ordered_steps(self):
    raise NotImplementedError("get_ordered_steps method must be implemeneted "
                              "by a strategy implementation class.")

  def __len__(self):
    return len(self.ordered_steps)

  def __getitem__(self, i):
    return self.ordered_steps[i]

  @classmethod
  def is_abstract(cls):
    return not (hasattr(cls, 'strategy_type') and
                hasattr(cls, 'strategy_description') and
                hasattr(cls, 'strategy_name') and
                hasattr(cls, 'get_ordered_steps'))
