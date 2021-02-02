#!/usr/bin/bash
RETVAL=0

prog="HVIOC"

cd /star/u/mtd/IocTop_MTD/MTD_HV

screen -S $prog -d -m ./main.py
