# JetSkims

Checkout:

```
scram project CMSSW_5_3_26  
cd CMSSW_5_3_26  
cmsenv  
git-cms-addpkg JetMETCorrections  
git-cms-addpkg RecoMET  
cd src  
git clone git@github.com:KappaAnalysis/Kappa.git  
cd Kappa  
git checkout Kappa_2_0_1  
cd $CMSSW_BASE  
scram b -j8
```

Test config:
```
cmsRun skim_pfjets.py
```
