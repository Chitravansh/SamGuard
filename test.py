import pyshark

INTERFACE = r"\Device\NPF_{073C257D-AC20-49B8-905B-CF285D93A9A7}"

cap = pyshark.LiveCapture(interface=INTERFACE)

print("🔥 Capturing packets... Press Ctrl+C to stop.")
for pkt in cap.sniff_continuously():
    print(pkt)
