import FWCore.ParameterSet.Config as cms


def get_process(datatype, globaltag):

	if not datatype:
		datatype = 'MC'

	is_data = datatype.lower() == 'data'
	
	if is_data:
		globaltag = globaltag if globaltag else 'FT53_V21A_AN6::All'
		filename = 'root://xrootd.unl.edu//store/data/Run2012D/JetMon/AOD/22Jan2013-v1/10000/00187058-1792-E211-AF2C-90B11C18BECE.root'
	else:
		globaltag = globaltag if globaltag else 'START53_V26::All'
		filename = 'root://xrootd.unl.edu//store/mc/Summer12_DR53X/QCD_Pt-15to3000_TuneZ2star_Flat_8TeV_pythia6/AODSIM/PU_S10_START53_V7A-v1/0000/004CB136-A1D3-E111-B958-0030487E4B8D.root'
	
	# Basic process setup ----------------------------------------------------------
	process = cms.Process("kappaSkim")
	process.source = cms.Source("PoolSource",
		fileNames = cms.untracked.vstring(filename)
	)
	process.maxEvents = cms.untracked.PSet( input = cms.untracked.int32(-1) )
	#-------------------------------------------------------------------------------
	
	print "A: GT:", globaltag, "| TYPE:", datatype,
	
	# Includes + Global Tag --------------------------------------------------------
	process.load("FWCore.MessageService.MessageLogger_cfi")
	process.load('Configuration.StandardSequences.Services_cff')
	process.load('Configuration.StandardSequences.MagneticField_38T_cff')
	process.load('Configuration.Geometry.GeometryIdeal_cff')
	process.load('Configuration.Geometry.GeometryPilot2_cff')
	process.load('Configuration.StandardSequences.FrontierConditions_GlobalTag_cff')
	process.load("Configuration.StandardSequences.Reconstruction_cff")
	process.GlobalTag.globaltag = globaltag
	#-------------------------------------------------------------------------------
	# Check if a gc 
	
	# Configure tuple generation ---------------------------------------------------
	process.load("Kappa.Producers.KTuple_cff")
	process.kappatuple = cms.EDAnalyzer('KTuple',
		process.kappaTupleDefaultsBlock,
		outputFile = cms.string('skim.root'),
	)
	process.kappatuple.PFJets.minPt = cms.double(25)
	process.kappatuple.verbose = cms.int32(0)
	process.kappatuple.active = cms.vstring(
		'LV', 'TrackSummary', 'VertexSummary', 'PFMET', 'PFJets', 'JetArea',
	)
	if is_data:
		process.kappatuple.active.append('DataMetadata')
		process.kappatuple.active.append('TriggerObjects')
	else:
		process.kappatuple.active.append('GenMetadata')
		# process.kappatuple.active.append('GenParticles')
	
	process.kappatuple.Metadata.hltWhitelist = cms.vstring(
		"^HLT_PFJet[0-9]+(U)?(_NoJetID)?(_v[[:digit:]]+)?$",
	)
	process.kappatuple.Metadata.hltBlacklist = cms.vstring()
	process.pathSkim = cms.Path(process.kappatuple)
	#-------------------------------------------------------------------------------
	
	# Process schedule -------------------------------------------------------------
	process.schedule = cms.Schedule(process.pathSkim)
	#-------------------------------------------------------------------------------
	return process

if __name__ == '__main__':
	process = get_process(datatype=None if '@' in '@DATATYPE@' else '@DATATYPE@',
						  globaltag=None if '@' in '@GLOBALTAG@' else '@GLOBALTAG@')
