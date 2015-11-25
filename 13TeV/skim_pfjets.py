import FWCore.ParameterSet.Config as cms
from  FWCore.PythonUtilities import LumiList


datatype=None if '@' in '@DATATYPE@' else '@DATATYPE@'
globaltag=None if '@' in '@GLOBALTAG@' else '@GLOBALTAG@'


if datatype is None:
    datatype = 'DATA'

is_data = (datatype.lower() == 'data')

if is_data:
    globaltag = globaltag if globaltag else 'GR_R_74_V12'
    filename = ['/store/data/Run2015D/JetHT/AOD/PromptReco-v4/000/258/159/00000/621D56A1-D16B-E511-9F01-02163E01444E.root']
else:
    globaltag = globaltag if globaltag else 'MCRUN2_74_V8'
    filename = ['']


# Basic process setup ----------------------------------------------------------
process = cms.Process("SKIM")
process.source = cms.Source("PoolSource",
    fileNames = cms.untracked.vstring(filename)
)
process.maxEvents = cms.untracked.PSet( input = cms.untracked.int32(100) )

print "Starting Kappa Skim"

print "GlobalTag: {0}".format(globaltag)
print "Datatype: {0}".format(datatype)

#-------------------------------------------------------------------------------
# Global Tag
#-------------------------------------------------------------------------------
process.load("FWCore.MessageService.MessageLogger_cfi")
process.load('Configuration.StandardSequences.Services_cff')
process.load('Configuration.StandardSequences.MagneticField_38T_cff')
process.load('Configuration.Geometry.GeometryRecoDB_cff')
process.load('Configuration.Geometry.GeometryPilot2_cff')
process.load('Configuration.StandardSequences.FrontierConditions_GlobalTag_condDBv2_cff')
process.load("Configuration.StandardSequences.Reconstruction_cff")
process.GlobalTag.globaltag = globaltag


process.path = cms.Path()

#-------------------------------------------------------------------------------
# Kappa Tuple
#-------------------------------------------------------------------------------
process.load("Kappa.Producers.KTuple_cff")

process.kappatuple = cms.EDAnalyzer('KTuple',
    process.kappaTupleDefaultsBlock,
    outputFile = cms.string('skim.root'),
)
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
    # process.kappatuple.active.append('GenParticles')
process.kappatuple.Info.hltWhitelist = cms.vstring(
    "^HLT_PFJet[0-9]+(U)?(_NoJetID)?(_v[[:digit:]]+)?$",
    "^HLT_DiPFJetAve[0-9]+(U)?(_NoJetID)?(_v[[:digit:]]+)?$",
    "^HLT_ZeroBias?(_v[[:digit:]]+)?$",
)
process.kappatuple.Info.hltBlacklist = cms.vstring()

#--------------------------------------------------------------
# PFCandidates
#--------------------------------------------------------------
from PhysicsTools.SelectorUtils.pvSelector_cfi import pvSelector
process.goodOfflinePrimaryVertices = cms.EDFilter('PrimaryVertexObjectFilter',
    filterParams = pvSelector.clone(maxZ = 24.0),  # ndof >= 4, rho <= 2
)

## ------------------------------------------------------------------------
## TopProjections from CommonTools/ParticleFlow:
process.load("CommonTools.ParticleFlow.pfNoPileUpIso_cff")
process.load("CommonTools.ParticleFlow.pfNoPileUpIso_cff")
process.load("CommonTools.ParticleFlow.pfParticleSelection_cff")


## pf candidate configuration for everything but CHS jets
process.pfPileUpIso.PFCandidates = 'particleFlow'
process.pfPileUpIso.Vertices = 'goodOfflinePrimaryVertices'
process.pfPileUpIso.checkClosestZVertex = True
process.pfNoPileUpIso.bottomCollection = 'particleFlow'


## pf candidate configuration for deltaBeta corrections for muons and electrons 
process.pfNoPileUpChargedHadrons  = process.pfAllChargedHadrons.clone()
process.pfNoPileUpNeutralHadrons = process.pfAllNeutralHadrons.clone()
process.pfNoPileUpPhotons = process.pfAllPhotons.clone()
process.pfPileUpChargedHadrons = process.pfAllChargedHadrons.clone(src = 'pfPileUpIso')

## pf candidate configuration for CHS jets
process.pfPileUp.Vertices				= 'goodOfflinePrimaryVertices'
process.pfPileUp.checkClosestZVertex	= False

