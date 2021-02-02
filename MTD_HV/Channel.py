from softioc import builder, softioc
import ctypes

class Channel():
    def __init__(self, bdlist, channel, lib, handle):
        self.bdlist = bdlist
        self.channel = channel
        self.lib = lib
        self.handle = handle
        # Process Variables
        if self.bdlist == 1 or self.bdlist == 5:
            base_PV = "Negative:{0}:{1}:".format(self.bdlist, self.channel)
        else:
            base_PV = "Positive:{0}:{1}:".format(self.bdlist, self.channel)
        self.readVol = builder.aIn(base_PV+"vmon", LOPR = 0, HOPR = 8000, LOW=6200, LOLO=6000, LLSV="MAJOR", LSV="MINOR", EGU = "V", )
        self.readCur = builder.aIn(base_PV+"imon", LOPR=0, HOPR=100, PREC=2, HIHI=20, HIGH=15, HHSV="MAJOR", HSV="MINOR", EGU = "muA")
        self.readStatus = builder.mbbIn(base_PV+"status", ("Off", 0), ("On", 1), ("Ramping Up", 2), ("Ramping Down", 3), 
                                        ("Over-Current", 4, "MAJOR"), ("Over-Voltage", 5, "MAJOR"), ("Under-Voltage", 6, "MAJOR"),
                                        ("External Trip", 7, "MAJOR"), ("Max V", 8, "MAJOR"), ("Ext. Disable", 9, "MAJOR"),
                                        ("Internal Trip", 10, "MAJOR"), ("Calib. Error", 11, "MINOR"), ("Unplugged", 12, "MINOR"),
                                        ("reserved forced to 0", 13, "MAJOR"), ("OverVoltage Protection", 14, "MAJOR"),
                                        ("PowerFail", 15, "MAJOR"), ("Temperature Error", 16, "MAJOR"))
        #self.setOn = builder.boolOut(base_PV+'setOn', on_update=self.setOn, HIGH=1, always_update=True)
        #self.setOff = builder.boolOut(base_PV+'setOff', on_update=self.setOff, HIGH=1, always_update=True)
        self.setVol = builder.aOut(base_PV+'v0set', LOPR=0, HOPR=8000, EGU="V", initial_value=self.getFloatParameter("V0Set"), on_update=self.setV0Set, always_update=True)
        self.setMaxVol = builder.aOut(base_PV+'setMaxVol', LOPR=0, HOPR=8000, EGU="V", initial_value=self.getFloatParameter("SVMax"), on_update=self.setSVMax, always_update=True)
        self.setRampUp = builder.aOut(base_PV+'setRampUp', LOPR=0, HOPR=50, EGU="V/s", initial_value=self.getFloatParameter("RUp"), on_update=self.setRUp, always_update=True)
        self.setRampDown = builder.aOut(base_PV+'setRampDown', LOPR=0, HOPR=50, EGU="V/s", initial_value=self.getFloatParameter("RDWn"), on_update=self.setRDWn, always_update=True)
        self.setTripI = builder.aOut(base_PV+'setTripI', LOPR=0, HOPR=90, PREC=2, EGU="muA", initial_value=self.getFloatParameter("I0Set"), on_update=self.setI0Set, always_update=True) 
        self.setTripTime = builder.aOut(base_PV+'setTripTime', LOPR=0, HOPR=90, PREC=1, EGU="s", initial_value=self.getFloatParameter("Trip"), on_update=self.setTrip, always_update=True)
        self.pwOnOff = builder.boolOut(base_PV+"pwonoff", on_update=self.slideOnOff, ZNAM="OFF", ONAM="ON", always_update=True)

    def update(self):
        self.readVol.set(self.getFloatParameter("VMon"))
        self.readCur.set(self.getFloatParameter("IMon"))
        self.readStatus.set(self.getStatus())

    def getFloatParameter(self, parName):
        chlist = (ctypes.c_ushort*1)(self.channel)
        FloatValues = (ctypes.c_float*1)(0.0)
        result = self.lib.CAENHV_GetChParam(self.handle.value, self.bdlist, parName, 1, chlist, ctypes.byref(FloatValues))        
        return FloatValues[0]

    def getStatus(self):
        chlist = (ctypes.c_int*1)(self.channel)
        StatusValues = (ctypes.c_uint*1)(0)
        result = self.lib.CAENHV_GetChParam(self.handle.value, self.bdlist, "Status", 1, chlist, ctypes.byref(StatusValues))
        a=0
        for i in range(0,16):
            if(StatusValues[0] >> i & 1): a=i+1
        return a

    def	slideOnOff(self, val):
       	if(val == 0):
            pass
       	    # Turn Off
            self.setOff() # definovat bez premennej val a zrusit process Variable setOff
       	elif(val == 1):
            pass
       	    # Turn on
            self.setOn() # definovat bez premennej val a zrusit process Variable setOn
        else:
            print("Possible values are 0 or 1")
            return

    def setOn(self):
	chlist = (ctypes.c_ushort*1)(self.channel)
	BoolValues = (ctypes.c_bool*1)(1)
	result = self.lib.CAENHV_SetChParam(self.handle.value, self.bdlist, "Pw", 1, chlist, ctypes.byref(BoolValues))
	#print hex(result)

    def setOff(self):
        chlist = (ctypes.c_ushort*1)(self.channel)
        BoolValues = (ctypes.c_bool*1)(0)
        result = self.lib.CAENHV_SetChParam(self.handle.value, self.bdlist, "Pw", 1, chlist, ctypes.byref(BoolValues))

    def setFloatParameter(self, val, parName):
        chlist = (ctypes.c_ushort*1)(self.channel)
        FloatValues = (ctypes.c_float*1)(val)
        result = self.lib.CAENHV_SetChParam(self.handle.value, self.bdlist, parName, 1, chlist, ctypes.byref(FloatValues))
    
    def setV0Set(self, val):
        self.setFloatParameter(val,"V0Set")
    def setI0Set(self, val):
        self.setFloatParameter(val, "I0Set")
    def setSVMax(self, val):
        self.setFloatParameter(val,"SVMax")    
    def setRUp(self, val):
        self.setFloatParameter(val,"RUp")    
    def setRDWn(self, val):
        self.setFloatParameter(val,"RDWn")
    def setTrip(self, val):
        self.setFloatParameter(val,"Trip")
