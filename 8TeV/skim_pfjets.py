import FWCore.ParameterSet.Config as cms
from  FWCore.PythonUtilities import LumiList

from FWCore.ParameterSet.VarParsing import VarParsing
options = VarParsing('python')
options.register('outputfilename', 'skim.root', VarParsing.multiplicity.singleton, VarParsing.varType.string, 'Filename for the Outputfile')
options.register('globaltag', '', VarParsing.multiplicity.singleton, VarParsing.varType.string, 'GlobalTag')
options.register('data', False, VarParsing.multiplicity.singleton, VarParsing.varType.bool, 'Is the dataset real data. Default: False')
options.parseArguments()

is_data = options.data
globaltag = options.globaltag
filename = []

if options.globaltag == '':
    if is_data:
        globaltag = globaltag if globaltag else 'FT53_V21A_AN6::All'
        filename = ["/store/data/Run2012D/JetHT/AOD/22Jan2013-v1/10002/04FAA943-9D97-E211-830B-E0CB4E1A11A2.root", "/store/data/Run2012D/JetHT/AOD/22Jan2013-v1/10002/D47C39F3-A197-E211-94A5-E0CB4E1A118B.root"]
    else:
        globaltag = globaltag if globaltag else 'START53_V27::All'
        filename = 'root://cms-xrd-global.cern.ch//store/mc/Summer12_DR53X/QCD_Pt-15to3000_TuneZ2star_Flat_8TeV_pythia6/AODSIM/PU_S10_START53_V7A-v1/0000/004CB136-A1D3-E111-B958-0030487E4B8D.root'


# Basic process setup ----------------------------------------------------------
process = cms.Process("SKIM")
process.source = cms.Source("PoolSource",
    fileNames = cms.untracked.vstring(filename)
)
process.maxEvents = cms.untracked.PSet( input = cms.untracked.int32(100) )

print "Starting Kappa Skim"

print "GlobalTag: {0}".format(globaltag)
print "Datatype is data: {0}".format(is_data)

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

process.path = cms.Path()


#-------------------------------------------------------------------------------
# Filters
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
# Lumi Filter
#-------------------------------------------------------------------------------

# TODO: LumiFilter Needs to be applied in GC. Otherwise overwritten by gc process source.
# if is_data:
#    process.source.lumisToProcess = LumiList.LumiList(filename = 'Cert_190456-208686_8TeV_22Jan2013ReReco_Collisions12_JSON.txt').getVLuminosityBlockRange()

#-------------------------------------------------------------------------------
# JEC
#-------------------------------------------------------------------------------
# process.load("CondCore.DBCommon.CondDBCommon_cfi")
# process.load('JetMETCorrections.Configuration.DefaultJEC_cff')
# process.load('JetMETCorrections.Configuration.JetCorrectionProducers_cff')
# process.load('JetMETCorrections.Configuration.JetCorrectionProducersAllAlgos_cff')
#
# if is_data:
#     if is_data:
#         jec_string = 'DATA'
#     else:
#         jec_string = 'MC'
#     process.jecsource = cms.ESSource("PoolDBESSource",
#           DBParameters = cms.PSet(
#             messageLevel = cms.untracked.int32(0)
#             ),
#           timetype = cms.string('runnumber'),
#           toGet = cms.VPSet(
#           cms.PSet(
#                 record = cms.string('JetCorrectionsRecord'),
#                 tag    = cms.string('JetCorrectorParametersCollection_Winter14_V5_{0}_AK5PF'.format(jec_string)),
#                 # tag    = cms.string('JetCorrectorParametersCollection_Summer12_V3_MC_AK5PF'),
#                 label  = cms.untracked.string('AK5PF')
#                 ),
#           cms.PSet(
#                 record = cms.string('JetCorrectionsRecord'),
#                 tag    = cms.string('JetCorrectorParametersCollection_Winter14_V5_{0}_AK7PF'.format(jec_string)),
#                 # tag    = cms.string('JetCorrectorParametersCollection_Summer12_V3_MC_AK7PF'),
#                 label  = cms.untracked.string('AK7PF')
#                 ),
#           ), 
#           connect = cms.string('sqlite:Winter14_V5_{0}.db'.format(jec_string))
#     )
#     # add an es_prefer statement to resolve a possible conflict from simultaneous connection to a global tag
#     process.es_prefer_jec = cms.ESPrefer('PoolDBESSource','jecsource')
# else:
#     # In this case the JEC from the GT (START_XYZ) should be used
#     pass
# if is_data:
#     process.jec = cms.Path(process.ak5PFJetsL1FastL2L3Residual + process.ak7PFJetsL1FastL2L3Residual)
# else:
#     process.jec = cms.Path(process.ak5PFJetsL1FastL2L3 + process.ak7PFJetsL1FastL2L3)
#-------------------------------------------------------------------------------
# MET Filters
#-------------------------------------------------------------------------------

