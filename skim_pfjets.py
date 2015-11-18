import FWCore.ParameterSet.Config as cms
from  FWCore.PythonUtilities import LumiList


datatype=None if '@' in '@DATATYPE@' else '@DATATYPE@'
globaltag=None if '@' in '@GLOBALTAG@' else '@GLOBALTAG@'


if datatype is None:
    datatype = 'DATA'

is_data = (datatype.lower() == 'data')

if is_data:
    globaltag = globaltag if globaltag else 'FT53_V21A_AN6::All'
    # filename = 'root://xrootd.unl.edu//store/data/Run2012A/Jet/AOD/22Jan2013-v1/30000/F8B135C2-2072-E211-BA5A-00304867BEDE.root'
    # filename = 'root://xrootd.unl.edu//store/data/Run2012A/Jet/AOD/22Jan2013-v1/20000/3E1876AD-7F72-E211-A2B7-003048678F8C.root'
    filename = ["/store/data/Run2012D/JetHT/AOD/22Jan2013-v1/10002/04FAA943-9D97-E211-830B-E0CB4E1A11A2.root", "/store/data/Run2012D/JetHT/AOD/22Jan2013-v1/10002/D47C39F3-A197-E211-94A5-E0CB4E1A118B.root"]
else:
    globaltag = globaltag if globaltag else 'START53_V27::All'
    filename = 'root://xrootd.unl.edu//store/mc/Summer12_DR53X/QCD_Pt-15to3000_TuneZ2star_Flat_8TeV_pythia6/AODSIM/PU_S10_START53_V7A-v1/0000/004CB136-A1D3-E111-B958-0030487E4B8D.root'


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
process.load('Configuration.Geometry.GeometryIdeal_cff')
process.load('Configuration.Geometry.GeometryPilot2_cff')
process.load('Configuration.StandardSequences.FrontierConditions_GlobalTag_cff')
process.load("Configuration.StandardSequences.Reconstruction_cff")
process.GlobalTag.globaltag = globaltag

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
# HLT Filter
#-------------------------------------------------------------------------------

#import HLTrigger.HLTfilters.hltHighLevel_cfi as hlt
#process.hlt_pfjets = hlt.hltHighLevel.clone(
#    HLTPaths = ["HLT_PFJet*_v*"],
#    throw = False
#    )
#
#process.hlt_pfjetspath = cms.Path(process.hlt_pfjets)

#-------------------------------------------------------------------------------
# MET Filter FilterResults
#-------------------------------------------------------------------------------

# process.load('RecoMET.METFilters.ecalLaserCorrFilter_cfi')
# # Create good vertices for the trackingFailure MET filter
# process.goodVertices = cms.EDFilter("VertexSelector",
#     filter = cms.bool(False),
#     src = cms.InputTag("offlinePrimaryVertices"),
#     cut = cms.string("!isFake && ndof > 4 && abs(z) <= 24 && position.rho < 2"),
# )
# # The good primary vertex filter for other MET filters
# process.primaryVertexFilter = cms.EDFilter("VertexSelector",
#     filter = cms.bool(True),
#     src = cms.InputTag("offlinePrimaryVertices"),
#     cut = cms.string("!isFake && ndof > 4 && abs(z) <= 24 && position.Rho <= 2"),
# )
# process.noscraping = cms.EDFilter("FilterOutScraping",
#     applyfilter = cms.untracked.bool(True),
#     debugOn = cms.untracked.bool(False),
#     numtrack = cms.untracked.uint32(10),
#     thresh = cms.untracked.double(0.25)
# )
# process.load('CommonTools.RecoAlgos.HBHENoiseFilter_cfi')
# process.load('RecoMET.METFilters.CSCTightHaloFilter_cfi')
# process.load('RecoMET.METFilters.hcalLaserEventFilter_cfi')
# process.hcalLaserEventFilter.vetoByRunEventNumber = cms.untracked.bool(False)
# process.hcalLaserEventFilter.vetoByHBHEOccupancy = cms.untracked.bool(True)
# process.load('RecoMET.METFilters.EcalDeadCellTriggerPrimitiveFilter_cfi')
# process.EcalDeadCellTriggerPrimitiveFilter.tpDigiCollection = cms.InputTag("ecalTPSkimNA")
# process.load('RecoMET.METFilters.EcalDeadCellBoundaryEnergyFilter_cfi')
# process.load('RecoMET.METFilters.eeBadScFilter_cfi')
# process.load('RecoMET.METFilters.eeNoiseFilter_cfi')
# process.load('RecoMET.METFilters.ecalLaserCorrFilter_cfi')
# process.load('RecoMET.METFilters.trackingFailureFilter_cfi')
# process.load('RecoMET.METFilters.inconsistentMuonPFCandidateFilter_cfi')
# process.load('RecoMET.METFilters.greedyMuonPFCandidateFilter_cfi')
#
# process.hcalLaserEventFilter.taggingMode = cms.bool(True)
# process.EcalDeadCellTriggerPrimitiveFilter.taggingMode = cms.bool(True)
# process.EcalDeadCellBoundaryEnergyFilter.taggingMode = cms.bool(True)
# process.eeBadScFilter.taggingMode = cms.bool(True)
# process.eeNoiseFilter.taggingMode = cms.bool(True)
# process.ecalLaserCorrFilter.taggingMode = cms.bool(True)
# process.trackingFailureFilter.taggingMode = cms.bool(True)
# process.inconsistentMuonPFCandidateFilter.taggingMode = cms.bool(True)
# process.greedyMuonPFCandidateFilter.taggingMode = cms.bool(True)
# process.beamScrapingFilter = process.inconsistentMuonPFCandidateFilter.clone(
#     ptMin = cms.double(5000.0)
# )
# process.hcalNoiseFilter = process.beamScrapingFilter.clone()
# process.beamHaloFilter = process.beamScrapingFilter.clone()
# process.filtersSeq = cms.Sequence(
#     process.primaryVertexFilter +
#     process.hcalLaserEventFilter +
#     process.EcalDeadCellTriggerPrimitiveFilter +
#     process.EcalDeadCellBoundaryEnergyFilter +
#     process.eeBadScFilter +
#     process.eeNoiseFilter +
#     process.ecalLaserCorrFilter +
#     process.goodVertices + process.trackingFailureFilter +
#     process.inconsistentMuonPFCandidateFilter +
#     process.greedyMuonPFCandidateFilter +
#     process.noscraping * process.beamScrapingFilter +
#     ~process.noscraping * ~process.beamScrapingFilter +
#     process.HBHENoiseFilter * process.hcalNoiseFilter +
#     ~process.HBHENoiseFilter * ~process.hcalNoiseFilter +
#     process.CSCTightHaloFilter * process.beamHaloFilter +
#     ~process.CSCTightHaloFilter * ~process.beamHaloFilter
# )
# process.metFilters = cms.Path(process.filtersSeq)
#-------------------------------------------------------------------------------
# JEC
#-------------------------------------------------------------------------------
process.load("CondCore.DBCommon.CondDBCommon_cfi")
process.load('JetMETCorrections.Configuration.DefaultJEC_cff')
process.load('JetMETCorrections.Configuration.JetCorrectionProducers_cff')
process.load('JetMETCorrections.Configuration.JetCorrectionProducersAllAlgos_cff')

