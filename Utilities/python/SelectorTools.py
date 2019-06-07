#!/usr/bin/env python
import ROOT
import glob
import datetime
# other python files
import ConfigureJobs, OutputTools
import sys
import os


# applySelector function creates an extra_inputs array, appends ntuple variable
# next, looking at the channel array. For every channel, there is an extra_inputs array, 
# called inputs (it is a root list) with the addition of tchannel. 
def applySelector(filelist, selector_name, selection, 
        rootfile,
        analysis="WZxsec2016", channels=["eee", "eem", "emm", "mmm"], 
        extra_inputs = [],
        nanoAOD=False,
        addSumweights=True,
        proof=False):
     
    ntuple = ROOT.TNamed("ntupleType", "NanoAOD" if nanoAOD else "UWVV")
    extra_inputs.append(ntuple)
    for i, chan in enumerate(channels):
        #TList is for TObjects; so basically creating specific type of list...
        inputs = ROOT.TList()
        for inp in extra_inputs:
            inputs.Add(inp)
        tchannel = ROOT.TNamed("channel", chan)
        inputs.Add(tchannel)
        # calling function getListOfFiles from Configure Jobs file
        for dataset in ConfigureJobs.getListOfFiles(filelist, selection):
            # getattr(object, name[, default]); returns the value of the named attribute of 
            # object. i.e. looking at the class ROOT. Finding what corresponds to selector_name
            select = getattr(ROOT, selector_name)()
            
            # ??? #####################################################################
            select.SetInputList(inputs)
            print "Processing channel %s for dataset %s" % (chan, dataset)
            try:
                file_path = ConfigureJobs.getInputFilesPath(dataset, 
                                                            selection, analysis)
                processLocalFiles(select, file_path, chan, nanoAOD)
            except ValueError as e:
                print e
                continue
            output_list = select.GetOutputList()
            dataset_list = output_list.FindObject(dataset)
            if not dataset_list or dataset_list.ClassName() != "TList":
                print "WARNING: No output found for dataset %s" % dataset
                dataset_list = output_list.FindObject("Unknown")
                if dataset_list and dataset_list.ClassName() == "TList":
                    print 'WARNING: Falling back to dataset "Unknown"'
                else:
                    print 'WARNING: Skipping dataset %s' % dataset
                    continue
            # Only add for one channel
            if addSumweights and i == 0:
                if nanoAOD:
                    sumWeightsBranch = "genEventSumw"
                    metaTreeName = "Runs"
                else:
                    sumWeightsBranch = "sumWeights"
                    metaTreeName = "metaInfo/metaInfo"
                #TChain is a collection of TFile objects. metaTreeName is the name of the TTree object
                meta_chain = ROOT.TChain(metaTreeName)
                meta_chain.Add(file_path)
                sumweights = ROOT.TH1D("sumweights", "sumweights", 1, 0, 10)
                meta_chain.Draw("1>>sumweights", sumWeightsBranch)
                dataset_list.Add(ROOT.gROOT.FindObject("sumweights"))

            OutputTools.writeOutputListItem(dataset_list, rootfile)
            output_list.Delete()
            ROOT.gROOT.GetList().Delete()
        #if chain.GetEntries() != 0 and proof:
        #proof_path = "_".join([analysis, selection+("#/%s/ntuple" % chan)])
        #ROOT.gProof.Process(proof_path, select, "")

def processLocalFiles(selector, file_path, chan, nanoAOD):
    if not (os.path.isfile(file_path) or os.path.isdir(file_path.rsplit("/", 1)[0])):
        raise ValueError("Invalid path! Skipping dataset. Path was %s" 
            % file_path)
    for filename in glob.glob(file_path):
        rtfile = ROOT.TFile(filename)
        tree_name = "Events" if nanoAOD else "%s/ntuple" % chan
        tree = rtfile.Get(tree_name)
        if not tree:
            raise ValueError(("tree %s/ntuple not found for file %s. " \
                    "Probably it is corrupted") % (chan, filename)
            )

        tree.Process(selector, "")
