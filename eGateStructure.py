import sys
import argparse
import copy

def fail_help_exit (msg_pass):
    print
    parser.print_help()
    print
    print msg_pass
    sys.exit()

def segment_dict_setup (segment, trigger, seg_arb):
    if segment in segment_dict:
        if prev_seg != segment:
            segment = segment + str(seg_arb)
            seg_arb += 1
    else:
        segment_dict[segment] = {"repeating" : 0, "required" : 0, "preceding" : [], "count" : 0}
        segment_dict["trigger"] = trigger
    #else:
    #    log_add("Segment failure. Dumping dictionary to error file", "dictdump")
    
def segment_dict_reset():
    #global segment_dict arbitrary_dict
    segment_dict = {"trigger" : trigger, "order" : []}
    arbitrary_dict = {}
    print "*************** SEG RESET ****************"
    
def log_add (logText, *args):
    log = ""
    if "dictdump" in args:
        log = "DICTIONARY DUMP:\n" + segment_dict + "\n\n"
    logfile = LOG_LOC + "StructureLog.log"
    with open(logfile, "w+") as log_file:
        pass
    
    if "help" in args:
        fail_help_exit(logText)
        
def trigger_final(segment_dict, master_dict):
    trigger = segment_dict["trigger"]
    master_dict[trigger] = copy.deepcopy(segment_dict)
    segment_dict = {"trigger" : "", "order" : []}
    
def finalize(master_dict):
    out_file = DEFAULT_FILE_LOC + "output.txt"
    if master_dict:
        with open(out_file, "w+") as final_file:
            final_file.write(str(segment_dict))
            


#MAIN Main main
"""
Processing Dictionary Setup: 
segments = {"order" : [] #General order of segments
                     "trigger" : <trigger> #current trigger being worked on.
                     "count' : 0 # master count for required.
                     "<Seg name>" : {"repeating": <number> # 1 = yes >1 = no
                                                 "required" : <bitvalue>, # 0=no, 1=yes
                                                 "preceding" : [<list of segments preceding>]
                                               }
                   }
Master Dictionary:
master_dict = {"trigger" : {"order" = <order>,
                                          <segment> : <seg defs>
                                         }
                        }
                       
"""
parser = argparse.ArgumentParser(description='eGate Structure Processor')
parser.add_argument("file", help="File Name to be processed")
parser.parse_args()
args = parser.parse_args()

DEFAULT_FILE_LOC = "/home/russjmc/Playground/Python/"
LOG_LOC = DEFAULT_FILE_LOC
msg_cnt = 0
prev_seg = ""
seg_arb = 1
cur_trigger = ""
arbitrary_dict = { }
segment_dict = { "trigger" : "", "order" : []}
master_dict = { }
file_w_path=DEFAULT_FILE_LOC + args.file
final_finish=0
seg_comb = ""
order = []

try: 
    f = open(file_w_path)
except IOError as e:
    fail_help_exit("I/O error ({0}): {1}".format(e.errno, e.strerror) + " - " + file_w_path)

with f:
    for line in f.readlines():
        msg_cnt += 1
        for segment in line.split():
            if '^' in segment:
                trigger = segment.split("^", 2)[1]
                if trigger not in segment_dict:
                    arbitrary_dict = {}
                    segment_dict = {"trigger" : "", "order" : [] }
                    final_finish=0
                    prev_seg = ""
                    print "************* RESET ***********"
                    continue
                elif trigger != segment_dict["trigger"]:
                    master_dict = trigger_final(segment_dict, master_dict)
                    final_finish=1
            else:
                trigger = segment_dict["trigger"]
                
            if segment in segment_dict:
                seg_data = segment_dict[segment]
                seg_rep = seg_data["repeating"]
                seg_rqd = seg_data["required"]
                seg_cnt = seg_data["count"]
                seg_prec = seg_data["preceding"]
            else:
                segment_dict_setup(segment, trigger, 0)
                seg_rep, seg_rqd, seg_cnt, seg_arb, seg_prec = 0,0,0,0,[]
                seg_data = {"repeating" : 0, "required" : 0, "count" : 0, "preceding" : [] }
            order = segment_dict["order"]
            seg_rep += 1
        
            if prev_seg != segment: 
                seg_cnt += 1
                prec1 = seg_data["preceding"]
                if prev_seg not in seg_prec and segment not in order: 
                    prec2 = "N N"
                    order.append(segment)
                    seg_prec.append(prev_seg)
                elif prev_seg in seg_prec and segment in order:
                    prec2 = "Y Y"
                    """ Rethink the following logic. 
                    If it is the first of a new line, and it is in the order, skip. how about if the arb is in the order, skip? Define arbitrary number,
                    then check? So the segment is already in both, so check again to see if the segment ARB is in both if the arb is < 1. 
                    """
                    if segment in arbitrary_dict:
                        arbitrary_dict[segment] += 1
                        seg_arb = arbitrary_dict[segment]
                    else:
                        arbitrary_dict[segment], seg_arb = 1,1
                        
                    seg_comb = segment + str(seg_arb)
                    if seg_comb not in order: 
                        order.append(segment + str(seg_arb))
                        seg_prec.append(prev_seg)
                elif prev_seg in seg_prec and segment not in order:
                    prec2 = "Y N"
                    order.append(segment)
                else:
                    prec2 = "N Y"
                    seg_prec.append(prev_seg)
            else:
                continue
                    
            print segment, prec1, seg_prec, prec2, seg_comb
            seg_data["required"] = 1 if seg_cnt == msg_cnt else 0
            seg_data["repeating"] = seg_rep
            seg_data["count"] = msg_cnt
            seg_data["preceding"] = seg_prec
            prev_seg = segment
            segment_dict[segment] = seg_data

if final_finish == 0:
    trigger_final(segment_dict, master_dict)
    finalize(master_dict)

print order
print "eGate structure Check:"
"""
for trigger, data in master_dict.iteritems():
    print "Trigger: " + str(trigger)
    order = master_dict[trigger]["order"]
    print "Order: " + "[%s] " % ", ".join(map(str, order))
    for segment in order:
        segment = segment[:3] if len(segment) > 3 else segment
        count = master_dict[trigger][segment]["count"]
        rqd = master_dict[trigger][segment]["required"]
        rqd = "YES" if rqd == 1 else "NO"
        rep = master_dict[trigger][segment]["repeating"]
        #rep = "YES" if rep > 1 else "NO"
        prec = master_dict[trigger][segment]["preceding"]
        
        print segment + " -- Total Count: " + str(count).ljust(3) + \
                                   "Required?: " + rqd.ljust(4) + \
                                   "Repeated: " + str(rep).ljust(4) + \
                                   "Preceded by: " + '[%s]' % ', '.join(map(str, prec))
"""