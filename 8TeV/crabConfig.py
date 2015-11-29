#!/bin/env python
# crab submission script
# usage: python crabConfig.py submit

from CRABClient.UserUtilities import getUsernameFromSiteDB
from httplib import HTTPException
from CRABAPI.RawCommand import crabCommand
from CRABClient.ClientExceptions import ClientException
from multiprocessing import Process
import sys
from glob import glob
import os, shutil
import json

def submit(config):
    try:
        crabCommand('submit', config = config)
    except HTTPException as hte:
        print "Failed submitting task: %s" % (hte.headers)
    except ClientException as cle:
        print "Failed submitting task: %s" % (cle)

def crab_command(command):
    for dir in glob('/nfs/dust/cms/user/gsieber/crab_kappa_skim-2015-11-29_8TEV/*'):
        crabCommand(command, dir=dir)

def check_path(path):
    if os.path.exists(path):
        print(path + " already exists! Delete it now in order to re-initialize it by crab? [y/n]")
        yes = set(['yes','y', 'ye', ''])
        no = set(['no','n'])

        choice = raw_input().lower()
        if choice in yes:
            shutil.rmtree(path)
            return
        elif choice in no:
            return
        else:
            sys.stdout.write(path + " already exists! Delete it now in order to re-initialize it by crab?")


def submission():
    from CRABClient.UserUtilities import config
    config = config()

    config.General.workArea = '/nfs/dust/cms/user/gsieber/crab_kappa_skim-2015-11-29_8TEV'
    check_path(config.General.workArea)
    config.General.transferOutputs = True
    config.General.transferLogs = True
    config.User.voGroup = 'dcms'

    config.JobType.pluginName = 'Analysis'
    config.JobType.psetName = 'skim_pfjets.py'
    config.JobType.inputFiles = ['Winter14_V5_DATA.db','Winter14_V5_MC.db']
    config.JobType.allowUndistributedCMSSW = True

    config.Data.inputDBS = 'global'
    config.Data.splitting = 'FileBased'
    config.Data.unitsPerJob = 10
    config.Data.outLFNDirBase = '/store/user/sieber/SKIMS_JETS_2015/2015-11-29_8TEV'
    config.Data.publication = False

    config.Site.storageSite = "T2_DE_DESY"

    with open('datasets.json') as json_file:
        try:
            datasets = json.load(json_file)
        except ValueError:
            print 'Failed to parse json file.'
            sys.exit(1)

    # loop over datasets and get repsective nicks
    for nickname in datasets.keys():
        print nickname
        print datasets[nickname]['globaltag']
        print datasets[nickname]['dataset']
        config.General.requestName = nickname
        config.JobType.pyCfgParams = [str('globaltag=%s'%(datasets[nickname]['globaltag'])), 
                                      str('outputfilename=kappa_%s.root'%(nickname)),
                                      str('data={0}'.format(datasets[nickname]['is_data']))
                                      ]
        print config.JobType.pyCfgParams
        config.JobType.outputFiles = [str('kappa_%s.root'%(nickname))]
        config.Data.inputDataset = datasets[nickname]['dataset']
        p = Process(target=submit, args=(config,))
        p.start()
        p.join()

if __name__ == "__main__":
    if len(sys.argv) == 1: 
        print "no setting provided"
        sys.exit()
    if sys.argv[1] == "submit":
        submission()
    elif sys.argv[1] in ["status", "resubmit", "kill"]:
        crab_command(sys.argv[1])
    else:
        print "setting \"%s\" is not implemented"% sys.argv[1]
