#!/bin/bash
##This script will perform basic Linux OS perfomance checkouts##
##nidhi.kn@thomsonreuters.com

echo -e "\e[100m--------------------------------------------------------------------- BASIC CHECKS --------------------------------------------------------------------\e[0m"

echo " "
echo " "
echo -e "\e[33mServer Make & Model\e[0m"
#echo "Server Make & Model"
MAKE=$(dmidecode -t1 |grep Manufacturer|awk -F: '{print $2}')
MODEL=$(dmidecode -t1 |grep Product|awk -F: '{print $2}')
echo $MAKE $MODEL

echo " "
#-------------------------------------------------------------------
echo -e "\e[33mOS Release\e[0m"
cat /etc/SuSE-release 2>/dev/null||cat /etc/oracle-release 2>/dev/null||cat /etc/redhat-release 2>/dev/null

echo " "

echo -e "\e[33mKernel version\e[0m"
#o "kernel version"
uname -r
echo " "
#-----------------------------
echo -e "\e[33mUPTIME\e[0m"

#----------------------------------------------
uptime -s
uptime -p
echo " "
#-------------------------------------------
echo -e "\e[33mLoad average\e[0m"
uptime | awk '{print $10,$11,$12}'
echo " "
#---------------------------------------------------
echo -e "\e[33mHigh CPU used process\e[0m"
echo " %CPU  PID PROCESS         USER"
ps -eo pcpu,pid,comm,user |sort -k1nr| head -5
echo " "
#-------------------------------------------------
echo -e "\e[33mTotal Memory and Free Memory in MB \e[0m"
free -m | egrep "Mem|total|free"
echo " "
#-------------------------------------------------------------------------------------------------
echo  -e "\e[33mHigh Memory used process \e[0m"
echo "%MEMORY PID PROCESS        USER"
ps -eo pmem,pid,comm,user | sort -k1nr|head -5
echo " "
#------------------------------------------------------------------------------------------------------------------
echo -e "\e[33mTotal Swap Utilization in MB \e[0m"
free -m | egrep "Swap|total|free"
echo " "
#------------------------------------------------------------------------------------------------------------------
echo -e "\e[33mThe logical CPU number of a CPU as used by the Linux kernel.\e[0m"
#lscpu | egrep 'CPU|Thread'
lscpu |egrep "^CPU|^Thread" |grep -v "CPU "
echo " "
#---------------------------------------------------------------------------------------------------------------------
echo -e "\e[33mChecking for NFS stale mounts \e[0m"

for fs in `mount | grep 'type nfs' | awk '{print $3}'`; do timeout 6 ls -ald $fs/. >/dev/null 2>/dev/null && echo -e "\e[32mNo stale in $fs.\e[0m" || echo -e "\e[31m $fs not responding. \e[0m"; done
mount |grep ' nfs' >/dev/null 2>/dev/null 
if [ $? -ne 0 ];then
  echo -e "\e[32mNo nfs mounted on the server\e[0m"
fi

echo " "
#-----------------------------------------------------------------------------------------------------------------------------------------------------

echo  -e "\e[33mChecking file System usage \e[0m"
df -hP | grep 100%
if [ $? == 0 ];then
  echo -e "\e[31mAbove file system is consuming 100% \e[0m "
else
  echo -e "\e[32mNone of the file system is 100% \e[0m"
fi
df -hi | grep 100%
if [ $? == 0 ];then
  echo -e "\e[31mAbove filesystem space is consuming 100%\e[0m"
else
  echo -e "\e[32mNone of the file system inode usage is 100%\e[0m"
fi
echo " "


#----------------------------------------------------------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------------------------------------------------------------------------

echo -e "\e[33mChecking for Read-only filesystem \e[0m"

grep ro, /proc/mounts |egrep "ext2|ext3|ext4|xfs| nfs " && echo -e "\e[31mThe above Filesystems is/are read-only\e[0m " ||  echo -e "\e[32mNo read-only filesystem\e[0m"

echo " "
#----------------------------------------------------------------------------------------------------------------------------
