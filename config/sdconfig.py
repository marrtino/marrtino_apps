import time
import os
import argparse
import sys
sys.path.append('../bringup')

devicename = '/dev/mmcblk0'
devicenamep1 = '/dev/mmcblk0p1'
devicenamep2 = '/dev/mmcblk0p2'
devicenamep3 = '/dev/mmcblk0p3'

from tmuxsend import TmuxSend

#        Device Boot      Start         End      Blocks   Id  System
#/dev/mmcblk0p1   *        2048      133119       65536    c  W95 FAT32 (LBA)
#/dev/mmcblk0p2          133120    20613119    10240000   83  Linux
#/dev/mmcblk0p3        20613120    63272959    21329920   83  Linux


#Device         Boot    Start      End  Sectors  Size Id Type
#/dev/mmcblk0p1 *        2048   133119   131072   64M  e W95 FAT16 (LBA)
#/dev/mmcblk0p2        133120 20613119 20480000  9,8G 83 Linux
#/dev/mmcblk0p3      20613120 61030399 40417280 19,3G 83 Linux


def umount(tmux):
    if tmux is None:
        os.system('umount %s' %devicenamep1)
        os.system('umount %s' %devicenamep2)
        os.system('umount %s' %devicenamep3)
    else:
        #tmux.cmd(1,'df -h')
        tmux.cmd(1,'umount %s' %devicenamep1, blocking=True)
        tmux.cmd(1,'umount %s' %devicenamep2, blocking=True)
        tmux.cmd(1,'umount %s' %devicenamep3, blocking=True)
        #tmux.cmd(1,'df -h')
    time.sleep(3)


def mount(tmux):
    if tmux is None:
        os.system('mkdir -p /media/$SUDO_USER/PI_ROOT')
        os.system('mount %s /media/$SUDO_USER/PI_ROOT' %devicenamep2)
    else:
        tmux.cmd(1,'mkdir /media/$SUDO_USER/PI_ROOT',blocking=True)
        tmux.cmd(1,'mount %s /media/$SUDO_USER/PI_ROOT' %devicenamep2,blocking=True)
        #tmux.cmd(1,'df -h')
    time.sleep(3)


def sudobash(tmux):
    tmux.cmd(1,'sudo bash')
    time.sleep(1)
    tmux.cmd(1,'marrtino')
    time.sleep(1)

def format(tmux):
    print('Formatting ...')

    wid = 1
    umount(tmux)
    tmux.cmd(wid,'fdisk %s' %devicename,2)
    tmux.cmd(wid,'p\no\nw\n')
    time.sleep(1)
    tmux.cmd(wid,'fdisk %s' %devicename,2)
    tmux.cmd(wid,'n\np\n1\n2048\n133119\nt\ne\np\n')
    time.sleep(1)
    tmux.cmd(wid,'n\np\n2\n133120\n20613119\np\n')
    time.sleep(1)
    tmux.cmd(wid,'n\np\n3\n\n\np\nw\n',3)

    umount(tmux)

    tmux.cmd(wid,'mkfs.fat -n PI_BOOT %s' %devicenamep1,blocking=True)
    tmux.cmd(wid,'mkfs.ext4 -F -L PI_ROOT %s' %devicenamep2,blocking=True)
    tmux.cmd(wid,'mkfs.ext4 -F -L data %s' %devicenamep3,blocking=True)
    time.sleep(3)

    tmux.cmd(wid,'fdisk %s' %devicename,2)
    tmux.cmd(wid,'a\n1\np\nw\n',3)

    umount(tmux)

def write(tmux, imagefile):
    print('Writing ...')
    #umount(tmux)
    wid=2

    cmd = 'dd if=%s_boot.img bs=512 of=%s' %(imagefile,devicenamep1)
    tmux.cmd(wid, cmd, blocking=True)
    cmd = 'dd if=%s_root.img | pv -s 10G | dd bs=512 of=%s' %(imagefile,devicenamep2)
    tmux.cmd(wid, cmd, blocking=True)
    tmux.cmd(wid, 'sudo sync', blocking=True)

    umount(tmux)

def getline(fname,n=1):
    r = ''
    try:
        f = open(fname,'r')
        r = ''
        for i in range(n):
            if i==n-1:
                r = f.readline().replace('\n','')
            else:
                f.readline()
        f.close()
    except:
        print('Cannot read from file %s' %fname)
    return r


