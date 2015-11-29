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
        globaltag = globaltag if globaltag else 'GR_R_74_V8'
        filename = 'root://xrootd.unl.edu//store/mc/RunIISpring15DR74/QCD_Pt-15to7000_TuneCUETP8M1_Flat_13TeV_pythia8/AODSIM/Asympt25nsRaw_MCRUN2_74_V9-v3/00000/62FC22C5-6F12-E511-A1CF-C4346BC8F6D0.root'
    else:
        globaltag = globaltag if globaltag else 'MCRUN2_74_V8'
        filename = '/store/mc/RunIISpring15DR74/QCD_Pt-15to7000_TuneCUETP8M1_Flat_13TeV_pythia8/AODSIM/Asympt25nsRaw_MCRUN2_74_V9-v3/00000/B6C8D7F2-6708-E511-906B-02163E01399C.root'


# Basic process setup ----------------------------------------------------------
process = cms.Process("SKIM")
process.source = cms.Source("PoolSource",
    fileNames = cms.untracked.vstring(filename)
)
process.maxEvents = cms.untracked.PSet(input=cms.untracked.int32(100))

print "Starting Kappa Skim"

print "GlobalTag: {0}".format(globaltag)
print "Datatype is data: {0}".format(is_data)

#-------------------------------------------------------------------------------
# Global Tag
#-------------------------------------------------------------------------------
process.load("FWCore.MessageService.MessageLogger_cfi")
process.load('Configuration.StandardSequences.Services_cff')
process.load("Configuration.Geometry.GeometryRecoDB_cff")
process.load('Configuration.StandardSequences.FrontierConditions_GlobalTag_condDBv2_cff')
process.load("Configuration.StandardSequences.MagneticField_cff")
process.GlobalTag.globaltag = globaltag

process.path = cms.Path()


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
    # process.kappatuple.Info.l1Source = cms.InputTag("")
    # process.kappatuple.Info.hltSource = cms.InputTag("")
    # process.kappatuple.Info.hlTrigger = cms.InputTag("")

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


# Primary Input Collections ###################################################
input_PFCandidates = 'particleFlow'
input_PFCandidatePtrs = 'particleFlowPtrs'
input_PrimaryVertices = 'goodOfflinePrimaryVertices'


#  PFCandidates  ###################################################
## Good offline PV selection: 
# from PhysicsTools.SelectorUtils.pvSelector_cfi import pvSelector
# process.goodOfflinePrimaryVertices = cms.EDFilter('PrimaryVertexObjectFilter',
#     filterParams = pvSelector.clone(maxZ = 24.0),  # ndof >= 4, rho <= 2
# )

## ------------------------------------------------------------------------
## TopProjections from CommonTools/ParticleFlow:
process.load("CommonTools.ParticleFlow.pfNoPileUpIso_cff")
process.load("CommonTools.ParticleFlow.pfNoPileUpIso_cff")
process.load("CommonTools.ParticleFlow.pfParticleSelection_cff")


## pf candidate configuration for everything but CHS jets
process.pfPileUpIso.PFCandidates        = cms.InputTag(input_PFCandidates)
process.pfPileUpIso.Vertices            = cms.InputTag(input_PrimaryVertices)
process.pfPileUpIso.checkClosestZVertex    = True
process.pfNoPileUpIso.bottomCollection    = cms.InputTag(input_PFCandidates)


## pf candidate configuration for deltaBeta corrections for muons and electrons 
process.pfNoPileUpChargedHadrons    = process.pfAllChargedHadrons.clone()
process.pfNoPileUpNeutralHadrons    = process.pfAllNeutralHadrons.clone()
process.pfNoPileUpPhotons            = process.pfAllPhotons.clone()
process.pfPileUpChargedHadrons        = process.pfAllChargedHadrons.clone(src = 'pfPileUpIso')

## pf candidate configuration for CHS jets
process.pfPileUp.Vertices                = cms.InputTag(input_PrimaryVertices)
process.pfPileUp.checkClosestZVertex    = False

# Modifications for new particleFlow Pointers
process.pfPileUp.PFCandidates = cms.InputTag(input_PFCandidatePtrs)
process.pfPileUpIso.PFCandidates = cms.InputTag(input_PFCandidatePtrs)
process.pfNoPileUp.bottomCollection = cms.InputTag(input_PFCandidatePtrs)
process.pfNoPileUpIso.bottomCollection = cms.InputTag(input_PFCandidatePtrs)
process.path *= (process.goodOfflinePrimaryVertices * process.pfParticleSelectionSequence)

#  Jets  ###########################################################
# Kappa jet processing
process.kappatuple.BasicJets.minPt = 5.0

# containers for objects to process
jet_resources = []
cmssw_jets = {}  # algoname: cmssw module
kappa_jets = {}  # algoname: kappa jet config

# GenJets
if not is_data:
    process.load('RecoJets.Configuration.GenJetParticles_cff')
    process.load('RecoJets.JetProducers.ak5GenJets_cfi')
    jet_resources.append(process.genParticlesForJetsNoNu)
    process.kappatuple.LV.whitelist = cms.vstring('ak5GenJetsNoNu') #default?
    genbase_jet = process.ak5GenJets.clone(src=cms.InputTag("genParticlesForJetsNoNu"), doAreaFastjet=True)

## PFBRECO?
process.load("RecoJets.JetProducers.ak5PFJets_cfi")
pfbase_jet = process.ak5PFJets.clone(srcPVs = 'goodOfflinePrimaryVertices', doAreaFastjet=True)

# create Jet variants
for param in (4, 5, 7, 8):
    # PFJets
    algos_and_tags = [("", input_PFCandidates), ("CHS", 'pfNoPileUp')]
    for algo, input_tag in algos_and_tags:
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
    if not is_data:
        for collection in ("NoNu",): # TODO: add "NoMuNoNu", "" ?
            variant_name = "ak%sGenJets%s" % (param, collection)
            variant_mod = genbase_jet.clone(rParam=param/10.0)
            cmssw_jets[variant_name] = variant_mod
            # GenJets are just KLVs
            process.kappatuple.LV.whitelist += cms.vstring(variant_name)
# mount generated jets for processing
for name, jet_module in cmssw_jets.iteritems():
    setattr(process, name, jet_module)
for name, pset in kappa_jets.iteritems():
    setattr(process.kappatuple.BasicJets, name, pset)


process.path *= reduce(lambda a, b: a * b, jet_resources + sorted(cmssw_jets.values()))
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
for p in sorted(process.kappatuple.active):
    print "  %s" % p
print "---------------------------------"
