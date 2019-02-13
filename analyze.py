#!/usr/bin/python
import sys
import re
import os
import argparse
from tabulate import tabulate

parser=argparse.ArgumentParser()
parser.add_argument("-l","--lldp",nargs="?",help="Check LLDP status")
parser.add_argument("-m","--mlag",nargs="?",help="Check MLAG status")
parser.add_argument("-mi","--mlagint",nargs="?",help="Check MLAG Interface status")
args=parser.parse_args()

def read_file(file_name):
 #print(file_name)    
 with open(file_name) as f:
  data=f.readlines()
 return data

#regexp = re.compile('^Port.*Flags$')
#for i in data:
# a=data.index(i)  if regexp.search(i) and a==0 else 0
# print a

#THIS IS NOT USED NOW!#
#def phy_int_list():
# phy_int_list=os.popen('cat 137753-show-tech-AU-SYD-SY3-7280-CORE01-02_01.1343  | egrep Et.*LLDP | cut -d " "  -f2 ').readlines()
#return phy_int_list

def file_finder(file_name):
 if ' ' in file_name:
  file_name="'"+file_name+"'"   
 check='ls | grep -v gz | grep -i '+file_name
 file_list=os.popen(check).readlines()
 if len(file_list) > 1:
  print('\nMore than one match found for filename, please be more specific!\n')
  for i in file_list:
   print i
  sys.exit(-2)
 else:
  file_name=file_list[0].strip('\n')
  if ' ' in file_name:
   file_name="'"+file_name+"'"
  return file_name
def check_mlagint(file_name):
 data=read_file(file_name)
 mi=[]
#print len(data)
 regexp = re.compile('mlag.*state.*oper.*changes')
 for i in data:
  if regexp.search(i):
    index=data.index(i)+2
 for i in range(index,index+200):
  if data[i].isspace():
   break
  else:
   mi.append(data[i].split('       '))
 print('\n')
 print tabulate(mi, headers=['MLAG', 'State','Local','Remote','Oper[Local/Remote]','Config[Local/Remote]','Last Change','Changes'],tablefmt='fancy_grid')
 print('\n')  
def check_mlag(file_name):
 mlag=[]
 lif=''
 change=''
 did=''
 check='cat '+file_name+'  | grep -e \'MLAG Configuration:\' -A 30'
 data=os.popen(check).readlines()
 for i in data:
  if 'domain-id' in i:
   did=i.split(':')[1].strip(' ').strip('\n')
  if 'local-interface' in i:
   lif=i.split(':')[1].strip(' ').strip('\n')
  if 'peer-address' in i:
   pad=i.split(':')[1].strip(' ').strip('\n')
  if 'state   ' in i:
   state=i.split(':')[1].strip(' ').strip('\n')
  if 'State  ' in i and 'Peer' not in i:
   state=state+'-'+i.split(':')[1].strip(' ').strip('\n')
  if 'tate change' in i:
   change=change+' - '+i.split(':')[1].strip(' ').strip('\n')
  if 'Configured  ' in i:
   cpo=i.split(':')[1].strip(' ').strip('\n')
  if 'Inactive   ' in i:
   ipo=i.split(':')[1].strip(' ').strip('\n')
  if 'Active-partial  ' in i:
   appo=i.split(':')[1].strip(' ').strip('\n')
  if 'Active-full  ' in i:
   afpo=i.split(':')[1].strip(' ').strip('\n')

 mlag.append([did,lif,pad,state,change[3:],cpo,ipo,appo,afpo])
 print('\n')
 print tabulate(mlag, headers=['Domain-ID', 'Local Interface','Peer-Address','State','Change(s)','Configured Po','Inactive Po','Active-Partial Po','Active-Full Po'],tablefmt='fancy_grid')
 print('\n')
def check_lldp(file_name):
 lldp=[]
 temp=[]
 sname=''
 pid=''
 pdesc=''
 check='cat '+file_name+'  | egrep Et.*LLDP | egrep -v 0.L | cut -d " "  -f2 '
 lldp_int_list=os.popen(check).readlines()
#####Need to fix this######
 lldp_int_list.append('Management1')
 for i in lldp_int_list:
  check='cat '+file_name+'  | grep -e "'+i.strip('\n')+'\s.*LLDP" -A 20'
  data=os.popen(check).readlines()
  for j in data:
   if 'System Name' in j:
    sname=j.split("\"")[1]
   if 'Port ID    ' in j:
       pid=j.split(":")[1].strip("\"")
   if 'Port Description' in j:
    pdesc=j.split("\"")[1]
   if sname and pid !='':
    lldp.append([sname,i,pid,pdesc])
    sname=''
    pid=''
 print('\n')
 print tabulate(lldp, headers=['Neighbor', 'Local port','Remote Port','Remote Description'],tablefmt='fancy_grid')
 print('\n')

def main():
 #file=file_finder(args.lldp)   
 if args.lldp:
  file=file_finder(args.lldp)   
  check_lldp(file)
 if args.mlag:
  file=file_finder(args.mlag)
  check_mlag(file)
 if args.mlagint:
  file=file_finder(args.mlagint)
  check_mlagint(file)
if __name__=='__main__':
 main()

