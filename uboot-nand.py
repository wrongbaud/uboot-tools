import serial
import os
import sys
import re
import struct

BAUD = 38400
PAGE_SIZE = 0x200
NAND_SIZE = 8 * (1024*1024)
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
    print ENV

def dump_nand(block):
    bytestr = ''
    resp = send_cmd("nand dump {}".format(block)).split("\n")
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
    with open("test.bin",'wb') as t:
        for x in range(0,NAND_SIZE/PAGE_SIZE+1):
            print("Dumping page {:X} of {:X}".format(x,NAND_SIZE/PAGE_SIZE))
            bytestr = dump_nand(x)
            t.write(bytestr)

if __name__ == "__main__":
    port = sys.argv[1]
    ser = serial.Serial(port,BAUD)
    main(ser)
