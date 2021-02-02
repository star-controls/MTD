#!/star/u/mtd/EPICSfromTOFP/modules/pythonIoc/pythonIoc

#import basic softioc framework
from softioc import softioc, builder

#import the the application
from MTD import MTD

#mtd = MTD('130.199.60.172')
mtd = MTD('130.199.60.254')

#run the ioc
builder.LoadDatabase()
softioc.iocInit()

mtd.do_startthread()

#start the ioc shell
softioc.interactive_ioc(globals())
