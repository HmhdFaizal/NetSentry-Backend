from collections import defaultdict
import time



def get_flow_key(packet_record):
    return(
        packet_record["src_ip"],
        packet_record["src_port"],
        packet_record["dst_ip"],
        packet_record["dst_port"],
        packet_record["protocol"],
      
    )


def create_flow_stats(packet_record):
    return {
        "packet_count": 1,
        "total_bytes": packet_record["packet_length"],
        "first_seen": packet_record["timestamp"],
        "last_seen": packet_record["timestamp"],
    }
def update_flow_stats(flow_stats, packet_record):
    flow_stats["packet_count"] += 1
    flow_stats["total_bytes"] += packet_record["packet_length"]
    flow_stats["last_seen"] = packet_record["timestamp"]

first_packet = {
    "timestamp": 1000.0,
    "src_ip": "192.168.1.10",
    "src_port": 5000,
    "dst_ip": "192.168.1.20",
    "dst_port": 443,
    "protocol": "TCP",
    "packet_length": 500,
}

second_packet = {
    "timestamp": 1002.0,
    "src_ip": "192.168.1.10",
    "src_port": 5000,
    "dst_ip": "192.168.1.20",
    "dst_port": 443,
    "protocol": "TCP",
    "packet_length": 1000,
}

third_packet = {
    "timestamp": 1003.0,
    "src_ip": "192.168.1.30",
    "src_port": 6000,
    "dst_ip": "192.168.1.40",
    "dst_port": 80,
    "protocol": "TCP",
    "packet_length": 300,
}

def calculate_flow_features(flow_stats):
    duration = flow_stats["last_seen"] - flow_stats["first_seen"]

    packet_rate = (
        flow_stats["packet_count"] / duration
        if duration > 0
        else 0.0
    )

    byte_rate = (
        flow_stats["total_bytes"] / duration
        if duration > 0
        else 0.0
    )

    return {
        "packet_count": flow_stats["packet_count"],
        "total_bytes": flow_stats["total_bytes"],
        "duration_seconds": duration,
        "packet_per_second": packet_rate,
        "bytes_per_second": byte_rate,
    }

def process_packet(packet_record,all_flows):
    flow_key = get_flow_key(packet_record)

    if flow_key not in all_flows:
        all_flows[flow_key] = create_flow_stats(packet_record)
    else:
        update_flow_stats(all_flows[flow_key],packet_record)

    

all_flows = {}

process_packet(first_packet, all_flows)
process_packet(second_packet, all_flows)
process_packet(third_packet, all_flows)

for flow_key, flow_stats in all_flows.items():
    print("Flow:", flow_key)
    print("Features:", calculate_flow_features(flow_stats))


def expire_old_flows(all_flows,timeout_seconds = 60):
    current_time = time.time()
    expired_flows = []

    for flow_key, stats in list(all_flows.items()):
        if current_time - stats["last_seen"] > timeout_seconds:
            final_features = calculate_flow_features(stats)

            expired_flows.append({
                "flow_key": flow_key,
                "features": final_features,
            })
            del all_flows[flow_key]
    return expired_flows

test_time = time.time()


test_time = time.time()

all_flows = {
    ("192.168.1.50", 7000, "192.168.1.60", 80, "TCP"): {
        "packet_count": 3,
        "total_bytes": 900,
        "first_seen": test_time - 125,
        "last_seen": test_time - 120,
    },

    ("192.168.1.70", 8000, "192.168.1.80", 443, "TCP"): {
        "packet_count": 4,
        "total_bytes": 2000,
        "first_seen": test_time - 10,
        "last_seen": test_time - 5,
    },
}

completed_flows = expire_old_flows(
    all_flows,
    timeout_seconds=60,
)

print("Completed flows:", completed_flows)
print("Remaining active flows:", len(all_flows))
print("Active flow keys:", list(all_flows.keys()))
