#!/usr/bin/env python

# Author: John Hawkins (jsh)

import argparse
import collections
from   email.mime.text import MIMEText
import getpass
import logging
import pprint
import random
import smtplib
import sys


logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(levelname)s %(message)s')

class Error(Exception):
  pass


def main():
  logging.info('Parsing command line.')
  parser = argparse.ArgumentParser(
      description='Send out secret santa emails.')
  parser.add_argument(
      'data_file', type=argparse.FileType('r'),
      help='File containing the tab delimited participant data.')
  parser.add_argument(
      'template_file', type=argparse.FileType('r'),
      help='File containing the template email.')
  parser.add_argument(
      'secret_log', type=argparse.FileType('w'),
      help='File in which to place the secret assignments. SPOILER ALERT.')
  args = parser.parse_args()
  participants = parse_data(args.data_file)
  santa_pairs = assign_santas(participants, args.secret_log)
  send_emails(participants, santa_pairs, args.template_file)


def parse_data(data_file):
  participants = dict()
  for line in data_file:
    fields = line.split('\t')
    if len(fields) != 3:
      logging.fatal('Wrong number of fields in line: {line}'.format(**vars()))
      raise Error
    else:
      (name, email, exclusions) = fields
      name = name.strip()
      email = email.strip()
      exclusions = exclusions.strip().split(',')
      participants[name] = (email, exclusions)
  pprint.pprint(participants)
  return participants

def assign_santas(participants, secret_log):
  santas = participants.keys()
  santees = list(santas)
  while True:
    random.shuffle(santees)
    santa_pairs = zip(santas, santees)
    if check_santas(santa_pairs, participants):
      break
  pprint.pprint(santa_pairs, secret_log)
  return santa_pairs

def check_santas(santa_pairs, participants):
  for (santa, santee) in santa_pairs:
    email, exclusions = participants[santa]
    if santee in exclusions or santa == santee:
      return False
  mapping = dict(santa_pairs)
  santa = santa_pairs[0][0]
  seen = set()
  while True:
    seen.add(santa)
    santa = mapping[santa]
    if santa in seen:
      return len(seen) == len(participants)

def send_emails(participants, santa_pairs, template):
  template = template.read()
  user = 'really'
  password = getpass.getpass('really\'s password: ')
  s = smtplib.SMTP('smtp.gmail.com', 587)
  s.starttls()
  s.login(user, password)
  for santa, santee in santa_pairs:
    logging.info('Sending mail to {santa}...'.format(**vars()))
    email, _ = participants[santa]
    message = MIMEText(template.format(**vars()))
    message['Subject'] = 'Your mission, should you choose to accept it...'
    message['To'] = email
    meta = 'metasanta@disquieting.com'
    message['From'] = meta
    s.sendmail(meta, [email], message.as_string())
  s.quit()

##############################################
if __name__ == "__main__":
    sys.exit(main())