# Modifications for new particleFlow Pointers
process.pfPileUp.PFCandidates = cms.InputTag("particleFlowPtrs")
process.pfPileUpIso.PFCandidates = cms.InputTag("particleFlowPtrs")
process.pfNoPileUp.bottomCollection = cms.InputTag("particleFlowPtrs")
process.pfNoPileUpIso.bottomCollection = cms.InputTag("particleFlowPtrs")
#process.pfJetTracksAssociatorAtVertex.jets= cms.InputTag("ak5PFJets")
process.path *= (process.goodOfflinePrimaryVertices * process.pfParticleSelectionSequence
)

#--------------------------------------------------------------
# Jets
#--------------------------------------------------------------

# Kappa jet processing
process.kappaTuple.Jets.minPt = 5.0
process.kappaTuple.Jets.taggers = cms.vstring()

# containers of objects to process
jet_resources = []
cmssw_jets = {}  # algoname: cmssw module
kappa_jets = {}  # algoname: kappa jet config

# GenJets
if not data:
	process.load('RecoJets.Configuration.GenJetParticles_cff')
	process.load('RecoJets.JetProducers.ak5GenJets_cfi')
	jet_resources.append(process.genParticlesForJetsNoNu)
	process.kappaTuple.active += cms.vstring('LV')
	process.kappaTuple.LV.whitelist = cms.vstring('ak5GenJetsNoNu') #default?
	genbase_jet = process.ak5GenJets.clone(src=cms.InputTag("genParticlesForJetsNoNu"), doAreaFastjet=True)

## PFBRECO?
process.load("RecoJets.JetProducers.ak5PFJets_cfi")
pfbase_jet = process.ak5PFJets.clone(srcPVs = 'goodOfflinePrimaryVertices', doAreaFastjet=True)

## PUPPI
# creates reweighted PFCandidates collection 'puppi'
process.load('CommonTools.PileupAlgos.Puppi_cff')
jet_resources.append(process.puppi)
if miniaod:
	process.puppi.candName = cms.InputTag('packedPFCandidates')
	process.puppi.vertexName = cms.InputTag('offlineSlimmedPrimaryVertices')

# create Jet variants
for param in (4, 5, 8):
	# PFJets
	for algo, input_tag in (("", 'particleFlow'), ("CHS", 'pfNoPileUp'), ("Puppi", 'puppi')):
		variant_name = "ak%dPFJets%s" % (param, algo)
		variant_mod = pfbase_jet.clone(src=cms.InputTag(input_tag), rParam=param/10.0)
		cmssw_jets[variant_name] = variant_mod
		# Full Kappa jet definition
		kappa_jets["ak%dPFJets%s"%(param, algo)] = cms.PSet(
			src = cms.InputTag(variant_name),
			PUJetID = cms.InputTag("ak%dPF%sPuJetMva" % (param, algo)),
			PUJetID_full = cms.InputTag("full"),
			QGtagger = cms.InputTag("AK%dPFJets%sQGTagger" % (param, algo)),
			Btagger = cms.InputTag("ak%dPF%s" % (param, algo)),
		)
	# GenJets
	if not data:
		for collection in ("NoNu",): # TODO: add "NoMuNoNu", "" ?
			variant_name = "ak%sGenJets%s" % (param, collection)
			variant_mod = genbase_jet.clone(rParam=param/10.0)
			cmssw_jets[variant_name] = variant_mod
			# GenJets are just KLVs
			process.kappaTuple.LV.whitelist += cms.vstring(variant_name)
# mount generated jets for processing
for name, jet_module in cmssw_jets.iteritems():
	setattr(process, name, jet_module)
for name, pset in kappa_jets.iteritems():
	setattr(process.kappaTuple.Jets, name, pset)
process.path *= reduce(lambda a, b: a * b, jet_resources) * reduce(lambda a, b: a * b, sorted(cmssw_jets.values()))

#-------------------------------------------------------------------------------
# Pileup Density
#-------------------------------------------------------------------------------
from RecoJets.JetProducers.kt4PFJets_cfi import kt4PFJets
process.pileupDensitykt6PFJets = kt4PFJets.clone(rParam=0.6, doRhoFastjet=True, Rho_EtaMax=2.5)

process.kappaTuple.active += cms.vstring('Jets', 'PileupDensity')
process.kappaTuple.PileupDensity.rename = cms.vstring("fixedGridRhoFastjetAll => pileupDensity")

process.path *= (
    process.pileupDensitykt6PFJets
)

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

# final information:
print "------- CONFIGURATION 2 ---------"
print "CMSSW producers:"
for p in str(process.path).split('+'):
    print "  %s" % p
print "Kappa producers:"
for p in sorted(process.kappaTuple.active):
    print "  %s" % p
print "---------------------------------"


