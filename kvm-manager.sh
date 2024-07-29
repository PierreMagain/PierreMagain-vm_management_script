#!/bin/bash

# Variables
#kvm_dir="/home/delhombre/Documents/KVM"
current_dir="$(pwd)"
kvm_dir="/home/$USER/Documents/KVM"
config_file="$current_dir/kvm-manager.conf"
inventory_file="$current_dir/inventory.ini"
request=$1
delay=5

# Functions
confirm_request()
{
  read -p "Please confirm your **$request** request (yes) : " confirm
  if [ -z $confirm ] || [ $confirm != 'yes' ]
  then
    echo "You didn't enter 'yes'.Leaving now, Bye Bye!"
    exit
  fi
}

create_inventory_file()
{
  if ! [ -f $inventory_file ]
  then
    echo "# Ansible groups" > $inventory_file
  fi

  sed -i '/^# Ansible groups/,$!d' $inventory_file
}

initial_setup ()
{
  case $request in
  clone|undefine)
    confirm_request
    ;;
  inv|inventory)
    create_inventory_file
    ;;
  start|shutdown)
    ;;
  *)
    echo "************************************************************"
    echo "**** Usage: clone|inv|inventory|start|shutdown|undefine ****"
    echo "************************************************************"
    echo
    exit
  esac
}

clone_vm()
{
  template="0-$distro"
  virt-clone --original $template --name $vm --file=$kvm_dir/$vm.qcow2
  sleep $delay
  virsh detach-interface $vm network --persistent
  sleep $delay
  virsh attach-interface $vm network $lan --model virtio --persistent
  sleep $delay
  echo "Setting RAM and max RAM to ${ram}M"
  virsh setmaxmem $vm ${ram}M --config
  sleep $delay
  virsh setmem $vm ${ram}M --config
  virsh start $vm
}

set_inventory()
{
  ip=$(virsh domifaddr $vm | grep ipv4 | tr -s ' ' | cut -d' ' -f5 | cut -d'/' -f1)
  line=$(echo "$vm ansible_host=$ip ansible_user=$user ansible_port=$port")
  echo $line
  sed -i "/^# Ansible groups/i$line" $inventory_file
}

manage_vm()
{
  action=$1
  $@ $vm
  sleep $delay
}

#### Main code ####
initial_setup

#line_number=1
while read line
do
  if [ -z $line ] || [[ $line =~ ^# ]]
  then
    continue
  fi

  vm=$(echo $line | cut -d'|' -f1)
  distro=$(echo $line | cut -d'|' -f2)
  ram=$(echo $line | cut -d'|' -f3)
  lan=$(echo $line | cut -d'|' -f4)
  user=$(echo $line | cut -d'|' -f5)
  port=$(echo $line | cut -d'|' -f6)
  
  case $request in
    clone)
      clone_vm
      ;;
    inv|inventory)
      set_inventory
      ;;
    start)
      manage_vm virsh start
      ;;
    shutdown)
      manage_vm virsh shutdown
      ;;
    undefine)
      manage_vm virsh shutdown
      sleep 3
      manage_vm virsh undefine --remove-all-storage
      ;;
  esac
  #line_number=$[ $line_number + 1 ]
done < "$config_file"