def check(tmux=None, fsck=False, wid=1):
    if fsck:
        os.system('xterm -e "sudo tmux a -t sdconfig" &')
        umount(tmux)
        tmux.cmd(wid,'fsck.ext4 -y %s' %devicenamep2, blocking=True)
        tmux.cmd(wid,'fsck.ext4 -y %s' %devicenamep3, blocking=True)

    mount(None)

    mdir = '/media/%s/PI_ROOT' %os.getenv('SUDO_USER')
    fAP = '%s/etc/NetworkManager/system-connections/MARRtinoAP' %mdir
    f = open(fAP,'r')
    l = f.readline()
    while l is not None and l!='':
        if l[0:4]=='chan':
            channel = l[8:].replace('\n','')
        if l[0:4]=='ssid':
            ssid = l[5:].replace('\n','')
        if l[0:3]=='psk':
            password = l[4:].replace('\n','')
        l = f.readline()
    f.close()

    hostname = getline('%s/etc/hostname' %mdir)

    hosts = getline('%s/etc/hosts' %mdir,2)

    machine = getline('%s/home/ubuntu/.marrtino_machine' %mdir)

    version = getline('%s/home/ubuntu/.marrtino_version' %mdir)

    motorboard = getline('%s/home/ubuntu/.marrtino_motorboard' %mdir)

    print('Machine: %s' %machine)
    print('Version: %s' %version)
    print('Motorboard: %s' %motorboard)
    print('Hostname: %s' %hostname)
    print('Hosts: %s' %hosts)
    print('SSID: %s' %ssid)
    print('Channel: %s' %channel)
    print('Password: %s' %password)

    os.system('umount %s' %devicenamep2)



def read(tmux, imagefile):
    print('Reading ...')
    #umount(tmux)
    wid=1

    cmd = 'dd if=%s bs=512 of=%s_boot.img' %(devicenamep1,imagefile)
    tmux.cmd(wid, cmd, blocking=True)
    cmd = 'dd if=%s bs=512 | pv -s 10G | dd of=%s_root.img' %(devicenamep2,imagefile)
    tmux.cmd(wid, cmd, blocking=True)
    tmux.cmd(wid, 'sudo sync', blocking=True)


def test(tmux):
    wid=3
    tmux.cmd(wid,'echo sleep 10 non blocking...')
    tmux.cmd(wid,'date')
    tmux.cmd(wid,'sleep 10',1)
    tmux.cmd(wid,'date')
    tmux.cmd(wid,'echo done')

    tmux.cmd(wid,'echo sleep 10 blocking...')
    tmux.cmd(wid,'date')
    tmux.cmd(wid,'sleep 10',blocking=True)
    tmux.cmd(wid,'date')
    tmux.cmd(wid,'echo done')


def setDeviceNames(devname):
    global devicename, devicenamep1, devicenamep2, devicenamep3

    devicename = devname
    if (devicename[0:7]=='/dev/mm'):
        devicenamep1 = devicename + 'p1'
        devicenamep2 = devicename + 'p2'
        devicenamep3 = devicename + 'p3'
        print('%s' %devicenamep1)
    elif (devicename[0:7]=='/dev/sd'):
        devicenamep1 = devicename + '1'
        devicenamep2 = devicename + '2'
        devicenamep3 = devicename + '3'
  
    print('Device: %s (%s, %s, %s)' %(devicename,devicenamep1,devicenamep2,devicenamep3))


# Read image from SD card
def readSDCard(devname, imagefile):

    setDeviceNames(devname)

    print('Read SD card %s to image file %s' %(devicename,args.imagefile))

    if os.geteuid() != 0:
        exit("You need to have root privileges to run this script.")
    
    val = raw_input('Please confirm [yes/no] ')
    if val=='yes':
        tmux = TmuxSend('sdconfig',['bash','read'])

        print("Running  'sudo tmux a -t sdconfig'  in a new terminal to check progresses.")
        os.system('xterm -e "sudo tmux a -t sdconfig" &')
        read(tmux,imagefile)
        print('Done')


# Write image to SD card
def writeSDCard(devname, imagefile):

    setDeviceNames(devname)

    print('Format SD card %s with image file %s' %(devicename,imagefile))

    if os.geteuid() != 0:
        exit("You need to have root privileges to run this script.")
    
    print('ALL DATA FROM SD CARD %s WILL BE ERASED!!!' %(devicename))
    val = raw_input('Please confirm [yes/no] ')
    if val=='yes':

        tmux = TmuxSend('sdconfig',['bash','format','write','check'])

        print("Running  'sudo tmux a -t sdconfig'  in a new terminal to check progresses.")
        os.system('xterm -e "sudo tmux a -t sdconfig" &')
        format(tmux)
        write(tmux,imagefile)
        #check(tmux, fsck=True, wid=3)
        print('Done')