if is_data:
    if is_data:
        jec_string = 'DATA'
    else:
        jec_string = 'MC'
    process.jecsource = cms.ESSource("PoolDBESSource",
          DBParameters = cms.PSet(
            messageLevel = cms.untracked.int32(0)
            ),
          timetype = cms.string('runnumber'),
          toGet = cms.VPSet(
          cms.PSet(
                record = cms.string('JetCorrectionsRecord'),
                tag    = cms.string('JetCorrectorParametersCollection_Winter14_V5_{0}_AK5PF'.format(jec_string)),
                # tag    = cms.string('JetCorrectorParametersCollection_Summer12_V3_MC_AK5PF'),
                label  = cms.untracked.string('AK5PF')
                ),
          cms.PSet(
                record = cms.string('JetCorrectionsRecord'),
                tag    = cms.string('JetCorrectorParametersCollection_Winter14_V5_{0}_AK7PF'.format(jec_string)),
                # tag    = cms.string('JetCorrectorParametersCollection_Summer12_V3_MC_AK7PF'),
                label  = cms.untracked.string('AK7PF')
                ),
          ), 
          connect = cms.string('sqlite:Winter14_V5_{0}.db'.format(jec_string))
    )
    # add an es_prefer statement to resolve a possible conflict from simultaneous connection to a global tag
    process.es_prefer_jec = cms.ESPrefer('PoolDBESSource','jecsource')
else:
    # In this case the JEC from the GT (START_XYZ) should be used
    pass
if is_data:
    process.jec = cms.Path(process.ak5PFJetsL1FastL2L3Residual + process.ak7PFJetsL1FastL2L3Residual)
else:
    process.jec = cms.Path(process.ak5PFJetsL1FastL2L3 + process.ak7PFJetsL1FastL2L3)
#-------------------------------------------------------------------------------
# MET Filters
#-------------------------------------------------------------------------------

process.load("RecoMET.METFilters.metFilters_cff")

#-------------------------------------------------------------------------------
# Kappa Tuple
#-------------------------------------------------------------------------------
process.load("Kappa.Producers.KTuple_cff")
process.kappatuple = cms.EDAnalyzer('KTuple',
    process.kappaTupleDefaultsBlock,
    outputFile = cms.string('skim.root'),
)
process.kappatuple.BasicJets.minPt = cms.double(20)
process.kappatuple.BasicJets.maxEta = cms.double(5.)
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
    # process.kappatuple.active.append('GenParticles')
process.kappatuple.Info.hltWhitelist = cms.vstring(
    "^HLT_PFJet[0-9]+(U)?(_NoJetID)?(_v[[:digit:]]+)?$",
    "^HLT_DiPFJetAve[0-9]+(U)?(_NoJetID)?(_v[[:digit:]]+)?$",
    "^HLT_ZeroBias?(_v[[:digit:]]+)?$",
)
process.kappatuple.Info.hltBlacklist = cms.vstring()

process.kappa_path = cms.Path(process.metFilters + process.kappatuple)

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
process.schedule = cms.Schedule(
                                process.jec,
                                process.kappa_path
                                )
