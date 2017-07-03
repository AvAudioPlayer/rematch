import idaapi
import idc

import json

from .. idasix import QtGui, QtWidgets, QtCore

from . import base
from .. import network
from .. import exceptions


class UploadDialog(QtWidgets.QProgressDialog, base.BaseDialog):
  def __init__(self, *args, **kwargs):
    super(UploadDialog, self).__init__(*args, **kwargs)

    self.setLabelText("Processing IDB... You may continue working,\nbut "
                      "please avoid making any ground-breaking changes.")
    self.setRange(0, 0)
    self.setValue(0)

  def advance(self, increase=1):
    new_value = self.value() + increase
    if new_value >= self.maximum():
      self.accept()
    else:
      self.setValue(new_value)

  @staticmethod
  def data():
    return {}

  def show(self, *args, **kwargs):
    super(UploadDialog, self).show(*args, **kwargs)
    self.submit_base()