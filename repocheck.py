#!/usr/bin/env python
import os
import sys
import re
import shutil
import logging
from logging.handlers import RotatingFileHandler
from logging.handlers import SysLogHandler
import yum
import argparse
import subprocess

## Functions
def doRepoSetup(repo,proxy=None):
  logger.debug(repo.id)
  status = None
  response = None
  repo.enable()
  logger.debug("repo enabled")
  cachedir = repo.basecachedir + "/" + repo.id
  logger.info("cachedir: {0}".format(cachedir))
  logger.info("baseurl: {0}".format(repo.baseurl))
  logger.info("mirrorlist: {0}".format(repo.mirrorlist))
  logger.info("metalink: {0}".format(repo.metalink))
  if os.path.isdir(cachedir):
    shutil.rmtree(cachedir)
    logger.debug("removed cachedir")
  repo.dirSetup()
  if proxy:
    repo.proxy = str("http://" + proxy + ":80")
    logger.debug("updated repo with proxy {0}".format(repo.proxy))
  logger.info("proxy: {0}".format(repo.proxy))
  repo.mdpolicy = 'group:primary'
  repo.metadata_expire = 0
  repo.timeout = 30
  repo.retries = 2
  try:
    yb.repos.doSetup()
    yb.repos.populateSack(mdtype='all')
  except Exception as e:
    status = 1
    response = str(e)
    logger.debug("repo setup failed")
  else:
    status = 0
    response = "Yum repo setup successful"
    logger.debug("repo setup success")
  finally:
    repo.disable()
    logger.debug("repo disabled")
    return status,response

## Main Program
## Command Line Argument Parser
parser = argparse.ArgumentParser(description="repocheck script v2.1")
parser.add_argument("-d","--debug", help=argparse.SUPPRESS,action="store_true")
args = parser.parse_args()

## Logging Configuration
logger = logging.getLogger("REPOCHECK")
logger.setLevel(logging.DEBUG)

# Logger Console handler
handler = logging.StreamHandler()
handler.setLevel(logging.INFO)
formatter = logging.Formatter("%(name)s:%(levelname)s: %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)

# Logger File handler
logfile = "/var/log/repotest.log"
# handler = logging.FileHandler(logfile,"w", encoding=None, delay="true")
handler = RotatingFileHandler(logfile, maxBytes=1000000, backupCount=3)
if args.debug:
  handler.setLevel(logging.DEBUG)
else:
  handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(name)s:%(asctime)s.%(msecs)03d:%(levelname)s: %(message)s', datefmt="%Y-%m-%d %H:%M:%S")
handler.setFormatter(formatter)
logger.addHandler(handler)

logger.info("################### START ###################")

## REPOCHECK Syslog Logging Configuration
syslogger = logging.getLogger("REPOCHECK")
sysloghandler = SysLogHandler(address = '/dev/log')
sysloghandler.setLevel(logging.CRITICAL)
sysformatter = logging.Formatter("%(name)s[%(process)d]: %(message)s")
sysloghandler.setFormatter(sysformatter)
syslogger.addHandler(sysloghandler)

## Remove public yum repo
logger.info("Removing public yum repos if exists...")
yum_files = ["/etc/yum.repos.d/public-yum-ol7.repo", "/etc/yum.repos.d/public-yum-ol6.repo"]
for yumfile in yum_files:
  if os.path.exists(yumfile):
    os.remove(yumfile)
    logger.info("Removing yumrepo: %s", yumfile )

## Remove cache under /var/cache/yum/
logger.info("Removing cache under /var/cache/yum/...")
command = "/bin/rm -rf /var/cache/yum/*"
p = subprocess.Popen(command,shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
output,error = p.communicate()
if error:
  logger.error("Error executing rm -rf /var/cache/yum/*")
else:
  logger.info("Cache removal successful.")

## Initiliaze Yum Base
logger.debug("Initializing Yum Base...")
yb = yum.YumBase()

## Get the list of enabled repos
repos = yb.repos.listEnabled()
repolist = [ repo.id for repo in repos ]
logger.info("List of enabled repos: {0}".format(repolist))

## Disabling all enabled repos
logger.debug("Disabling all enabled repos...")
for repo in repos:
  repo.disable()
exitcode = 0
## Test all enabled repos
failed_repos = set()
success_repos = set()
failed_dco_repo = False
failed_ndco_repo = False
logger.info("Starting repo test of all enabled repos...")
for repo in repos:
  logger.info("{0} - repo testing...".format(repo.id))
  status,response = doRepoSetup(repo)
  if status == 0:
    logger.info("{0} - repo test is successful".format(repo.id))
    success_repos.add(repo.id)
  else:
    logger.info("{0} - repo test is failed".format(repo.id))
    logger.error(response)
    failed_repos.add(repo.id)
    if repo.baseurl:
      if repo.baseurl[0].startswith("https://repo.int.thomsonreuters.com"):
        failed_dco_repo = True
      else:
        failed_ndco_repo = True
    else:
      failed_ndco_repo = True

if failed_dco_repo:
  exitcode += 4

if failed_ndco_repo:
  exitcode += 1

## Check if proxy is set in /etc/yum.conf
logger.info("Checking if proxy is set in /etc/yum.conf...")
with open("/etc/yum.conf") as yumfile:
  yumproxy = False
  for line in yumfile.readlines():
    if re.search('^proxy *= *http', line):
      yumproxy = True
      logger.error("Yum Proxy: {0}".format(line.rstrip("\n")))
  if yumproxy:
    logger.error("Proxy set in /etc/yum.conf")
    exitcode += 2
  else:
    logger.info("NO Proxy set in /etc/yum.conf")

if exitcode == 0:
  exitmsg = "Repo Check is Successful."
elif exitcode == 1:
  exitmsg = "Non-DCO repo is failing. To remediate fix the failed repo."
elif exitcode == 2:
  exitmsg = "Proxy is set in /etc/yum.conf. To remediate remove the proxy from /etc/yum.conf."
elif exitcode == 3:
  exitmsg = "Non-DCO repo is failing and Proxy is set in /etc/yum.conf. \
To remediate fix the failed repo & remove the proxy from /etc/yum.conf."
elif exitcode == 4:
  exitmsg = "DCO repo is failing. To remediate fix the failed repo."
elif exitcode == 5:
  exitmsg = "DCO & Non-DCO repos are failing. To remediate fix the failed repos."
elif exitcode == 6:
  exitmsg = "DCO repo is failing and Proxy is set in /etc/yum.conf. \
To remediate fix the failed repo & remove the proxy from /etc/yum.conf."
elif exitcode == 7:
  exitmsg = "DCO & Non-DCO repos are failing and Proxy is set in /etc/yum.conf. \
To remediate fix the failed repos & remove the proxy from /etc/yum.conf."
else:
  exitmsg = "Unknown exitcode. To remediate reach out to UNIX-ENGINEERING team."

logger.info("Successful repos: {0}".format(list(success_repos)))
logger.info("Failed repos: {0}".format(list(failed_repos)))
logger.info("Exit Code: {0}".format(exitcode))
logger.info("Exit Message: {0}".format(exitmsg))
logger.info("END")
if exitcode == 0:
  syslogger.info("| Success | {0} | {1} | None".format(exitcode,exitmsg))
else:
  if len(list(failed_repos)) == 0:
    syslogger.critical("| Failed | {0} | {1} | None".format(exitcode,exitmsg))
  else:
    syslogger.critical("| Failed | {0} | {1} | {2}".format(exitcode,exitmsg,list(failed_repos)))

exit(exitcode)
