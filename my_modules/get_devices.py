#!/usr/bin/python
DOCUMENTATION = '''
---
module: setup
short_description: Gathers devices information  about remote hosts
options: {}
description: 
     - This module is automatically called by playbooks to gather devices information
notes: 
    - KK 
examples:
    - code: ansible all -m get_devices
      description: Obtain Devices information from all hosts.
author: 
'''


import os
import re
import sys
import errno
from subprocess import Popen,PIPE

def find_device(data, pciid):
    id = re.escape(pciid)
    m = re.search("^" + id + "\s(.*)$", data, re.MULTILINE)
    return m.group(1)

def pretty_size(size):
    size_strs = ['B', 'KiB', 'MiB', 'GiB', 'TiB']
    last_size = size
    fract_size = size
    num_divs = 0

    while size > 1:
        fract_size = last_size
        last_size = size
        size /= 1024
        num_divs += 1

    num_divs -= 1
    fraction = fract_size / 1024
    pretty = "%.2f" % fraction
    pretty = pretty + size_strs[num_divs]
    return pretty

def virtual_device(path):
    for dir in os.listdir(path):
        if re.search("device", dir):
            return 0
    return 1

class Device:
    def __init__(self):
        self.sectorsize = ""
        self.sectors = ""
        self.rotational = ""
        self.sysdir = ""
        self.host = ""
        self.model = ""
        self.vendor = ""
        self.holders = []
        self.diskname = ""
        self.partitions = []
        self.removable = ""
        self.start = ""
        self.discard = ""
        self.sysfs_no_links = 0

    def populate_model(self):
        try:
            f = open(self.sysdir + "/device/model")
            self.model = f.read().rstrip()
            f.close()
        except IOError:
            # do nothing
            pass

    def populate_vendor(self):
        try:
            f = open(self.sysdir + "/device/vendor")
            self.vendor = f.read().rstrip()
            f.close()
        except IOError:
            #do nothing
            pass

    def populate_sectors(self):
        try:
            f = open(self.sysdir + "/size")
            self.sectors = f.read().rstrip()
            f.close()
        except IOError:
            self.sectors = 0

    def populate_sector_size(self):
        try:
            f = open(self.sysdir + "/queue/hw_sector_size")
            self.sectorsize = f.read().rstrip()
            f.close()
        except IOError:
            # if this sysfs doesnt show us sectorsize then just assume 512
            self.sectorsize = "512"

    def populate_rotational(self):
        try:
            f = open(self.sysdir + "/queue/rotational")
            rotation = f.read().rstrip()
            f.close()
        except IOError:
            self.rotational = "Could not determine rotational"
            return
        if rotation == "1":
            self.rotational = "Spinning disk"
        else:
            self.rotational = "SSD"

    def populate_host(self, pcidata):
        if self.sysfs_no_links == 1:
            try:
                sysdir = os.readlink(os.path.join(self.sysdir, "device"))
            except:
                pass
        else:
            sysdir = self.sysdir
        m = re.match(".+/\d+:(\w+:\w+\.\w)/host\d+/\s*", sysdir)
        if m:
            pciid = m.group(1)
            self.host = find_device(pcidata, pciid)
        else:
            self.host = ""

    def populate_diskname(self):
        m = re.match(".*/(.+)$", self.sysdir)
        self.diskname = m.group(1)

    def populate_holders(self):
        for dir in os.listdir(self.sysdir + "/holders"):
            if re.search("^dm-.*", dir):
                try:
                    f = open(self.sysdir + "/holders/" + dir + "/dm/name")
                    name = f.read().rstrip()
                    f.close()
                    self.holders.append(name)
                except IOError:
                    self.holders.append(dir)
            else:
                self.holders.append(dir)

    def populate_discard(self):
        try:
            f = open(self.sysdir + "/queue/discard_granularity")
            discard = f.read().rstrip()
            f.close()
            if discard == "0":
                self.discard = "No"
            else:
                self.discard = "Yes"
        except IOError:
            self.discard = "No"

    def populate_start(self):
        try:
            f = open(self.sysdir + "/start")
            self.start = f.read().rstrip()
            f.close()
        except IOError:
            pass

    def populate_partitions(self):
        for dir in os.listdir(self.sysdir):
            m = re.search("(" + self.diskname + "\d+)", dir)
            if m:
                partname = m.group(1)
                part = Device()
                part.sysdir = self.sysdir + "/" + partname
                part.populate_part_info()
                self.partitions.append(part)

    def populate_part_info(self):
        """ Only call this if we are a partition """
        self.populate_diskname()
        self.populate_holders()
        self.populate_sectors()
        self.populate_start()

    def populate_removable(self):
        try:
            f = open(self.sysdir + "/removable")
            remove = f.read().rstrip()
            f.close()
            if remove == "1":
                self.removable = "Yes"
            else:
                self.removable = "No"
        except IOError:
            self.removable = "No"

    def populate_all(self, pcidata):
        self.populate_diskname()
        self.populate_holders()
        self.populate_partitions()
        self.populate_removable()
        self.populate_model()
        self.populate_vendor()
        self.populate_sectors()
        self.populate_sector_size()
        self.populate_rotational()
        self.populate_discard()
        self.populate_host(pcidata)

