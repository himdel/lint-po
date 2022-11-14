#!/usr/bin/env python3
import json
import re
from os import environ
from sys import stderr
import warnings

# find any {num} {str} <num> </num> <num/> %(str)s
REGEX = r'(\{(\w+|\d+)\})|(<\/?\d+\/?>)|(%(\(\w+\))?.)'

PLURAL_REGEX = r'^{(\w+), plural, .*}$'

# s.encode('utf-8').decode('unicode-escape') if only it worked with utf8 strings
def unqqbackslash(s):
  return json.loads(s)


# extract all vars from string - findall(REGEX).map((arr) => arr.compact.first)
def extract(s):
  return [ [truthy for truthy in match if truthy][0] for match in re.findall(REGEX, s) ]


def fail(msg, file, line):
  if environ.get('GITHUB_ACTIONS'):
    s = msg.replace("\r", "").replace("\n", "").replace('%', '%25')
    print(f"::error file={file},line={line}::{s}", file=stderr)
  return f"  {msg}\n"


def process_pair(msgid, msgstr, file, line):
  # handling eof while still in state 2; magic id, untranslated strings
  if not msgid or not msgstr:
    return True

  # lingui-style plurals - "{n, plural, one {# Word} other {# Words}}"
  lingui_id = re.match(PLURAL_REGEX, msgid)
  lingui_str = re.match(PLURAL_REGEX, msgstr)
  if lingui_id or lingui_str:
    message = ""
    if not lingui_id or not lingui_str:
      message += fail(f"Plural only in msgid or only in msgstr, not the other", file, line)
    elif lingui_id[1] != lingui_str[1]:
      message += fail(f"Plural var different between msgid ({lingui_id[1]}) and msgstr ({lingui_str[1]})", file, line)

    if message:
      print(f"Plural issue between msgid=\"{msgid}\" and msgstr=\"{msgstr}\":\n{message}\n", file=stderr)
      return False

    return True

  # regular message with placeholders
  msgidvars = extract(msgid)
  msgstrvars = extract(msgstr)

  missing = set(msgidvars) - set(msgstrvars)
  extra = set(msgstrvars) - set(msgidvars)

  if len(missing) or len(extra):
    message = ""
    if len(missing):
      message += fail(f"Missing from msgstr: {', '.join(missing)}", file, line)
    if len(extra):
      message += fail(f"Unexpected in msgstr: {', '.join(extra)}", file, line)
    message += f"  at {file}:{line}"

    print(f"Difference between msgid=\"{msgid}\" and msgstr=\"{msgstr}\":\n{message}\n", file=stderr)
    return False

  return True


def process_file(filename, lines):
  errors = False
  state = 0
  msgid = None
  msgstr = None
  msgstrlineno = 0

  for lineno, line in enumerate(lines):
    if re.match(r'^#', line):
      continue

    line = line.strip()

    if state == 0: # expecting `msgid`
      if re.match(r'^$', line):
        continue

      if m := re.match(r'^msgid\s+(.*)$', line):
        msgid = unqqbackslash(m[1])
        state = 1
        continue

      warnings.warn(f"({state}) Unexpected input: {line}")
      errors = True

    elif state == 1: # expecting `msgstr`, or more bits of previous msgid
      if m := re.match(r'^msgstr\s+(.*)$', line):
        msgstr = unqqbackslash(m[1])
        msgstrlineno = lineno + 1
        state = 2
        continue

      if re.match(r'^"', line):
        msgid += unqqbackslash(line)
        continue

      warnings.warn(f"({state}) Unexpected input: {line}")
      errors = True

    elif state == 2: # expecting newline, or more bits of previous msgstr
      if re.match(r'^$', line):
        if not process_pair(msgid, msgstr, filename, msgstrlineno):
          errors = True

        state = 0
        msgid = None
        msgstr = None
        msgstrlineno = 0
        continue

      if re.match(r'^"', line):
        msgstr += unqqbackslash(line)
        continue

      warnings.warn(f"({state}) Unexpected input: {line}")
      errors = True

  if not process_pair(msgid, msgstr, filename, msgstrlineno):
    errors = True

  return errors


def main(files):
  errors = False

  for filename in files:
    lines = None
    with open(filename) as f:
      lines = f.read().splitlines()

    if process_file(filename, lines):
      errors = True

  return(1 if errors else 0)
