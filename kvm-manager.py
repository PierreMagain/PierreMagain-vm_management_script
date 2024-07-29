#!/usr/bin/python3

import os
import sys
import subprocess

######## Variables ########

kvm_dir = f"/home/{os.getenv('USER')}/Documents/KVM"
current_dir = os.getcwd()
config_file = f"{current_dir}/kvm-manager.conf"
request = sys.argv[1]
delay = 2

###### Functions ######

def confirm_request():
    confirm = input(f"Please Confirm your request **{request}** request (yes) : ")
    if not confirm or confirm != 'yes':
        print("You didn't enter 'yes'. Leaving now. Bye Bye!")
        sys.exit()

def clone_vm(vm, type, lan):
    template = f"0-{type}"
    subprocess.run(["virt-clone", "--original", template, "--name", vm, "--file", f"{kvm_dir}/{vm}.qcow2"])
    subprocess.run(["sleep", str(delay)])
    subprocess.run(["virsh", "detach-interface", vm, "network", "--persistent"])
    subprocess.run(["sleep", str(delay)])
    subprocess.run(["virsh", "attach-interface", vm, "network", lan, "--model", "virtio", "--persistent"])
    subprocess.run(["sleep", str(delay)])
    subprocess.run(["virsh", "start", vm])

def manage_vm(action, vm):
    subprocess.run(["virsh", action, vm])
    subprocess.run(["sleep", str(delay)])

####### Main code ########

match request:
    case 'clone' | 'destroy':
        confirm_request()
    case 'start' | 'stop' :
        print('ok let\'go')
    case _:
        print("********************************************")
        print("**** Usage  : clone|start|stop|destroy *****")
        print("********************************************")
        pass

with open(config_file, 'r') as file:
    for line in file:
        if not line.strip() or line.strip().startswith('#'):
            continue
        
        vm, type, lan, user, port = line.strip().split('|')
        
        match request:
            case 'clone':
                clone_vm(vm.strip(), type.strip(), lan.strip())
            case 'start':
                manage_vm("start", vm.strip())
            case 'stop':
                manage_vm("shutdown", vm.strip())
            case 'destroy':
                manage_vm("shutdown", vm.strip())
                manage_vm("undefine", vm.strip())
                subprocess.run(["virsh", "vol-delete", f"{kvm_dir}/{vm}.qcow2", "--pool", "default"])
