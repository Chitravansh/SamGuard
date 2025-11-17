# import pyshark
# import requests
# import os

# SCORER = os.getenv("SCORER_URL", "http://localhost:5000/score")

# # Your Wi-Fi interface (correct)
# INTERFACE = r"\Device\NPF_{073C257D-AC20-49B8-905B-CF285D93A9A7}"

# def packet_to_event(pkt):
#     try:
#         if 'IP' in pkt:
#             src_ip = pkt.ip.src
#             dst_ip = pkt.ip.dst
#         elif 'IPV6' in pkt:
#             src_ip = pkt.ipv6.src
#             dst_ip = pkt.ipv6.dst
#         else:
#             return None  # ignore non-IP packets

#         length = int(pkt.length)
#         proto = pkt.transport_layer or "UNKNOWN"

#         event = {
#             "src_ip": src_ip,
#             "dst_ip": dst_ip,
#             "bytes_out": length,
#             "bytes_in": 0,
#             "duration": 0,
#             "proto": proto,
#             "pkts": 1
#         }
#         return event

#     except Exception:
#         return None

# def start_capture():
#     print("📡 Live capture started on:", INTERFACE)
#     cap = pyshark.LiveCapture(interface=INTERFACE)

#     for pkt in cap.sniff_continuously():
#         event = packet_to_event(pkt)
#         if event:
#             try:
#                 r = requests.post(SCORER, json=event, timeout=5)
#                 print("Sent:", event["src_ip"], "→", r.status_code)
#             except Exception as e:
#                 print("Error sending:", e)

# if __name__ == "__main__":
#     start_capture()



import pyshark
import requests
import os

# ML scoring endpoint
SCORER = os.getenv("SCORER_URL", "http://localhost:5000/score")


# ---------------------------
#  AUTO-DETECT NETWORK INTERFACE
# ---------------------------
def get_best_interface():
    interfaces = pyshark.tshark.tshark.get_tshark_interfaces()

    preferred = ['Wi-Fi', 'Ethernet', 'WLAN', 'Local Area']

    # Try to match human-readable names
    for iface in interfaces:
        if any(name.lower() in iface.lower() for name in preferred):
            print(f"✔ Auto-selected interface: {iface}")
            return iface

    # Fallback: first Npcap interface (Device\NPF)
    for iface in interfaces:
        if r"\Device\NPF_" in iface:
            print(f"✔ Fallback interface selected: {iface}")
            return iface

    raise RuntimeError("❌ No network interface found!")


INTERFACE = r"\Device\NPF_{073C257D-AC20-49B8-905B-CF285D93A9A7}"


# ---------------------------
#  PACKET → EVENT CONVERSION
# ---------------------------
def packet_to_event(pkt):
    """
    Convert a raw packet into the ML model event structure.
    """
    try:
        # Handle IPv4 packets
        if hasattr(pkt, 'ip'):
            src_ip = pkt.ip.src
            dst_ip = pkt.ip.dst
        # Handle IPv6 packets
        elif hasattr(pkt, 'ipv6'):
            src_ip = pkt.ipv6.src
            dst_ip = pkt.ipv6.dst
        else:
            return None  # Ignore non-IP packets

        length = int(pkt.length)
        proto = pkt.transport_layer or "UNKNOWN"

        event = {
            "src_ip": src_ip,
            "dst_ip": dst_ip,
            "bytes_out": length,
            "bytes_in": 0,     # Not available per packet; optional
            "duration": 0,     # Not available per packet; optional
            "proto": proto,
            "pkts": 1
        }

        return event

    except Exception:
        return None


# ---------------------------
#  START LIVE CAPTURE
# ---------------------------
def start_capture():
    print("📡 Starting LIVE capture on:", INTERFACE)

    cap = pyshark.LiveCapture(interface=INTERFACE)

    for pkt in cap.sniff_continuously():
        event = packet_to_event(pkt)

        if not event:
            continue

        try:
            r = requests.post(SCORER, json=event, timeout=5)
            print("➡ Sent:", event["src_ip"], "→", r.status_code)
        except Exception as e:
            print("❌ Error sending packet:", e)


# ---------------------------
#  MAIN
# ---------------------------
if __name__ == "__main__":
    start_capture()
