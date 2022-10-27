import sys
import argparse
import copy

def fail_help_exit (msg_pass):
    print
    parser.print_help()
    print
    print msg_pass
    sys.exit()
   
def log_add (logText, *args):
    log = ""
    if "dictdump" in args:
        log = "DICTIONARY DUMP:\n" + segment_dict + "\n\n"
    logfile = LOG_LOC + "StructureLog.log"
    with open(logfile, "w+") as log_file:
        pass
    
    if "help" in args:
        fail_help_exit(logText)

def trigger_final():
    #Segment.trigger = segment_dict["trigger"]
    newTrig=Master(seg.trigger, Segment.order, seg.dicts)
    segment_dict = {"trigger" : "", "order" : []}
    
def finalize(master_dict):
    out_file = DEFAULT_FILE_LOC + "output.txt"
    if master_dict:
        with open(out_file, "w+") as final_file:
            final_file.write(str(segment_dict))

def main():

    parser = argparse.ArgumentParser(description='eGate Structure Processor')
    parser.add_argument("file", help="File Name to be processed")
    parser.parse_args()
    args = parser.parse_args()
    file_w_path=DEFAULT_FILE_LOC + args.file

    msg_cnt = 0    
       
    try: 
        f = open(file_w_path)
    except IOError as e:
        fail_help_exit("I/O error ({0}): {1}".format(e.errno, e.strerror) + " - " + file_w_path)

    with f:
        for line in f.readlines():
            Segment.msg_cnt += 1
            for i in line.split():
                seg = Segment(i)
                segment = seg.get_segment()
                trigger = seg.get_trigger()
                #print "Segment: " + str(segment) + " " + "Trigger: " + str(trigger)
                
                if trigger == "CONT": continue 

                if segment in Segment.dicts:
                    seg_data = Segment.dicts[segment]
                    seg_rep = seg_data["repeating"]
                    seg_rqd = seg_data["required"]
                    seg_cnt = seg_data["count"]
                else:
                    seg_rep, seg_rqd, seg_cnt = 0,0,1
                    seg.segment_update(segment, seg_rep, seg_rqd, seg_cnt)
                #print "BEFORE -- Segment.dicts[" + segment + "]: " + str(Segment.dicts[segment])# + ", print order: " + str(Segment.order)
        
                if Segment.previous != segment: 
                    #print "Previous Segment not equal: " + segment + Segment.previous + str(prec1)
                    seg_cnt += 1 

                    if Segment.previous not in Segment.order and segment not in Segment.order: 
                        #print "if " + Segment.previous + " not in " + str(Segment.order) + " and " + segment + " not in Segment.order"
                        Segment.order.append(segment)
                    elif Segment.previous in Segment.order and segment in Segment.order:
                        #print "elif -1- " + Segment.previous + " in str(Segment.order) and " + segment + " in Segment.Order"
                        
                        if segment in seg.arb_dict:
                            Segment.arb_dict[segment] += 1
                            seg_arb = Segment.arb_dict[segment]
                        else:
                            Segment.arb_dict[segment], seg_arb = 1,1
                        
                        seg_combine = segment + str(seg_arb)
                        if seg_combine not in Segment.order: 
                            Segment.order.append(seg_combine)
                    elif Segment.previous in Segment.order and segment not in Segment.order:
                        #print "elif -2- " + Segment.previous + " in Segment.order and " + segment + " not in Segment.order"
                        Segment.order.append(segment)
                    else:
                        pass
                        #print "ELSE -----"
                else:
                    #print "Else " + Segment.previous + " is equal to " + segment
                    seg_rep += 1
                    #continue
                    
                seg_rqd = 1 if seg_cnt == msg_cnt else 0
                Segment.previous = segment
                #print "Segment.previous = " + Segment.previous
                seg.segment_update(segment, seg_rep, seg_rqd, seg_cnt)
                print "AFTER -- Segment.dicts[" + segment + "]: " + str(Segment.dicts[segment])
                #print
                
            seg.add_to_master()
            
            
