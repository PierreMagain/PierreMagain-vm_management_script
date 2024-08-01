#!/usr/bin/python3

import os
import sys
import subprocess
import time

######## Variables ########

kvm_dir = f"/home/{os.getenv('USER')}/Documents/KVM"
current_dir = os.getcwd()
config_file = f"{current_dir}/kvm-manager.conf"
inventory_file = f"{current_dir}/inventory.ini"
request = sys.argv[1] if len(sys.argv) > 1 else None
delay = 5

###### Functions ######

def confirm_request():
    confirm = input(f"Please confirm your **{request}** request (yes) : ")
    if not confirm or confirm != 'yes':
        print("You didn't enter 'yes'. Leaving now, Bye Bye!")
        sys.exit()

def create_inventory_file():
    if not os.path.isfile(inventory_file):
        with open(inventory_file, 'w') as file:
            file.write("# Ansible groups\n")

    with open(inventory_file, 'r') as file:
        lines = file.readlines()
    
    with open(inventory_file, 'w') as file:
        write = False
        for line in lines:
            if line.strip() == "# Ansible groups":
                write = True
            if write:
                file.write(line)

def clone_vm(vm, distro, ram, lan):
    template = f"0-{distro}"
    subprocess.run(["virt-clone", "--original", template, "--name", vm, "--file", f"{kvm_dir}/{vm}.qcow2"])
    time.sleep(delay)
    subprocess.run(["virsh", "detach-interface", vm, "network", "--persistent"])
    time.sleep(delay)
    subprocess.run(["virsh", "attach-interface", vm, "network", lan, "--model", "virtio", "--persistent"])
    time.sleep(delay)
    print(f"Setting RAM and max RAM to {ram}M")
    subprocess.run(["virsh", "setmaxmem", vm, f"{ram}M", "--config"])
    time.sleep(delay)
    subprocess.run(["virsh", "setmem", vm, f"{ram}M", "--config"])
    subprocess.run(["virsh", "start", vm])

def set_inventory(vm, user, port):
    result = subprocess.run(["virsh", "domifaddr", vm], capture_output=True, text=True)
    ip = None
    for line in result.stdout.splitlines():
        if 'ipv4' in line:
            ip = line.split()[4].split('/')[0]
            break

    if ip:
        line = f"{vm} ansible_host={ip} ansible_user={user} ansible_port={port}\n"
        with open(inventory_file, 'r+') as file:
            content = file.read()
            file.seek(0)
            file.write(line + content)
    else:
        print(f"Failed to get IP address for {vm}")

def manage_vm(action, vm):
    subprocess.run(["virsh", action, vm])
    time.sleep(delay)

####### Main code ########

if request is None:
    print("************************************************************")
    print("**** Usage: clone|inv|inventory|start|shutdown|undefine ****")
    print("************************************************************")
    sys.exit()

if request in ['clone', 'undefine']:
    confirm_request()
elif request == 'inv' or request == 'inventory':
    create_inventory_file()

with open(config_file, 'r') as file:
    for line in file:
        if not line.strip() or line.strip().startswith('#'):
            continue
        
        parts = line.strip().split('|')
        vm = parts[0].strip()
        distro = parts[1].strip()
        ram = parts[2].strip()
        lan = parts[3].strip()
        user = parts[4].strip()
        port = parts[5].strip()

        if request == 'clone':
            clone_vm(vm, distro, ram, lan)
        elif request in ['inv', 'inventory']:
            set_inventory(vm, user, port)
        elif request == 'start':
            manage_vm("start", vm)
        elif request == 'shutdown':
            manage_vm("shutdown", vm)
        elif request == 'undefine':
            manage_vm("shutdown", vm)
            time.sleep(3)
            manage_vm("undefine", vm)
            subprocess.run(["virsh", "vol-delete", f"{kvm_dir}/{vm}.qcow2", "--pool", "default"])
