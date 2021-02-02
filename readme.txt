# Muon Telescope Detector
Setup:
  in bashrc:
    export PATH=/home/mtd/EPICSfromTOFP/base-3.14.12.2/bin/linux-x86_64:/home/mtd/EPICSfromTOFP/modules/soft/seq-2.1.4/bin/linux-x86_64:/home/mtd/EPICSfromTOFP/modules/soft/autosave-4-8/asApp/src/linux-x86_64:/home/mtd/EPICSfromTOFP/extensions/bin/linux-x86_64/:$PATH
    export LD_LIBRARY_PATH=/home/mtd/MTD/HV/HVCAENx527_4.0.1/lib/linux-x86_64:/home/mtd/MTD/LV/LVWienerPL5xx_2.0.6/LVWienerPL5xxApp/src/lib:$LD_LIBRARY_PATH
    export LD_LIBRARY_PATH=/star/u/mtd/CAENGECO2020-1.7.2/qt/x64:$LD_LIBRARY_PATH
    export LD_LIBRARY_PATH=/home/mtd/EPICS/module/soft/autosave-5-0/lib/linux-x86_64:$LD_LIBRARY_PATH
    export PYEPICS_LIBCA=/home/mtd/EPICSfromTOFP/base-3.14.12.2/lib/linux-x86_64/libca.so
    alias MTDHV_IOC='~/IocScripts/HV.sh'
    alias MTDHV_MEDM='medm -x -displayFont -attach ~/MTD/HV/HV_MEDM/General_newrun18.adl &'
    alias MTDHV_MEDMsc='medm -x -displayFont scalable -attach ~/MTD/HV/HV_MEDM/General_newrun18.adl &'
    alias MTDLV_IOC='~/IocScripts/LV.sh'
    alias MTD_Alarm='~/EPICS/extensions/bin/linux-x86/alh -l /home/mtd/logs -T mtdalarms.alhConfig&

It needs files:
  Scripts/HV.sh in ~/IocScripts/HV.sh
  everything in GUI directory in ~/MTD/HV/HV_MEDM
  MTDHV_IOCRESET_FULL.sh, MTDHV_IOCRESET_OFF.sh, MTDHV_IOCRESET_STANDBY.sh in ~/butter directory   
  everything in MTD_HV directory in the ~/IocTop_MTD directory  

Usage Notes:
  At initialization stage the IOC reads values from the power supplies and sets the main switches (ON-OFF)
  and (Full-Standby) according to the setup in the file init_val.txt
  Changes in the main switches triggers setting of voltages to all channels 
  	  in function Standby(self,val) 
	     obj.setVol.set(#) (first one standby values and second full values)
	     to set values on individual channes use the softioc.dbpf commands (as shown by those commented examples inside the function)    	
		   