def format_info():
    print "eGate structure Check:"

    for trigger, data in Master.trigger_dicts.iteritems():
        print "Trigger: " + str(trigger)
        order = Master.trigger_dicts[trigger]["order"]
        print "Order: " + "[%s] " % ", ".join(map(str, order))
        for segment in order:
            segment = segment[:3] if len(segment) > 3 else segment
            count = Master.trigger_dicts[trigger][segment]["count"]
            rqd = Master.trigger_dicts[trigger][segment]["required"]
            rqd = "YES" if rqd == 1 else "NO"
            rep = Master.trigger_dicts[trigger][segment]["repeating"]
            rep = "YES" if rep > 1 else "NO"
        
            print segment + " -- Total Count: " + str(count).ljust(3) + \
                                   "Required?: " + rqd.ljust(4) + \
                                   "Repeated: " + str(rep).ljust(4)

class Segment(object): 
    order = []
    trigger = ""
    dicts = {}
    arb_dict = {}
    proc_trigger = ""
    previous = ""
    msg_cnt = 0
    
    def __init__(self, segment):
        self.seg = segment
    
    def get_segment(self):
        return self.seg

    def get_trigger(self):
        if "^" in self.seg:
            proc_trigger = self.seg.split("^", 2)[1]
            print "Splitting " + str(self.seg) + " into " + proc_trigger + " Segment.trigger is " + Segment.trigger + "."
            Segment.trigger = proc_trigger
            if proc_trigger in Master.trigger_list:
                #print "Trigger " + proc_trigger + " was already in the trigger list. Possibly out of order\n"
                log_text = "Trigger " + proc_trigger + " was already in the trigger list. Possibly out of order\n"
                log_add(log_text)
                
            print "CONTINUE"                     
            return "CONT"
            
        else:
            #print "No ^, returning segment.trigger: " + Segment.trigger
            return Segment.trigger
        

    def add_to_master(self):
        #self.clean_order()
        print "Master reset. Trigger: " + Segment.trigger
        master=Master()
        master.trigger_add(Segment.trigger)
        Segment.order = [ ]
        Segment.dicts = {}
        Segment.arb_dict = {}
        Segment.msg_count = 0
        
    def segment_update(self, segment, rep, rqd, cnt):
        Segment.dicts[segment] = {"repeating" : rep, "required" : rqd, "count" : cnt } 
        #print "Segment Update: " + segment, rep, rqd, cnt
    
class Master(object): # do I even need this? Or just keep trigger_dicts and trigger_list? 
    trigger_list = [ ]
    trigger_dicts = { }
    
    #def __init__(self, trigger, order):
    #    self.trigger = trigger
    #    self.order = []
        
    def trigger_add(self, trigger):
        Master.trigger_list.append( trigger )
        #print Segment.order
        #print Segment.dicts
        Master.trigger_dicts[trigger] = { "order" : Segment.order }
        Master.trigger_dicts[trigger] = { "count" : Segment.msg_count }
        for segment in Segment.order:
            #print Master.trigger_dicts[trigger]
            Master.trigger_dicts[trigger][segment]=Segment.dicts[segment[0:3]]
        

#MAIN Main main

"""
Segment Class: 
    order = []        - Trigger Order
    trigger = ""      - Current Trigger
    dicts = {}        - Current trigger dictonary 
    arb_dict = {}     - Arbitrary dictionary (Additional segments that exist)
    proc_trigger = "" - Processing Trigger
"""

DEFAULT_FILE_LOC = "/home/russjmc/Playground/Python/"
LOG_LOC = DEFAULT_FILE_LOC
prev_seg = ""
seg_arb = 1
cur_trigger = ""

"""
master_dict[trigger] = {"order" : [ ], 
                        "<name>" : {"required" = 0,
                                    "repeating" = 0
                                   }
                        }
"""

final_finish=1
seg_comb = ""
order = []

main()
format_info()


#print "" 
#print Master.trigger_list
#print Segment.order
#print ""
#print Segment.dicts
#print "" 
#print Master.trigger_dicts
