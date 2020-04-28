import serial
import os
import sys
import re
import struct

BAUD = 38400
PAGE_SIZE = 0x200
NAND_SIZE = 64 * (1024*1024)
DRAM = 128 * (1024*1024)
ENV = {}
ser = None
def send_cmd(cmd):
    ser.write(cmd+"\n")
    resp = ser.read_until("=>")
    return resp

def get_env():
    resp = send_cmd("printenv")
    lines = resp.split("\n")
    for line in lines:
        if "=" in line:
            env_var = line.split("=")
            ENV[env_var[0]] = env_var[1]

def dump_mem(addr):
    memstr = ''
    resp = send_cmd("md.l 0x{:X} 0x200".format(addr)).split("\n")
    for line in resp:
        md_vals = re.split('(([0-9a-f]{8}\s){4})',line)
        if len(md_vals) > 2:
            mem_vals = md_vals[1]
            mem_vals = mem_vals.replace(" ",'')
            memstr += mem_vals.decode("hex")
    return memstr

def dump_nand(block):
    bytestr = ''
    resp = send_cmd("nand dump {:X}".format(block)).split("\n")
    for line in resp:
        if re.search('(([0-9a-f]{2}\s){8})\s',line):
            line = line.strip("\t")
            line = line.strip("\n")
            line = line.strip("\r")
            line = line.replace(" ",'')
            bytestr += line.decode("hex")
    return bytestr    

def main(ser):
    get_env()
    #print(dump_mem(0x10F40))
    with open("memdump.bin",'wb') as md:
        for x in range(0,DRAM/(4*0x200)):
            print("Dumping page {:X} of {:X}".format(x,DRAM/(4*0x200)))
            md.write(dump_mem(x*(4*0x200)))
    '''
    with open("NAND-TEST.bin",'wb') as t:
        for x in range(0,(NAND_SIZE/PAGE_SIZE)+1):
            print("Dumping page {:X} of {:X}".format(x,NAND_SIZE/PAGE_SIZE))
            print("Dumping page {:X}".format(x*0x200,NAND_SIZE/PAGE_SIZE))
            bytestr = dump_nand(x*0x200)
            t.write(bytestr)
    '''

if __name__ == "__main__":
    port = sys.argv[1]
    ser = serial.Serial(port,BAUD)
    main(ser)
