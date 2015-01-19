import FWCore.ParameterSet.Config as cms
from  FWCore.PythonUtilities import LumiList


datatype=None if '@' in '@DATATYPE@' else '@DATATYPE@'
globaltag=None if '@' in '@GLOBALTAG@' else '@GLOBALTAG@'


if datatype is None:
    datatype = 'MC'

is_data = (datatype.lower() == 'data')

if is_data:
    globaltag = globaltag if globaltag else 'FT53_V21A_AN6::All'
    filename = 'root://xrootd.unl.edu//store/data/Run2012A/Jet/AOD/22Jan2013-v1/30000/F8B135C2-2072-E211-BA5A-00304867BEDE.root'
else:
    globaltag = globaltag if globaltag else 'START53_V26::All'
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
if is_data:
   process.source.lumisToProcess = LumiList.LumiList(filename = 'Cert_190456-208686_8TeV_22Jan2013ReReco_Collisions12_JSON.txt').getVLuminosityBlockRange()

print "Using HLT Filter path"
import HLTrigger.HLTfilters.hltHighLevel_cfi as hlt
process.hlt_pfjets = hlt.hltHighLevel.clone(
    HLTPaths = ["HLT_PFJet*_v*"],
    throw = False
    )

process.hlt_pfjetspath = cms.Path(process.hlt_pfjets)

print "Using MET Filters"
## The iso-based HBHE noise filter ___________________________________________||
process.load('CommonTools.RecoAlgos.HBHENoiseFilter_cfi')
process.load('CommonTools.RecoAlgos.HBHENoiseFilterResultProducer_cfi')
## The CSC beam halo tight filter ____________________________________________||
process.load('RecoMET.METFilters.CSCTightHaloFilter_cfi')
## The HCAL laser filter _____________________________________________________||
process.load('RecoMET.METFilters.hcalLaserEventFilter_cfi')
## The ECAL dead cell trigger primitive filter _______________________________||
process.load('RecoMET.METFilters.EcalDeadCellTriggerPrimitiveFilter_cfi')
## The EE bad SuperCrystal filter ____________________________________________||
process.load('RecoMET.METFilters.eeBadScFilter_cfi')
## The ECAL laser correction filter
process.load('RecoMET.METFilters.ecalLaserCorrFilter_cfi')
## The Good vertices collection needed by the tracking failure filter ________||
process.goodVertices = cms.EDFilter(
  "VertexSelector",
  filter = cms.bool(False),
  src = cms.InputTag("offlinePrimaryVertices"),
  cut = cms.string("!isFake && ndof > 4 && abs(z) <= 24 && position.rho < 2")
)
## The tracking failure filter _______________________________________________||
process.load('RecoMET.METFilters.trackingFailureFilter_cfi')
## The tracking POG filters __________________________________________________||
process.load('RecoMET.METFilters.trackingPOGFilters_cff')
## NOTE: to make tagging mode of the tracking POG filters (three of them), please do:
##    manystripclus53X.taggedMode = cms.untracked.bool(True)
##    manystripclus53X.forcedValue = cms.untracked.bool(False)
##    toomanystripclus53X.taggedMode = cms.untracked.bool(True)
##    toomanystripclus53X.forcedValue = cms.untracked.bool(False)
##    logErrorTooManyClusters.taggedMode = cms.untracked.bool(True)
##    logErrorTooManyClusters.forcedValue = cms.untracked.bool(False)
## Also the stored boolean for the three filters is opposite to what we usually
## have for other filters, i.e., true means rejected bad events while false means 
## good events.
process.HBHENoiseFilter.taggingMode = cms.bool(True)
process.CSCTightHaloFilter.taggingMode = cms.bool(True)
process.hcalLaserEventFilter.taggingMode = cms.bool(True)
process.EcalDeadCellTriggerPrimitiveFilter.taggingMode = cms.bool(True)
process.trackingFailureFilter.taggingMode = cms.bool(True)
process.eeBadScFilter.taggingMode = cms.bool(True)
process.ecalLaserCorrFilter.taggingMode = cms.bool(True)
# process.trkPOGFilters.taggingMode = cms.bool(True)
# TODO: trkPOGFilters are not putting a product in the event, so no passing to FilterVertexSummary possible
process.metFilters = cms.Sequence(
   process.HBHENoiseFilterResultProducer + process.HBHENoiseFilter +
   process.CSCTightHaloFilter +
   process.hcalLaserEventFilter +
   process.EcalDeadCellTriggerPrimitiveFilter +
   process.goodVertices * process.trackingFailureFilter +
   process.eeBadScFilter +
   process.ecalLaserCorrFilter +
   process.trkPOGFilters
)
#-------------------------------------------------------------------------------
# Filter Results
#-------------------------------------------------------------------------------
# process.load('CommonTools.RecoAlgos.HBHENoiseFilterResultProducer_cfi')
# process.filterresults = cms.Path(process.HBHENoiseFilterResultProducer)
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
process.kappatuple.GenJets.whitelist = cms.vstring("recoGenJets_ak5GenJets.*", "recoGenJets_ak7GenJets.*")
process.kappatuple.verbose = cms.int32(0)
process.kappatuple.active = cms.vstring(
    'TrackSummary', 'VertexSummary', 'FilterSummary', 'MET', 'BasicJets', 'PileupDensity', 'HCALNoiseSummary',
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
)
process.kappatuple.Info.hltBlacklist = cms.vstring()

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

process.jec = cms.Sequence(process.ak5PFJetsL1FastL2L3Residual + process.ak7PFJetsL1FastL2L3Residual)

#-------------------------------------------------------------------------------
# Process schedule
#-------------------------------------------------------------------------------

process.skim_path = cms.Path(process.metFilters *
                             process.hlt_pfjets *
                             process.jec *
                             process.kappatuple
                             )
