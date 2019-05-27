#!/usr/bin/env python
#AUTHOR=Jithesh PK
#CONTACT=jithesh.pk@thomsonreuters.com
#Version=1.0
import os
import sys
import optparse
#from optparse import OptionParser
import json
import requests
s=''
if len(sys.argv) < 2:
        #os.system('clear')
        os.system("/tools/infra/share/jithesh/cma_beta.py -h")
        sys.exit(-1)
class color:
   FAILRED  = '\033[91m'
   UNDERLINE = '\033[4m'
   OKGREN = '\033[92m'
   END  = '\033[0m'
syntax="""
To find correct DNS/SMTP/NTP/PROXY etc using CMA API:
Example:
1. General syntax.
   /tools/infra/bin/dconetconf.py -s <server_name> -o <option>
2. To find a hosts DNS server name or name server.
   /tools/infra/bin/dconetconf.py -s c111tqc-vm26 -o dns
3. To find http/ftp proxy server name.
   /tools/infra/bin/dconetconf.py -s c111tqc-vm26 -o proxy
4. To show NFS share path for /tools/deploy and deploy_media 
   /tools/infra/bin/dconetconf.py -s c111tqc-vm26 -o storage
5. List all subscribed platform service assosiations   
   /tools/infra/bin/dconetconf.py -s c111tqc-vm26 -o service    
USAGE:
-s 'Server name'
-o 'options'
"""
parser = optparse.OptionParser(usage=syntax)
parser.add_option('-s', '--server', help=' -s server_name - mandatory', dest='server', action='store')
parser.add_option('-o', '--option', help=' -o all,dns,ntp,proxy,service,smtp', dest='opt', action='store', default='all')
(options, args) = parser.parse_args()
server=options.server
opt=options.opt
url = 'http://automation-eag-mgmt.int.thomsonreuters.com/api/hiera/v1/hostname/'+server
reply = requests.get(url)
dicout = reply.json()
if opt == 'dns':
   print color.OKGREN+ "\nUpdate \'/etc/resolv.conf\' with  below DNS Server entries \n"+color.END
   dnso = dicout["dns_servers"]
   for item in dnso: print "nameserver ",unicode(item)
   print "\n"

elif opt == 'ntp':
   print color.OKGREN+ "\nUpdate \'/etc/ntp.conf\' with follwoing NTP Servers \n"+color.END
   ntpo = dicout["ntp_servers"]
   for item in ntpo: print unicode(item)
   print "\n"

elif opt == 'sensu':
   print color.OKGREN+"Sensu ingestion node is:"+color.END
   sensuo = dicout["compassmon_sensu_ingestion_node"]
   print sensuo
   
elif opt == 'avamar':
   print color.OKGREN+"Avamar Backup Grid server is:"+color.END
   avamaro = dicout["eng_avamar_grid"]
   print avamaro
   print "\n"
   
elif opt == 'splunk':
   print color.OKGREN+"Splunk server is:"+color.END
   splunko = dicout["splunk_server"]
   print splunko
   
elif opt == 'proxy':
   print color.OKGREN+"\nHTTP proxy server is:"+color.END
   proxyh = dicout["webproxy"]
   print proxyh
   print color.OKGREN+"\nFTP proxy server is:"+color.END
   proxyf = dicout["ftp_proxy"]
   print proxyf
   print "\n"
   
elif opt == 'dsm':
   print color.OKGREN+"\nDSM server is:"+color.END
   dsmo = dicout["dsm_server"]
   print dsmo
   print "\n"
   
elif opt == 'smtp':
   print color.OKGREN+"\nUpdate \'/etc/postfix/main.cf\' with following entry \n"+color.END
   smtpo = dicout["smtp_relay"]
   print "relayhost = ",smtpo
   print "\n"
   
elif opt == 'ldap':
   print color.OKGREN+"\nLDAP Sever VIP  is:"+color.END
   ldapo = dicout["ldap_vip"]
   print ldapo
   print "\n"

elif opt == 'service':
   ASSO = "/ci/" + server + "/association"
   cmaurl = "http://platform-api.int.thomsonreuters.com/api/cma/1.3"+ ASSO
   replycma = requests.get(cmaurl)
   dicoutcma = replycma.json()
   TRS  = dicoutcma["result"]
   print '\n',color.OKGREN+"Service Association of "+ server +" :-"+color.END
   for i in TRS:
           serv = i["Service"]
           ver = i["TRVersion"]
           print '\t',(serv), ( ver)
   #print color.OKGREN+"\nSubscribed Service Associations are:\n"+color.END
   #cmao = dicoutcma["cma"]
   #print cmao
   #for item in cmao: print unicode(item)
   
   print "\n"

elif opt == 'storage':
   print color.OKGREN+"\n Add following lines in \'/etc/auto.tools\':\n"+color.END
   vfiler = dicout["infra_storage_device"]
   deploy = dicout["infra_storage_shared_nfs_volume"]
   media  = dicout["infra_storage_media_nfs_volume"]
   nfs_media = str(vfiler+':'+media)
   nfs_deploy = str(vfiler+':'+deploy)
   print "deploy_media    -ro,noacl  ",nfs_media
   print "deploy          -ro,noacl  ",nfs_deploy

else:
   #/tools/infra/share/jithesh/cma_beta.py -h
   print color.FAILRED+ "Please enter a valid option from follwoing list" +color.END 
   print "\n \t -o dns \n \t -o smtp \n \t -o ntp \n \t -o proxy \n \t -o storage \n \t -o service \n \t -o sensu \n \t -o avamar \n \t -o dsm \n \t -o ldap \n \t -o splunk \n"

