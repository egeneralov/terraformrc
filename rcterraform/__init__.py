#!/usr/bin/env python3

import sys
import re
import os
import platform
import logging
import yaml
import requests
import zipfile
from lxml import html



class cd:
  """Context manager for changing the current working directory"""
  def __init__(self, newPath):
    self.newPath = os.path.expanduser(newPath)
  
  def __enter__(self):
    self.savedPath = os.getcwd()
    os.chdir(self.newPath)
  
  def __exit__(self, etype, value, traceback):
    os.chdir(self.savedPath)




def patch_url(url, version = None, config = {}, **kwargs):
  url = url.replace('{os}',config['os'])
  url = url.replace('{arch}',config['arch'])
  if version:
    url = url.replace('{version}',version)
  return url


def file_or_url(data):
  '''
  for url in ['http://ya.ru/some/dir/some.tar.gz','file://tmp/ansible-sdasodjsklajdajlkds/some.tf']:
    print(
      file_or_url(
        url
      )
    )
  '''
  url_result = re.findall(
    r'(https?):\/\/.*', data
  )
  file_result = re.findall(
    r'(file):\/\/.*', data
  )
  if len(url_result):
    if url_result[0] in ['http', 'https']:
      return 'http'
  if len(file_result):
    if file_result[0] == 'file':
      return 'file'
  raise Exception(
    'What is it? {}'.format(data)
  )



def get_url_auto(name, arch = 'amd64', os = 'linux'):
  url = 'https://releases.hashicorp.com/terraform-provider-{}/'.format(
    name
  )
  r = requests.get(url)
  page = html.fromstring(r.text)
  urls = page.xpath('//a/text()')
  try:
    urls.remove('../')
    urls.remove('Fastly')
  except:
    pass
  all = [ i.split('_')[1] for i in urls ]
  all.sort()
  latest_version = all[-1]
  url = 'https://releases.hashicorp.com/terraform-provider-{}/{}/'.format(
    name, latest_version
  )
  r = requests.get(url)
  page = html.fromstring(r.text)
  urls = page.xpath('//a/text()')
  urls.remove('../')
  urls.remove('Fastly')
  all = [ i.split('_')[1] for i in urls ]
  all.sort()
  latest_version = all[-1]
  r = requests.get(url)
  page = html.fromstring(r.text)
  for el in page.xpath('//a[contains(@data-os,"{}")]'.format(os)):
    if el.get('data-arch') == arch:
      name, version, os, arch, url = el.values()
#       print((name, version, os, arch, url))
      continue
  return 'https://releases.hashicorp.com' + url


def get_config(override=None):
  config = {
    'path': '~/.terraformrc.yml',
    'dir': '~/.terraform.d/plugins'
  }
  if override:
    config.update(**override)
  if platform.machine() == 'x86_64':
    config['arch'] = 'amd64'
  else:
    config['arch'] = 'i386'
  config['os'] = platform.platform().split('-')[0].lower()
  if config['os'] not in ['linux', 'darwin']:
    raise Exception(
      "OS '{}' not supported".format(config['os'])
    )
  if config['dir'].startswith('~'):
    logging.debug("replace tilda")
    config['dir'] = config['dir'].replace(
      '~', os.environ['HOME']
    )
  os.system('mkdir -p {}'.format(config['dir']))
  if config['path'].startswith('~'):
    logging.debug("replace tilda")
    config['path'] = config['path'].replace(
      '~', os.environ['HOME']
    )
  with open(config['path']) as f:
    logging.debug("load configuration")
    payload = f.read()
    config['rc'] = yaml.load(payload)
  return config


def download_file(url, local_path):
  if os.path.isfile(local_path):
    return local_path
  with requests.get(url, stream=True) as r:
    with open(local_path, 'wb') as f:
      for chunk in r.iter_content(chunk_size=8192): 
        if chunk: # filter keep-alive
          f.write(chunk)
#           logging.debug('Writed chunk')
      f.flush()
  return local_path



def proceed_item(item, config, item_type = 'ansible'):
  if not item['name']:
    logging.warning("Empty item {}".format(item))
    return item
  logging.info(
    "Processing item {}".format(item)
  )
  # hardcode...
  status = {
    "http": True,
    "file": False
  }

  # set path to save binary
  item['local_path'] = '{}/terraform-{}-{}'.format(
    config['dir'], item_type, item['name']
  )

  # if url not present - try to get it from official mirror
  if 'url' not in item:
    item['url'] = get_url_auto(
      name = item['name'],
      arch = config['arch'],
      os = config['os']
    )

#     with cd(config['dir']):
    download_file(
      url = item['url'],
      local_path = '{}.zip'.format(item['local_path'])
    )
    zip_ref = zipfile.ZipFile('{}.zip'.format(item['local_path']), 'r')
    zip_ref.extractall(config['dir'])
    zip_ref.close()
    os.unlink('{}.zip'.format(item['local_path']))
    item['url'] = 'file://{}'.format(item['local_path'])

#   logging.info(item['local_path'])
  if 'url' in item:
    item['url'] = patch_url(**item, config=config)
  item['is_url'] = status[
    file_or_url(item['url'])
  ]
  item['is_url'] = status[
    file_or_url(item['url'])
  ]
  if item['is_url']:
    try:
      download_file(
        url = item['url'],
        local_path = item['local_path']
      )
    except:
      msg = 'Cannot download item {}'.format(
        item['name']
      )
      logging.critical(msg)
      raise Exception(msg)
#   logging.info(item)
  item['ready'] = os.path.isfile(
    item['local_path']
  )
  os.system(
    'chmod +x {}*'.format(item['local_path'])
  )
  return item



# if __name__ == '__main__':
#   logging.basicConfig(
#     level = logging.INFO,
#     format = '{"time": "%(asctime)s", "filename":"%(filename)s", "line":"%(lineno)d", "level":"%(levelname)s", "message": "%(message)s"}',
#     handlers = [
# #       logging.FileHandler(filename='{}/history.log'.format(base_dir)),
#       logging.StreamHandler(sys.stdout)
#     ]
#   )
#   
#   
#   config = get_config()
#   
#   logging.info(config)
#   
#   for provisioner in config['rc']['provisioners']:
#     provisioner = proceed_item(
#       provisioner, config, item_type = 'provisioner'
#     )
# #     logging.info(provisioner)
#   
#   for provider in config['rc']['providers']:
#     provider = proceed_item(
#       provider, config, item_type = 'provider'
#     )
# #     logging.info(provider)
#   



























