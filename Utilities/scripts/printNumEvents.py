#!/usr/bin/env python
import ROOT
import argparse
import os
from python import ConfigureJobs,ApplySelection
import datetime

parser = argparse.ArgumentParser() 
parser.add_argument("-f", "--filelist", 
                    type=lambda x : [i.strip() for i in x.split(',')],
                    required=True, help="List of input file names "
                    "to be processed (separated by commas)")
parser.add_argument("-s", "--selection", required=True)
parser.add_argument("-p", "--printEventNums", action='store_true')
parser.add_argument("-t", "--printTrigger", action='store_true')
parser.add_argument("--printDetail", action='store_true')
parser.add_argument("-d", "--checkDuplicates", action='store_true')
parser.add_argument("-m", "--cut_string", required=False, type=str,
                    default="")
parser.add_argument("-c", "--channels", required=False, type=str,
                    default="eee,eem,emm,mmm")
parser.add_argument("-o", "--output_dir", required=False, type=str,
                    default="")
args = parser.parse_args()
path = "/cms/kdlong" if "hep.wisc.edu" in os.environ['HOSTNAME'] else \
        "/afs/cern.ch/user/k/kelong/work"
filelist = ConfigureJobs.getListOfFiles(args.filelist, path) if \
    not any("root" in x for x in args.filelist) else args.filelist
states = [x.strip() for x in args.channels.split(",")]
totals = dict((i,0) for i in states)
total = 0
if args.checkDuplicates:
    eventArray = []
metaChain = ROOT.TChain("metaInfo/metaInfo")
for name in filelist:
    print name
    if ".root" not in name:
        try:
            file_path = ConfigureJobs.getInputFilesPath(name, path,
                args.selection, "WZxsec2016")
        except ValueError as e:
            print e
            continue
    else:
        file_path = name
    print "Results for file %s" % name
    print "File path is %s" % file_path
    metaChain.Add(file_path)
    for state in states:
        state = state.strip()
        chain = ROOT.TChain("%s/ntuple" % state)
        chain.Add(file_path)
        ApplySelection.setAliases(chain, state, "Cuts/aliases.json")
        cut_tree = chain
        num_events = cut_tree.GetEntries(args.cut_string)
        print "Number of events in state %s is %i" % (state, num_events)
        if args.printEventNums:
            cut_tree = chain.CopyTree(args.cut_string) if args.cut_string != "" \
                else chain
            file_name = 'WZEvents_{:%Y-%m-%d}_{selection}_{name}_{chan}.out'.format(datetime.date.today(), 
                    selection=args.selection, name=name, chan=(state if args.channels != "" else ""))
            output_file = file_name if args.output_dir == "" else "/".join([args.output_dir, file_name])
            with open(output_file, "wa") as outfile:
                outfile.write("# Made with cut: %s\n" % args.cut_string)
                for row in cut_tree:
                    eventId = '{0}:{1}:{2}'.format(row.run, row.lumi,row.evt)
                    outfile.write(eventId+'\n')
                    if args.printTrigger or args.printDetail:
                        print "-"*20 + eventId + "_"*20
                        if args.printTrigger:
                            print "singleMu: ", row.singleMuPass
                            print "singleIsoMu: ", row.singleIsoMuPass
                            print "singleE: ", row.singleEPass
                            print "doubleE: ", row.doubleEPass
                            print "doubleMu: ", row.doubleMuPass
                        if args.printDetail:
                            if state == "emm":
                                print "ePt :", row.ePt
                                print "m1Pt :", row.m1Pt
                                print "m2Pt :", row.m2Pt
                                print "Zmass :", row.m1_m2_Mass
                    if args.checkDuplicates:
                        if eventId in eventArray:
                            print "Found a duplicate: %s" % eventId
                        else:
                            eventArray.append(eventId)
        totals[state] += num_events
        total += num_events
    print "Number of events in all states is %i" % total
print ""
print "Results for all files:"
total = 0
for state, count in totals.iteritems():
    print "Summed events for all files in %s state is %i" % (state, count)
    total += count
print "Summed events for all files in all states is %i" % total
total_processed = 0
for row in metaChain:
    total_processed += row.nevents
print "A total of %i events were processed from the dataset" % total_processed