def get_devices(module):
    pcidata = None
    try:
        try:
            p = Popen(["/sbin/lspci"], stdout=PIPE)
        except:
            try:
                p = Popen(["/usr/sbin/lspci"], stdout=PIPE)
            except:
                p = Popen(["lspci"], stdout=PIPE)
        err = p.wait()
        if err:
            print "Error running lspci"
        else:
            pcidata = p.stdout.read()
    except OSError, e:
        module.fail_json( msg="lspci failed %s" % e) # no lspci
    sysfs_no_links = 0
    devices = []

    if len(sys.argv) > 1:
        m = re.match("/dev/(\D+)\d*", sys.argv[1])
        if m:
            block = m.group(1)
        else:
            block = sys.argv[1]

        try:
            path = os.readlink(os.path.join("/sys/block/", block))
        except OSError, e:
            if e.errno == errno.EINVAL:
                path = block
            else:
                print "Invalid device name " + block
                sys.exit()
        d = Device()
        d.sysdir = os.path.join("/sys/block", path)
        d.populate_all(pcidata)
        devices.append(d)
    else:
        for block in os.listdir("/sys/block"):
            try:
                if sysfs_no_links == 0:
                    path = os.readlink(os.path.join("/sys/block/", block))
                else:
                    path = block
            except OSError, e:
                if e.errno == errno.EINVAL:
                    path = block
                    sysfs_no_links = 1
                else:
                    continue
            if re.search("virtual", path):
                continue
            if sysfs_no_links == 1:
                sysdir = os.path.join("/sys/block", path)
                if virtual_device(sysdir) == 1:
                    continue
            d = Device()
            d.sysdir = os.path.join("/sys/block", path)
            d.sysfs_no_links = sysfs_no_links
            d.populate_all(pcidata)
            devices.append(d)    
    return get_devices_info(devices)

def get_devices_info(devices):
    a_devices= {}
    device_names=[]
    dd={}
    for d in devices:
        k={}
        k['host']= d.host
        k['vendor']=d.vendor
        k['model']=d.model
        k['sector size(bytes)']=d.sectorsize
        k['sectors']=d.sectors
        size = float(d.sectors) * float(d.sectorsize)
        pretty = pretty_size(size)
        k['size']=pretty
        k['removable']=d.removable
        k['disk type']= d.rotational
        k['support discard']= d.discard
        if len(d.holders) > 0:
            kk=[]
            i=0
            for h in d.holders:
                kk.append(h)
            k['holders']=kk
        if len(d.partitions) > 0:
            for p in d.partitions:
                kk1={}
                kk1['start sector']=p.start
                kk1['sectors']=p.sectors
                size = float(p.sectors) * float(d.sectorsize)
                pretty = pretty_size(size)
                kk1['size']= pretty
                if len(p.holders) > 0:
                    kk1['holders']={}
                    kk2=[]
                    for h in p.holders:
                        kk2.append(h)
                    kk1['holders']=kk2
 
                k[p.diskname]=kk1
        dd[d.diskname]=k
        device_names.append(d.diskname)
    a_devices['devices']=device_names
    a_devices['device_details']=dd
    return a_devices   

def main():
    global module
    module = AnsibleModule(
        argument_spec = dict()
    )

    data = get_devices(module)
    result = {"ansible_facts": data}
    module.exit_json(**result)

# this is magic, see lib/ansible/module_common.py
#<<INCLUDE_ANSIBLE_MODULE_COMMON>>
main()

# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4
