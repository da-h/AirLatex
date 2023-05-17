import traceback
import time
import logging
import traceback
from logging import NOTSET
import random

__version__ = "0.2"


# Generate a timstamp with a length of 13 numbers
def _genTimeStamp():
  t = time.time()
  t = str(t)
  t = t[:10] + t[11:]
  while len(t) < 13:
    t += "0"
  return t


# get logging
logging_settings = {"level": "NOTSET", "file": "AirLatex.log", "gui": True}


class CustomLogRecord(logging.LogRecord):

  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)
    self.filename = self.filename.split(".")[0]
    self.origin = f"{time.time()} | {self.filename} / {self.funcName} #{self.lineno:<4}"


def init_logger():
  log = logging.getLogger("AirLatex")

  # user settings
  level = logging_settings["level"]
  file = logging_settings["file"]

  # gui related logging
  DEBUG_LEVEL_GUI = 9
  logging.addLevelName(DEBUG_LEVEL_GUI, "DEBUG_GUI")

  def debug_gui(self, message, *args, **kws):
    if self.isEnabledFor(DEBUG_LEVEL_GUI) and logging_settings["gui"]:
      self._log(DEBUG_LEVEL_GUI, message, args, **kws)

  logging.Logger.debug_gui = debug_gui
  logging.DEBUG_GUI = DEBUG_LEVEL_GUI

  if level != "NOTSET":

    # formatter
    logging.setLogRecordFactory(CustomLogRecord)
    f = logging.Formatter('%(origin)40s: %(message)s')

    # handler
    h = logging.FileHandler(file, "w")
    h.setFormatter(f)

    # logger settings
    log.addHandler(h)
    log.setLevel(getattr(logging, level))

  return log


# https://github.com/overleaf/overleaf/blob/959e6a73d8b0db78c4d4f7c844c935cf9157e5bc/libraries/ranges-tracker/index.cjs#L80
# General track changes (new comment in thread / other tc
def generateId():
  pid = format(random.randint(0, 32767), 'x')
  machine = format(random.randint(0, 16777216), 'x')
  timestamp = format(int(time.time()), 'x')

  return (
      '00000000'[:8 - len(timestamp)] + timestamp +
      '000000'[:6 - len(machine)] + machine + '0000'[:4 - len(pid)] + pid)


# Specifically for creating comments
def generateCommentId(increment):
  increment = format(increment, 'x')  # convert to hex
  id = generateId() + ('000000' + increment)[-6:]  # pad with zeros
  return id


def pynvimCatchException(fn, alt=None):

  def wrapped(self, *args, **kwargs):
    try:
      return fn(self, *args, **kwargs)
    except Exception as e:
      self.status = f"Error: {e}. This is an unexpected Exception, thus stopping AirLatex. Please check the logfile & consider writing an issue to help improving the code."
      self.log.debug(traceback.format_exc())
      self.updateStatusLine()

      if self.log.level == NOTSET:
        self.nvim.err_write(traceback.format_exc(e) + "\n")
      else:
        self.log.exception(
            "Uncaught exception occured. Please consider the log file.")
        self.log.exception(str(e))

      if alt is not None:
        return alt

  return wrapped
