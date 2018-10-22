import sys
import argparse
import copy

def fail_help_exit (msg_pass):
    print
    parser.print_help()
    print
    print msg_pass
    sys.exit()

def segment_dict_setup (segment, trigger):
    global seg_arb
    if segment in segment_dict:
        if prev_seg != segment:
            segment = segment + str(seg_arb)
            seg_arb += 1
    else:
        segment_dict[segment] = {"repeating" : 0, "required" : 0, "preceding" : [], "count" : 0}
        segment_dict["trigger"] = trigger
    #else:
    #    log_add("Segment failure. Dumping dictionary to error file", "dictdump")
    
def trigger_dict_setup (segment, trigger, segment_dict):
    segment_dict["trigger"] = trigger
           
def order_add (segment, segment_dict):
        order = str(segment_dict["order"])
        segment_dict["order"] = order + "," + segment if order != "" else segment
    
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
    master_dict[trigger] = {}
    #print segment_dict
    print master_dict
    #master_dict[trigger] = copy.deepcopy(segment_dict)
    #master_dict[trigger]["order"] = copy.deepcopy(segment_dict["order"])
    for dict_seg in segment_dict: 
        print dict_seg
        master_dict[trigger][dict_seg] = copy.deepcopy(segment_dict[dict_seg])
        print master_dict[trigger][dict_seg]
        print master_dict
    segment_dict = {"trigger" : "", "order" : []}
    return master_dict
    
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
segment_dict = { "trigger" : "", "order" : []}
master_dict = { }
file_w_path=DEFAULT_FILE_LOC + args.file
final_finish=0

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
                    trigger_dict_setup(segment, trigger, segment_dict)
                    final_finish=0
                    prev_seg = ""
                    continue
                elif trigger != segment_dict["trigger"]:
                    master_dict = trigger_final(segment_dict, master_dict)
                    final_finish=1
            else:
                trigger = segment_dict["trigger"]
        
            if segment in segment_dict:
                seg_rep = segment_dict[segment]["repeating"]
                seg_rqd = segment_dict[segment]["required"]
                seg_cnt = segment_dict[segment]["count"]
            else:
                segment_dict_setup(segment, trigger)
                seg_rep, seg_rqd, seg_cnt = 0,0,0
        
            seg_rep += 1
        
            if prev_seg != segment: 
                seg_cnt += 1
                if segment not in segment_dict[segment]["preceding"]: 
                    segment_dict["order"].append(segment)
                    segment_dict[segment]["preceding"].append(prev_seg)
                else:
                    seg_arb += 1
                    segment_dict["order"].append(segment + str(seg_arb))
                    segment_dict[segment]["preceding"].append(prev_seg)
                
            segment_dict[segment]["required"] = 1 if seg_cnt == msg_cnt else 0
            segment_dict[segment]["repeating"] = seg_rep
            segment_dict[segment]["count"] = msg_cnt
            prev_seg = segment
        

# print segment_dict["order"]        
if final_finish == 0:
    trigger_final(segment_dict, master_dict)
    finalize(master_dict)


print "eGate structure Check:"

for trigger in master_dict.iteritems():
    #trigger = master_dict[trigger]["trigger"]
    print "Trigger: " + str(trigger)
    print master_dict[trigger]["order"]
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

        
#    Check the message type
#    If it is a new message type, write any outputs to a file and clear variables (Possibly set order, etc stuff)
#    Split the segment into SEGMENT and NUMBER
#    Add the segment to a simple count dictionary for REQUIRED.
#    if the simple count != messageCounter
#      set required to 1
#    if NUMBER > 1
#      set repeating to 1
#    if the segment is already in the dictionary, pull values to compare to see if they are already repeating/required and reset if necessary
#    Add to a count to a dictionary that has SEGMENT as the key, REQUIRED, REPEATING, and segments that segment follows (Ex 1)
