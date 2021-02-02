#!/bin/sh
echo 'Restarting the IOC into FULL HV State'
echo 'Currently Running IOCs'
/usr/bin/screen -ls
sleep 5 
IOCVAR=$(/usr/bin/screen -ls|grep HVIOC|head -n1|awk '{print $1}')
if [ $IOCVAR ]
then
 echo 'Terminating HVIOC: '
 echo $IOCVAR
 /usr/bin/screen -d -r $IOCVAR -p 0 -X stuff "exit() $(printf '\r')"
 sleep 5
 echo 'HV IOC has been terminated.'
 echo 'Running IOCs:'
 /usr/bin/screen -ls
fi

echo 'Any remaining semaphores?'
ipcs -cs
A=$(ipcs -cs|grep root|head -n1|awk '{print $1}')
if [ $A ]
then
 echo 'Removing root owned semaphore:'
 echo $A
 sudo ipcrm -s $A
 C=$(ipcs -cs|grep root|head -n1|awk '{print $1}')
 echo $C
 echo "hi there, removed hung root semaphore"
fi
B=$(ipcs -cs|grep mtd|head -n1|awk '{print $1}')
if [ $B ]
then
 echo "You have a mtd semaphore, if hvioc is not running, it is hung.  to remove: ipcrm -s $B"
fi


echo 'Preparing to start the HV IOC'

cp /star/u/mtd/IocTop_MTD/MTD_HV/InitValStandBy.txt /star/u/mtd/IocTop_MTD/MTD_HV/init_val.txt


sleep 5 
echo 'Starting the HV IOC'
#STARTSCREEN="/usr/bin/screen -L -S HVIOC -d -m /home/mtd/MTD/HV/HVCAENx527_3.7.2/iocBoot/iocHVCAENx527/HVIOC.cmd -c mtdhv@130.199.60.172"
#STARTSCREEN="/usr/bin/screen -L -S HVIOC -d -m /home/mtd/MTD/HV/HVCAENx527_3.7.2/iocBoot/iocHVCAENx527/HVIOC.cmd -c mtdhv@130.199.60.254"
#STARTSCREEN="/usr/bin/screen -L -S HVIOC -d -m /home/mtd/IocScripts/HV.sh"
STARTSCREEN="/home/mtd/IocScripts/HV.sh"
$STARTSCREEN
sleep 5 
echo 'Running IOCs'
#/home/mtd/bin/runningIOCs.sh
/usr/bin/screen -ls
