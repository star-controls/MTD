import time
import threading
import numpy as np
import ctypes
from Channel import Channel
from softioc import builder, softioc
builder.SetDeviceName('MTD:HV')

class MTD():
    def __init__(self, ip):
        self.ip = ip
        self.boards = [1,3,5,7]
        self.channels = [0,1,2,3,4,5]
        self.lib = ctypes.cdll.LoadLibrary('/home/mtd/CAENHVWrapper-5.82/lib/x64/libcaenhvwrapper.so.5.82')
        self.handle = ctypes.c_int(0)
        #self.result0 = self.lib.CAENHV_InitSystem(2, 0, self.ip, "admin", "admin", ctypes.byref(self.handle)) # for CAEN SY4527 
        self.result0 = self.lib.CAENHV_InitSystem(0, 0, self.ip, "admin", "admin", ctypes.byref(self.handle)) # for CAEN SY1527
        print "MTD is using {0} boards".format(len(self.boards))
        #### Read INITIAL values for self.on and self.standby ####
        try:
            self.values = {}
            with open("init_val.txt","r") as f:
                for line in f:
                    variable, value = line.split(",")
                    self.values[variable] = value.strip("\n")
        except:
            print "!!! init_val.txt not found, setting default values !!!"
            self.values = {"MTD:HV:SectorSwitch":0, "MTD:HV:Standby":0} # Setting default values
        finally:
            self.init_standby = int(self.values["MTD:HV:Standby"])
            self.init_switch = int(self.values["MTD:HV:SectorSwitch"])
        #### Process Variables creation ####
	self.standby = builder.boolOut("Standby", on_update=self.Standby, always_update=True, ZNAM="FULL", ONAM="StandBy",initial_value=self.init_standby)
	self.full = builder.boolOut("full", on_update=self.full, HIGH=0.1)
	#self.off = builder.boolOut('off', on_update=self.turnOff, HIGH=0.1)
	#self.on = builder.boolOut('on', on_update=self.turnOn, HIGH=0.1)
        self.on = builder.boolOut('SectorSwitch', on_update=self.Switch, always_update=True, ZNAM="OFF", ONAM="ON", initial_value=self.init_switch)
	self.boardlist_temp = [] # Board Temperature list
        self.boardlist_stat = [] # Board Status list
	self.chanlist = []
        for i in range(0, len(self.boards)):
	    if self.boards[i] == 1 or self.boards[i] == 5:
                base_PV_temp = "Negative:{0}:Temp".format(self.boards[i])
                base_PV_stat = "Negative:{0}:status".format(self.boards[i])
            else:
                base_PV_temp = "Positive:{0}:Temp".format(self.boards[i])
                base_PV_stat = "Positive:{0}:status".format(self.boards[i])
            self.boardlist_temp.append(builder.aIn(base_PV_temp))
            self.boardlist_stat.append(builder.mbbIn(base_PV_stat,("All good",0), ("Power-failure",1),
                                                                  ("Firmware error",2), ("HV calib error",3),
                                                                  ("Temtp calib error",4), ("Under temp",5),
                                                                  ("Over temp",6)))
            for j in range(0, len(self.channels)):
                self.chanlist.append( Channel(self.boards[i], self.channels[j], self.lib, self.handle))
    #-----------------------------------------------------------------------------------------------------------------------------------------------            
    def temperature(self):
        self.bdlist = (ctypes.c_ushort*len(self.boards))(*self.boards)
        zero_array = np.zeros(len(self.boards))
        self.temp = (ctypes.c_float*len(self.boards))(0.0,0.0,0.0,0.0)
        self.result1 = self.lib.CAENHV_GetBdParam(self.handle, len(self.boards), self.bdlist, "Temp", ctypes.byref(self.temp))
        return self.temp
    #----------------------------------------------------------------------------------------------------------------------------------------------- 
    def bdstatus(self):
        self.bdlist = (ctypes.c_ushort*len(self.boards))(*self.boards)
        zero_array = np.zeros(len(self.boards))
        self.status = (ctypes.c_ushort*len(self.boards))(99,99,99,99)
        self.result1 = self.lib.CAENHV_GetBdParam(self.handle, len(self.boards), self.bdlist, "BdStatus", ctypes.byref(self.status))
        return self.status    
    #----------------------------------------------------------------------------------------------------------------------------------------------- 
    def do_runreading(self):
        while True:
            time.sleep(0.5)
            # Boards temperaturex
            for i in range(0, len(self.boards)):
                self.boardlist_temp[i].set(self.temperature()[i])
                self.boardlist_stat[i].set(self.bdstatus()[i])
            # Channels loop
            for ch in self.chanlist:
                ch.update()
    #----------------------------------------------------------------------------------------------------------------------------------------------- 
    def do_startthread(self):
        self.Standby(self.init_standby)
        self.Switch(self.init_switch)
        t = threading.Thread(target=self.do_runreading)
        t.daemon = True
        t.start()
    #----------------------------------------------------------------------------------------------------------------------------------------------- 
    def Standby(self,val):
        self.values["MTD:HV:Standby"] = val
        with open("init_val.txt","w") as f:
            for variable, value in self.values.items():
                f.write("{0},{1}\n".format(variable, value))
        print val        
        if val == 1:
            for obj in self.chanlist:
                obj.setVol.set(4400)
            #softioc.dbpf("MTD:HV:Negative:1:4:v0set", "4399")
            #softioc.dbpf("MTD:HV:Positive:3:4:v0set", "4399")    
        elif val == 0:        
            for obj in self.chanlist:
                obj.setVol.set(6300)
            #softioc.dbpf("MTD:HV:Negative:1:4:v0set", "6299")
            #softioc.dbpf("MTD:HV:Positive:3:4:v0set", "6299")
        else:
            print "Possible values are 0 or 1"
            return            
    #----------------------------------------------------------------------------------------------------------------------------------------------- 
    def full(self, val):
	if(val==0): return
	for obj in self.chanlist:
	    obj.setVol.set(6300)
    #----------------------------------------------------------------------------------------------------------------------------------------------- 
    def turnOff(self, val):
	if(val==0): return
	for obj in self.chanlist:
	    obj.setOff.set(1)
    #----------------------------------------------------------------------------------------------------------------------------------------------- 
    def turnOn(self, val):
	if(val==0): return
	for obj in self.chanlist:
	    obj.setOn.set(1)
    #----------------------------------------------------------------------------------------------------------------------------------------------- 
    def Switch(self, val):
        self.values["MTD:HV:SectorSwitch"] = val
       	with open("init_val.txt","w") as f:
            for	variable, value	in self.values.items():	
                f.write("{0},{1}\n".format(variable, value))
        if val == 1:
            for obj in self.chanlist:
                #obj.setOn.set(1)
                obj.pwOnOff.set(1)
        elif val == 0:    
            for obj in self.chanlist:
                #obj.setOff.set(1)
                obj.pwOnOff.set(0)
        else:
            print "Possible values are 0 or 1"
            return
