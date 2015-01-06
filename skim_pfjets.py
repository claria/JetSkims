import FWCore.ParameterSet.Config as cms
from  FWCore.PythonUtilities import LumiList

def get_process(datatype, globaltag):

    if not datatype:
        datatype = 'DATA'

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
    print "GT: {0}".format(globaltag)
    print "TYPE: {0}".format(datatype)

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
    #if is_data:
    #    process.source.lumisToProcess = LumiList.LumiList(filename = 'Cert_190456-208686_8TeV_22Jan2013ReReco_Collisions12_JSON.txt').getVLuminosityBlockRange()


    #-------------------------------------------------------------------------------
    # Filter Results
    #-------------------------------------------------------------------------------
    process.load('CommonTools.RecoAlgos.HBHENoiseFilterResultProducer_cfi')
    process.filterresults = cms.Path(process.HBHENoiseFilterResultProducer)
 
    #-------------------------------------------------------------------------------
    # Kappa Tuple
    #-------------------------------------------------------------------------------
    process.load("Kappa.Producers.KTuple_cff")
    process.kappatuple = cms.EDAnalyzer('KTuple',
        process.kappaTupleDefaultsBlock,
        outputFile = cms.string('skim.root'),
    )
    process.kappatuple.PFJets.minPt = cms.double(20)
    process.kappatuple.PFJets.maxEta = cms.double(5.)
    process.kappatuple.PFJets.whitelist = cms.vstring("recoPFJets_ak5PFJets.*", "recoPFJets_ak7PFJets.*")
    process.kappatuple.verbose = cms.int32(0)
    process.kappatuple.active = cms.vstring(
        'LV', 'TrackSummary', 'VertexSummary', 'FilterSummary', 'PFMET', 'PFJets', 'JetArea', 'HCALNoiseSummary',
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

    if is_data:
        jec_string = 'DATA'
    else:
        jec_string = 'MC'
    # process.jecsource = cms.ESSource("PoolDBESSource",
    #       DBParameters = cms.PSet(
    #         messageLevel = cms.untracked.int32(0)
    #         ),
    #       timetype = cms.string('runnumber'),
    #       toGet = cms.VPSet(
    #       cms.PSet(
    #             record = cms.string('JetCorrectionsRecord'),
    #             tag    = cms.string('JetCorrectorParametersCollection_Winter14_V5_{0}_AK5PF'.format(jec_string)),
    #             # tag    = cms.string('JetCorrectorParametersCollection_Summer12_V3_MC_AK5PF'),
    #             label  = cms.untracked.string('AK5PF')
    #             ),
    #       cms.PSet(
    #             record = cms.string('JetCorrectionsRecord'),
    #             tag    = cms.string('JetCorrectorParametersCollection_Winter14_V5_{0}_AK7PF'.format(jec_string)),
    #             # tag    = cms.string('JetCorrectorParametersCollection_Summer12_V3_MC_AK7PF'),
    #             label  = cms.untracked.string('AK7PF')
    #             ),
    #       ), 
    #       connect = cms.string('sqlite:Winter14_V5_{0}.db'.format(jec_string))
    # )
    ## add an es_prefer statement to resolve a possible conflict from simultaneous connection to a global tag
    # process.es_prefer_jec = cms.ESPrefer('PoolDBESSource','jecsource')

    process.load('JetMETCorrections.Configuration.DefaultJEC_cff')
    process.load('JetMETCorrections.Configuration.JetCorrectionProducers_cff')
    process.load('JetMETCorrections.Configuration.JetCorrectionProducersAllAlgos_cff')
    process.load('JetMETCorrections.Configuration.JetCorrectionServices_cff')
    process.load('JetMETCorrections.Configuration.JetCorrectionServicesAllAlgos_cff')


    process.ak5PFJetsL2L3   = cms.EDProducer('PFJetCorrectionProducer',
       src         = cms.InputTag('ak5PFJets'),
       correctors  = cms.vstring('ak5PFL2L3')
    )
    process.ak7PFJetsL2L3   = cms.EDProducer('PFJetCorrectionProducer',
       src         = cms.InputTag('ak7PFJets'),
       correctors  = cms.vstring('ak7PFL2L3')
    )
    process.ak5PFJetsL1Fast   = cms.EDProducer('PFJetCorrectionProducer',
       src         = cms.InputTag('ak5PFJets'),
       correctors  = cms.vstring('ak5PFL1Fastjet')
    )
    process.ak7PFJetsL1Fast   = cms.EDProducer('PFJetCorrectionProducer',
       src         = cms.InputTag('ak7PFJets'),
       correctors  = cms.vstring('ak7PFL1Fastjet')
    )

    process.jec = cms.Path(process.ak5PFJetsL1Fast +
                           process.ak7PFJetsL1Fast +
                           process.ak5PFJetsL2L3 +
                           process.ak7PFJetsL2L3 +
                           process.ak5PFJetsL1FastL2L3Residual +
                           process.ak7PFJetsL1FastL2L3Residual
                           )

    #-------------------------------------------------------------------------------
    # Process schedule
    #-------------------------------------------------------------------------------

    process.schedule = cms.Schedule(
            process.filterresults,
            process.jec,
            process.pathSkim,
            )

    return process

if __name__ == '__main__':
    process = get_process(datatype=None if '@' in '@DATATYPE@' else '@DATATYPE@',
                          globaltag=None if '@' in '@GLOBALTAG@' else '@GLOBALTAG@')
