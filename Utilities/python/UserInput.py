import json
import glob
import argparse
import datetime
from collections import OrderedDict
import ConfigureJobs
import sys

def getHistExpr(hist_names, selection):
    info = ROOT.TList()
    info.SetName("histinfo")
    for hist_name in hist_names:
        bin_info = ConfigHistTools.getHistBinInfo(manager_path, selection, hist_name)
        if "TH1" in ConfigHistTools.getHistType(manager_path, selection, hist_name):
            bin_expr = "{nbins}, {xmin}, {xmax}".format(**bin_info)
        else:
            bin_expr = "{nbinsx}, {xmin}, {xmax}, {nbinsy}, {ymin}, {ymax}".format(**bin_info)
        info.Add(ROOT.TNamed(hist_name, " $ ".join([hist_name, bin_expr])))
    return info

def readAllJson(json_file_path):
    json_info = {}
    for json_file in glob.glob(json_file_path):
        json_info.update(readJson(json_file))
    return json_info

def readJson(json_file_name):
    json_info = {}
    with open(json_file_name) as json_file:
        try:
            json_info = json.load(json_file)
        except ValueError as err:
            print "Error reading JSON file %s. The error message was:" % json_file_name 
            print(err)
    return json_info

def getDefaultParser():
    parser = argparse.ArgumentParser()
    parser.add_argument("-s", "--selection", type=str,
                        required=True, help="Name of selection to make, "
                        " as defined in Cuts/<analysis>/<selection>.json")
    parser.add_argument("-v", "--version", type=str,
                        required=False, default="1",
                        help="Version number, appended to name")
    parser.add_argument("-a", "--analysis", type=str,
                        required=False, default="WZxsec2016",
                        help="Analysis name, used in selecting the cut json")
    parser.add_argument("-f", "--filenames", 
                        type=lambda x : [i.strip() for i in x.split(',')],
                        default=["WZxsec2016"], help="List of input file names, "
                        "as defined in AnalysisDatasetManager, separated "
                        "by commas")
    return parser

def getHistInfo(analysis, input_hists, noConfig=False):
    if noConfig:
        print "INFO: assuming histogram information is specified in selector"
        return (input_hists, [])

    manager_path = ConfigureJobs.getManagerPath()
    sys.path.append("/".join([manager_path, 
        "AnalysisDatasetManager", "Utilities/python"]))
    import ConfigHistTools

    # For histograms produced with some postprocessing on the hist file
    excludedHistPatterns = ["wCR", "unrolled", "CutFlow", "YieldByChannel"]
    config_hists = ConfigHistTools.getAllHistNames(manager_path, analysis) \
        if "all" in input_hists else input_hists

    hists = filter(lambda x : any(y in x for y in excludedHistPatterns), config_hists)
    hist_inputs = [getHistExpr(hists, analysis)]

    return hists, hist_inputs
