from ..idasix import QtCore, QtWidgets

from ..dialogs.review import ReviewDialog

from .. import network, netnode, log
from . import base

import json


class ReviewAction(base.BoundFileAction):
  name = "&Review"
  dialog = ReviewDialog

  def __init__(self, *args, **kwargs):
    super(ReviewAction, self).__init__(*args, **kwargs)
    self.functions = None
    self.results = None
    self.task_id = None
    self.file_version_id = None
    self.instance_set = []

    self.source = None
    self.source_single = None
    self.source_range = None
    self.target = None
    self.target_project = None
    self.target_file = None
    self.matchers = None

    self.delayed_queries = []

    self.pbar = QtWidgets.QProgressDialog()
    self.pbar.canceled.connect(self.cancel)
    self.pbar.rejected.connect(self.cancel)
    self.pbar.hide()

    self.timer = QtCore.QTimer()

  def clean(self):
    self.timer.stop()
    try:
      self.timer.timeout.disconnect()
    except TypeError:
      pass
    try:
      self.pbar.accepted.disconnect()
    except TypeError:
      pass

  def cancel_delayed(self):
    for delayed in self.delayed_queries:
      log('match_action').info("async task cancelled: %s", repr(delayed))
      delayed.cancel()
    self.delayed_queries = []

  def cancel(self):
    log('match_action').info("match action cancelled")
    self.clean()
    self.cancel_delayed()

  def submit_handler(self, source, source_single, source_range, target,
                     target_project, target_file, matchers):
    self.source = source
    self.source_single = source_single
    self.source_range = source_range
    self.target = target
    self.target_project = target_project if target == 'project' else None
    self.target_file = target_file if target == 'file' else None
    self.matchers = matchers

    file_version_hash = self.calc_file_version_hash()
    uri = "collab/files/{}/file_version/{}/".format(netnode.bound_file_id,
                                                    file_version_hash)
    return network.QueryWorker("POST", uri, json=True)

  def response_handler(self, file_version):
    self.file_version_id = file_version['id']

    if file_version['newly_created']:
      self.start_upload()
    else:
      self.start_task()

    return True

  def start_task(self):
    if self.source == 'idb':
      self.source_range = [None, None]
    elif self.source == 'single':
      self.source_range = [self.source_single, self.source_single]
    elif self.source == 'range':
      pass
    else:
      raise NotImplementedError("Unsupported source type encountered in task "
                                "creation")

    params = {'source_file': netnode.bound_file_id,
              'source_file_version': self.file_version_id,
              'source_start': self.source_range[0],
              'source_end': self.source_range[1],
              'target_project': self.target_project,
              'target_file': self.target_file,
              'source': self.source, 'matchers': json.dumps(self.matchers)}
    r = network.query("POST", "collab/tasks/", params=params, json=True)
    self.task_id = r['id']

    self.pbar.setLabelText("Waiting for remote matching... You may continue "
                           "working without any limitations.")
    self.pbar.setRange(0, int(r['progress_max']) if r['progress_max'] else 0)
    self.pbar.setValue(int(r['progress']))
    self.pbar.accepted.connect(self.accept_task)
    self.pbar.show()

    self.timer.timeout.connect(self.perform_task)
    self.timer.start(200)

  def perform_task(self):
    try:
      r = network.query("GET", "collab/tasks/{}/".format(self.task_id),
                        json=True)

      progress_max = int(r['progress_max']) if r['progress_max'] else None
      progress = int(r['progress'])
      status = r['status']
      if status == 'failed':
        self.pbar.cancel()
      elif progress_max:
        self.pbar.setMaximum(progress_max)
        if progress >= progress_max:
          self.pbar.accept()
        else:
          self.pbar.setValue(progress)
    except Exception:
      self.cancel()
      log('match_action').exception("perform update failed")
      raise

  def accept_task(self):
    log('match_action').info("Remote task completed successfully")

    self.clean()
    self.delayed_queries = []

    self.start_results()

  def start_results(self):
    self.pbar.setLabelText("Receiving match results...")
    self.pbar.setRange(0, 0)
    self.pbar.setValue(0)
    self.pbar.accepted.connect(self.accept_results)
    self.pbar.show()

    self.ui.finished.connect(self.close_dialog)

    log('match_action').info("Result download started")
    locals_url = "collab/tasks/{}/locals/".format(self.task_id)
    q = network.QueryWorker("GET", locals_url, json=True, paginate=True,
                            params={'limit': 100})
    q.start(self.handle_locals)
    self.delayed_queries.append(q)

    remotes_url = "collab/tasks/{}/remotes/".format(self.task_id)
    q = network.QueryWorker("GET", remotes_url, json=True, paginate=True,
                            params={'limit': 100})
    q.start(self.handle_remotes)
    self.delayed_queries.append(q)

    matches_url = "collab/tasks/{}/matches/".format(self.task_id)
    q = network.QueryWorker("GET", matches_url, json=True, paginate=True,
                            params={'limit': 100})
    q.start(self.handle_matches)
    self.delayed_queries.append(q)

  def handle_locals(self, response):
    new_locals = {obj['id']: obj for obj in response['results']}
    self.results.add_locals(new_locals)

    self.handle_page(response)

  def handle_remotes(self, response):
    new_remotes = {obj['id']: obj for obj in response['results']}
    self.results.add_remotes(new_remotes)

    self.handle_page(response)

  def handle_matches(self, response):
    def rename(o):
      o['local_id'] = o.pop('from_instance')
      o['remote_id'] = o.pop('to_instance')
      return o

    new_matches = map(rename, response['results'])
    self.results.add_matches(new_matches)

    self.handle_page(response)

  def handle_page(self, response):
    if 'previous' not in response or not response['previous']:
      self.pbar.setMaximum(self.pbar.maximum() + response['count'])

    new_value = max(self.pbar.value(), 0) + len(response['results'])
    if new_value >= self.pbar.maximum():
      self.pbar.accept()
    else:
      self.pbar.setValue(new_value)

  def accept_results(self):
    log('match_action').info("Result download completed successfully")

    self.clean()
    self.delayed_queries = []

    self.results.show()