# Check SD card
def checkSDCard(devname):

    setDeviceNames(devname)

    print('Check SD card %s' %(devicename))

    if os.geteuid() != 0:
        exit("You need to have root privileges to run this script.")

    check()


def replace(fname, olds, news):
    cmd =  " awk '{gsub(\"%s\",\"%s\")}1' %s > %s.new" %(olds,news,fname,fname)
    os.system(cmd)


def setSDCard(devname, ssid, channel, password, hostname):
    setDeviceNames(devname)

    print('Set values in SD card %s' %(devicename))
    print('SSID: %s\nChannel: %s\nPassword: %s\nHostname: %s' 
            %(ssid, channel, password, hostname))
    if os.geteuid() != 0:
        exit("You need to have root privileges to run this script.")

    mount(None)

    mdir = '/media/%s/PI_ROOT' %os.getenv('SUDO_USER')
    fAP = '%s/etc/NetworkManager/system-connections/MARRtinoAP' %mdir
    os.system('cp %s %s.bak' %(fAP,fAP))
    fin = open(fAP+'.bak','r')
    fout = open(fAP,'w')
    l = fin.readline()
    while l is not None and l!='':
        if l[0:4]=='chan' and channel is not None:
            l = 'channel=%d\n' %channel
        if l[0:4]=='ssid' and ssid is not None:
            l = 'ssid=%s\n' %ssid
        if l[0:3]=='psk' and password is not None:
            l = 'psk=%s\n' %password
        fout.write(l)
        l = fin.readline()
    fin.close()
    fout.close()

    if hostname is not None:
        os.system('echo "%s" > %s/etc/hostname' %(hostname,mdir))
        fAP = '%s/etc/hosts' %mdir
        os.system('cp %s %s.bak' %(fAP,fAP))
        fin = open(fAP+'.bak','r')
        fout = open(fAP,'w')
        l = fin.readline()
        while l is not None and l!='':
            if l[0:9]=='127.0.1.1' and hostname is not None:
                l = '127.0.1.1    %s\n' %hostname
            fout.write(l)
            l = fin.readline()
        fin.close()
        fout.close()

    os.system('umount %s' %devicenamep2)


def speedSDCard(devname):

    setDeviceNames(devname)
    print('Check read/write speed of SD card %s' %(devicename))
    if os.geteuid() != 0:
        exit("You need to have root privileges to run this script.")

    mount(None)
    mdir = '/media/%s/PI_ROOT' %os.getenv('SUDO_USER')
    tf = '%s/tmp/testspeed' %mdir

    print('Write test (%s)' %tf)
    cmd = 'dd if=/dev/urandom of=/tmp/testspeed bs=512 count=200000'
    os.system(cmd)
    cmd = 'dd if=/tmp/testspeed of=%s bs=512 count=200000' %tf
    os.system(cmd)
    print('Read test')
    cmd = 'dd if=%s of=/dev/null bs=512 count=200000' %tf
    os.system(cmd)
    os.system('rm /tmp/testspeed %s' %tf)

    os.system('umount %s' %devicenamep2)


# Main program

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='MARRtino SD config')
    parser.add_argument('op', type=str, help='[read, write, check, set, speed]')
    parser.add_argument('device', type=str, help='device name (e.g.: %s)' %devicename, default=devicename)
    parser.add_argument('-imagefile', type=str, help='image file prefix (e.g., raspi3b_marrtino_2.0)', default=None)
    parser.add_argument('-ssid', type=str, help='Wlan SSID', default=None)
    parser.add_argument('-channel', type=int, help='Wlan channel', default=None)
    parser.add_argument('-password', type=str, help='Wlan password', default=None)
    parser.add_argument('-hostname', type=str, help='host name', default=None)

    args = parser.parse_args()

    if (args.op=='read' or args.op=='write') and args.imagefile is None:
        print('Image file needed for read/write operations')
        sys.exit(1)

    if args.op=='read':
        readSDCard(args.device, args.imagefile)
    elif args.op=='write':
        writeSDCard(args.device, args.imagefile)
    elif args.op=='check':
        checkSDCard(args.device)
    elif args.op=='set':
        setSDCard(args.device,args.ssid,args.channel,args.password,args.hostname)
    elif args.op=='speed':
        speedSDCard(args.device)



