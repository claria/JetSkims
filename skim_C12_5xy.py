import FWCore.ParameterSet.Config as cms

# Basic process setup ----------------------------------------------------------
process = cms.Process("kappaSkim")
process.source = cms.Source("PoolSource", fileNames = cms.untracked.vstring(
	'file:///home/cguenth/Testfiles/Jet2012A.root',
))
process.maxEvents = cms.untracked.PSet( input = cms.untracked.int32(10) )
#-------------------------------------------------------------------------------

# Includes + Global Tag --------------------------------------------------------
process.load("FWCore.MessageService.MessageLogger_cfi")
process.load('Configuration.StandardSequences.Services_cff')
process.load('Configuration.StandardSequences.MagneticField_38T_cff')
process.load('Configuration.Geometry.GeometryIdeal_cff')
process.load('Configuration.Geometry.GeometryPilot2_cff')
process.load('Configuration.StandardSequences.FrontierConditions_GlobalTag_cff')
process.load("Configuration.StandardSequences.Reconstruction_cff")
#process.GlobalTag.globaltag = 'FT_53_V10_AN3::All'
process.GlobalTag.globaltag = '@GLOBALTAG@'
#-------------------------------------------------------------------------------

# Configure tuple generation ---------------------------------------------------
process.load("Kappa.Producers.KTuple_cff")
process.kappatuple = cms.EDAnalyzer('KTuple',
	process.kappaTupleDefaultsBlock,
	outputFile = cms.string('skim.root'),
)
process.kappatuple.PFJets.minPt = cms.double(25)
process.kappatuple.verbose = cms.int32(1)
process.kappatuple.active = cms.vstring(@ACTIVE@,
	'LV', 'TrackSummary', 'VertexSummary', 'VertexSummary', 'PFMET', 'PFJets', 'JetArea',
)
process.kappatuple.Metadata.hltWhitelist = cms.vstring(
	"^HLT_PFJet[0-9]+(U)?(_NoJetID)?(_v[[:digit:]]+)?$",
)
process.kappatuple.Metadata.hltBlacklist = cms.vstring()
process.pathSkim = cms.Path(process.kappatuple)
#-------------------------------------------------------------------------------

# Process schedule -------------------------------------------------------------
process.schedule = cms.Schedule(process.pathSkim)
#-------------------------------------------------------------------------------
