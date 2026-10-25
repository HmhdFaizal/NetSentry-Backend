from scapy.all import TCP,sniff,IP,IPv6,UDP,ICMP
from feature_extraction.traffic_features import(
    process_packet,
    calculate_flow_features,
    expire_old_flows,
)
all_flows = {}

def packet_callback(packet):
    if IP in packet:
        source = packet[IP].src
        destination = packet[IP].dst
    elif IPv6 in packet:
        source = packet[IPv6].src
        destination = packet[IPv6].dst
    else: return

    if TCP in packet:
        protocol = "TCP"
        source_port = int(packet[TCP].sport)
        destination_port = int(packet[TCP].dport)

    elif UDP in packet:
        protocol = "UDP"
        source_port = int(packet[UDP].sport)
        destination_port = int(packet[UDP].dport)

    elif ICMP in packet:
        protocol = "ICMP"
        source_port = 0
        destination_port = 0
    else:
        protocol = "OTHER"
        source_port = 0
        destination_port = 0
    packet_record = {
        "src_ip": source,
        "src_port": source_port,
        "dst_ip": destination,
        "dst_port": destination_port,
        "protocol": protocol,
        "packet_length": len(packet),
        "timestamp": float(packet.time),
    }

    process_packet(packet_record, all_flows)
    print(
        f"{source}:{source_port} - >"
        f"{destination}:{destination_port} |"
        f"{protocol} | {len(packet)} bytes"
    )

print("NetSentry packet monitor starting ....")
print("Waiting to capture 10 IP packets....")

sniff(
    prn = packet_callback,
    count = 10,
    store = False,
    lfilter = lambda packet: IP in packet or IPv6 in packet
)
print("\nCapture finished.")


print("\nCapture finished.")

# Expire flows that have been inactive for over 60 seconds
completed_flows = expire_old_flows(
    all_flows,
    timeout_seconds=60
)

# Display expired flows
for flow in completed_flows:
    print("\nExpired flow:")
    print("Flow key:", flow["flow_key"])
    print("Features:", flow["features"])

# Display remaining active flows
print("\nActive flows:")
for flow_key, stats in all_flows.items():
    print("Flow key:", flow_key)
    print("Features:", calculate_flow_features(stats))
