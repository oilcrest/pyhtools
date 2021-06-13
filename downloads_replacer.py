#!usr/bin/env python

#########################################################################
# Author : Dhrumil Mistry
#########################################################################


#########################################################################
# If you encounter Import error after installing netfilter use command 
# sudo pip3 install --upgrade -U git+https://github.com/kti/python-netfilterqueue 
#########################################################################


from os import remove
from subprocess import call
import netfilterqueue
import scapy.all as scapy


SPOOF_WEBSITE = b'www.google.com'
SPOOF_RDATA = b'10.0.2.15'

############################### Functions ############################### 
def forward_packets():
    '''
    configures the mitm for incoming request packets
    into a queue.
    '''

    # executing the following command
    # iptables -I FOWARD -j NFQUEUE --queue-num (any number)
    # sudo iptables -I FORWARD -j NFQUEUE --queue-num 0
    # -I -> insert (packet into a chain specified by the user)
    # -j -> jump if the packet matches the target.
    # --queue-num -> jump to specfic queue number
    # call('sudo iptables -I FORWARD -j NFQUEUE --queue-num 0', shell=True)

    # for local host
    call('sudo iptables -I INPUT -j NFQUEUE --queue-num 0', shell=True)
    call('sudo iptables -I OUTPUT -j NFQUEUE --queue-num 0', shell=True)
    


def reset_config():
    '''
    resets the configurations changed while exectution of the program to 
    its original configuration.
    '''
    call('sudo iptables --flush', shell=True)

ack_list = []

def process_packet(packet):
    '''
    process received packet, everytime a packet is received.
    prints the packet received in the queue and it changes 
    the DNS response dest ip with your desired ip.
    '''
    scapy_pkt = scapy.IP(packet.get_payload())

    # HTTP layer is in the Raw layer.
    # if dport (destination port) = http (i.e. port 80) in TCP and raw layer 
    # consists of get method then, packet consists a HTTP request.
    # 
    # if sport (source port) = http (80) in TCP then the packet consists 
    # a HTTP response.
    #  
    if scapy_pkt.haslayer(scapy.Raw):
        if scapy_pkt[scapy.TCP].dport == 80:
            if b".exe" in scapy_pkt[scapy.Raw].load:
                print('[*] EXE Request Detected!')
                ack_list.append(scapy_pkt[scapy.TCP].ack)
                print(scapy_pkt.show())
                print()

            if b".txt" in scapy_pkt[scapy.Raw].load:
                print('[*] TXT Request Detected!')
                ack_list.append(scapy_pkt[scapy.TCP].ack)
                print(scapy_pkt.show())
                print()

        elif scapy_pkt[scapy.TCP].sport == 80:
            if scapy_pkt[scapy.TCP].seq in ack_list:
                print('[*] Replacing File!\n')
                ack_list.remove(scapy_pkt[scapy.TCP].seq)
                print(scapy_pkt.show())
                print()
        

    packet.accept()
    

############################### Main ############################### 

print('[*] configuring packet receiver...')

forward_packets()
print('[*] packet receiver configured successfully.\n')

print('[*] Creating Queue to start receiving packets.')
try:
    queue = netfilterqueue.NetfilterQueue()
    # Bind queue with queue-number 0
    queue.bind(0, process_packet)
    queue.run()

except OSError as e:
    print('[-] Run script with root priviliges.')
    print(e)

except KeyboardInterrupt:
    print('\r[-] Keyboard Interrupt detected!')

except Exception:
    print('[-] An Exception occurred while creating queue.\n', Exception)

finally:
    print('[*] Restoring previous configurations.. please be patient...')
    reset_config()

    print('[-] Program stopped.')
