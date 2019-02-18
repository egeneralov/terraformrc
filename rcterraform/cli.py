import argparse
import logging

from rcterraform import *

def parse_args():
  parser = argparse.ArgumentParser()
  parser.add_argument(
    "-f", "--file",
    default = "~/.terraformrc.yml",
    help="File (rc.yml) to proceed"
  )
  parser.add_argument(
    "-d", "--directory",
    default = "~/.terraform.d/plugins",
    help="Plugins directory"
  )
  parser.add_argument(
    "-v", "--verbose",
    default = 1,
    help="Verbose",
    action='count'
  )
  args = parser.parse_args()
  return args


def set_logging(verbose = 1):
  level = 60 - 10 * verbose
  if level < 0:
    level = 10
  if level > 60:
    level = 60
  logging.basicConfig(
    level = level,
    format = '{"time": "%(asctime)s", "filename":"%(filename)s", "line":"%(lineno)d", "level":"%(levelname)s", "message": "%(message)s"}',
    handlers = [
      logging.StreamHandler(sys.stdout)
    ]
  )


def main():
  args = parse_args()
  set_logging(args.verbose)

  config = {
    'path': args.file,
    'dir': args.directory
  }

  config = get_config(config)
  logging.info(config)

  for provisioner in config['rc']['provisioners']:
    provisioner = proceed_item(
      provisioner, config, item_type = 'provisioner'
    )
#     logging.info(provisioner)
  
  for provider in config['rc']['providers']:
    provider = proceed_item(
      provider, config, item_type = 'provider'
    )
#     logging.info(provider)
  
if __name__ == '__main__':
  main()