process.load("RecoMET.METFilters.metFilters_cff")


process.path *= process.metFilters

#-------------------------------------------------------------------------------
# Kappa Tuple
#-------------------------------------------------------------------------------
process.load("Kappa.Producers.KTuple_cff")


process.kappatuple = cms.EDAnalyzer('KTuple',
    process.kappaTupleDefaultsBlock,
    outputFile = cms.string(options.outputfilename),
)
process.kappatuple.BasicJets.whitelist = cms.vstring("recoPFJets_ak5PFJets.*", "recoPFJets_ak7PFJets.*")
# process.kappatuple.GenJets.whitelist = cms.vstring("recoGenJets_ak5GenJets.*", "recoGenJets_ak7GenJets.*")
process.kappatuple.verbose = cms.int32(0)
process.kappatuple.active = cms.vstring(
    'TrackSummary', 'VertexSummary', 'FilterSummary', 'MET', 'BasicJets', 'PileupDensity'
)
if is_data:
    process.kappatuple.active.append('DataInfo')
    process.kappatuple.active.append('TriggerObjects')
else:
    process.kappatuple.active.append('GenInfo')
    process.kappatuple.active.append('LV')
    process.kappatuple.LV.whitelist = cms.vstring("recoGenJets_ak5GenJets.*", "recoGenJets_ak7GenJets.*")
    process.kappatuple.active.append('GenParticles')
process.kappatuple.Info.hltWhitelist = cms.vstring(
    "^HLT_PFJet[0-9]+(U)?(_NoJetID)?(_v[[:digit:]]+)?$",
    "^HLT_DiPFJetAve[0-9]+(U)?(_NoJetID)?(_v[[:digit:]]+)?$",
    "^HLT_ZeroBias?(_v[[:digit:]]+)?$",
)
process.kappatuple.Info.hltBlacklist = cms.vstring()

#--------------------------------------------------------------
# PFCandidates
#--------------------------------------------------------------

process.load('Kappa.Skimming.KPFCandidates_cff')
process.path *= (
    process.goodOfflinePrimaryVertices
    * process.pfPileUp
    * process.pfNoPileUp
)

#--------------------------------------------------------------
# Jets
#--------------------------------------------------------------

process.load('RecoJets.JetProducers.ak5PFJets_cfi')

process.ak5PFJets.srcPVs = cms.InputTag('goodOfflinePrimaryVertices')
process.ak5PFJetsCHS = process.ak5PFJets.clone( src = cms.InputTag('pfNoPileUp') )
process.ak7PFJets = process.ak5PFJets.clone()
process.ak7PFJets.rParam = cms.double(0.7)
process.ak7PFJetsCHS = process.ak7PFJets.clone( src = cms.InputTag('pfNoPileUp') )


process.kappatuple.BasicJets = cms.PSet(
	process.kappaNoCut,
	process.kappaNoRegEx,
	ak5PFJets = cms.PSet(
		src = cms.InputTag('ak5PFJets'),
		),
	ak5PFJetsCHS = cms.PSet(
		src = cms.InputTag('ak5PFJetsCHS'),
		),
	ak7PFJets = cms.PSet(
		src = cms.InputTag('ak7PFJets'),
		),
	ak7PFJetsCHS = cms.PSet(
		src = cms.InputTag('ak7PFJetsCHS'),
		),
	)
process.kappatuple.BasicJets.minPt = cms.double(20)
process.kappatuple.BasicJets.maxEta = cms.double(5.)

process.path *= (process.ak5PFJets * process.ak5PFJetsCHS * process.ak7PFJets * process.ak7PFJetsCHS)


#-------------------------------------------------------------------------------
# Output
#-------------------------------------------------------------------------------
# process.out = cms.OutputModule('PoolOutputModule',
#    fileName = cms.untracked.string('file:test_aod.root')
#    )
# process.pathOutput = cms.EndPath(process.out)

# process.MessageLogger = cms.Service("MessageLogger",
       # destinations = cms.untracked.vstring('debug'),
      # debug   = cms.untracked.PSet(threshold=cms.untracked.string('DEBUG') ),
# )

#-------------------------------------------------------------------------------
# Process schedule
#-------------------------------------------------------------------------------
process.path *= process.kappatuple
