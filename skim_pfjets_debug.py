import FWCore.ParameterSet.Config as cms


# Basic process setup ----------------------------------------------------------
process = cms.Process("kappaSkim")
process.source = cms.Source("PoolSource",
		fileNames = cms.untracked.vstring(
										"/store/data/Run2012D/JetHT/AOD/22Jan2013-v1/10000/2CBB9625-E19B-E211-94A6-485B39800B62.root",
										"/store/data/Run2012D/JetHT/AOD/22Jan2013-v1/10000/E4F04401-D89B-E211-A94D-001EC9D8D967.root",
										"/store/data/Run2012D/JetHT/AOD/22Jan2013-v1/10000/FE8CCBAC-E09B-E211-845F-E0CB4E1A114B.root",)
		# lumisToProcess = cms.untracked.VLuminosityBlockRange('206744:1-206744:155'),

)
process.maxEvents = cms.untracked.PSet( input = cms.untracked.int32(100) )
#-------------------------------------------------------------------------------

# Includes + Global Tag --------------------------------------------------------
process.load("FWCore.MessageService.MessageLogger_cfi")
process.load('Configuration.StandardSequences.Services_cff')
process.load('Configuration.StandardSequences.MagneticField_38T_cff')
process.load('Configuration.Geometry.GeometryIdeal_cff')
process.load('Configuration.Geometry.GeometryPilot2_cff')
process.load('Configuration.StandardSequences.FrontierConditions_GlobalTag_cff')
process.load("Configuration.StandardSequences.Reconstruction_cff")
# process.GlobalTag.globaltag = "START53_V26::All"
process.GlobalTag.globaltag = "FT_53_V21_AN6::All"

#-------------------------------------------------------------------------------
# Configure tuple generation ---------------------------------------------------
process.load("Kappa.Producers.KTuple_cff")
process.kappatuple = cms.EDAnalyzer('KTuple',
	process.kappaTupleDefaultsBlock,
	outputFile = cms.string('skim.root'),
)
process.kappatuple.PFJets.minPt = cms.double(25)
process.kappatuple.verbose = cms.int32(2)
# process.kappatuple.Metadata.fixBrokenLS = cms.untracked.VLuminosityBlockRange('206744:153-206744:153')
process.kappatuple.active = cms.vstring(
	'LV', 'TrackSummary', 'VertexSummary', 'PFMET', 'PFJets', 'JetArea',
)
process.kappatuple.active.append('DataMetadata')
process.kappatuple.active.append('TriggerObjects')

# process.kappatuple.Metadata.hltSource = cms.InputTag("TriggerResults", "", "HLT")
process.kappatuple.Metadata.hltWhitelist = cms.vstring(
	"^HLT_PFJet[0-9]+(U)?(_NoJetID)?(_v[[:digit:]]+)?$",
)
process.kappatuple.Metadata.hltBlacklist = cms.vstring()
process.pathSkim = cms.Path(process.kappatuple)
#-------------------------------------------------------------------------------

# Process schedule -------------------------------------------------------------
process.schedule = cms.Schedule(process.pathSkim)
#-------------------------------------------------------------------------------

