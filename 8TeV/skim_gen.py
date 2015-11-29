# Kappa test: CMSSW 5.3.26
# Kappa test: scram arch slc6_amd64_gcc472
# Kappa test: output skim.root

import FWCore.ParameterSet.Config as cms
from  FWCore.PythonUtilities import LumiList


filename = 'file:/nfs/dust/cms/user/gsieber/dijetana/np/CMSSW_5_3_28/QCD_Pt_15to500_Tune4C_FlatPtEta_8TeV_pythia8.root'
# filename = 'file:/nfs/dust/cms/user/gsieber/dijetana/np/CMSSW_5_3_28/QCD_Pt_15to500_Tune4C_FlatPtEta_NOMPINOHAD_8TeV_pythia8.root'
globaltag = 'START53_V27::All'
datatype = 'GEN'

# Basic process setup ----------------------------------------------------------
process = cms.Process("SKIM")

process.source = cms.Source("PoolSource",
    fileNames = cms.untracked.vstring(filename)
)
process.maxEvents = cms.untracked.PSet( input = cms.untracked.int32(-1) )

print "Starting Kappa Skim"

print "GlobalTag: {0}".format(globaltag)
print "Datatype: {0}".format(datatype)

#-------------------------------------------------------------------------------
# Global Tag
#-------------------------------------------------------------------------------
process.load("FWCore.MessageService.MessageLogger_cfi")
process.load('Configuration.StandardSequences.Services_cff')
process.load('Configuration.StandardSequences.MagneticField_38T_cff')
process.load('Configuration.Geometry.GeometryIdeal_cff')
process.load('Configuration.Geometry.GeometryPilot2_cff')
process.load('Configuration.StandardSequences.FrontierConditions_GlobalTag_cff')
process.load("Configuration.StandardSequences.Reconstruction_cff")
process.GlobalTag.globaltag = globaltag

#-------------------------------------------------------------------------------
# Kappa Tuple
#-------------------------------------------------------------------------------
process.load("Kappa.Producers.KTuple_cff")
process.kappatuple = cms.EDAnalyzer('KTuple',
    process.kappaTupleDefaultsBlock,
    outputFile = cms.string('skim.root'),
)
process.kappatuple.verbose = cms.int32(0)

process.kappatuple.Info.l1Source = cms.InputTag("")
process.kappatuple.Info.hltSource = cms.InputTag("")
process.kappatuple.Info.hlTrigger = cms.InputTag("")
process.kappatuple.Info.noiseHCAL = cms.InputTag("")

process.kappatuple.active = cms.vstring("GenInfo", "LV")
process.kappatuple.LV.whitelist = cms.vstring("recoGenJets_ak5GenJets.*", "recoGenJets_ak7GenJets.*")

process.kappa_path = cms.Path(process.kappatuple)

process.schedule = cms.Schedule(
                                # process.metFilters,
                                process.kappa_path
                                )
