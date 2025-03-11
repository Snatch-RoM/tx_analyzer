#!/usr/bin/python3

import json
import subprocess
import sys
import re

SSH_HOST = "hodlr"
BITCOIN_CLI_PATH = "/snap/bitcoin-core/current/bin/bitcoin-cli"

def run_ssh_command(command):
    """Executes an SSH command and returns the result."""
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.returncode != 0:
            print("❌ Error:", result.stderr)
            return None
        return result.stdout.strip()
    except Exception as e:
        print(f"❌ Failed to execute command: {e}")
        return None

def get_transaction(txid):
    """Fetch raw transaction JSON."""
    cmd = f"ssh -x {SSH_HOST} {BITCOIN_CLI_PATH} getrawtransaction {txid} 1"
    result = run_ssh_command(cmd)
    if result:
        return json.loads(result)
    sys.exit(1)

def decode_script(script_hex):
    """Decode a Bitcoin script."""
    if not script_hex:
        return "N/A"
    cmd = f"ssh -x {SSH_HOST} {BITCOIN_CLI_PATH} decodescript {script_hex}"
    decoded_script = run_ssh_command(cmd)
    if decoded_script:
        return json.loads(decoded_script).get("asm", "Could not decode script")
    return "Could not decode script"

def extract_opcodes(script):
    """Extract OP codes from script."""
    if not script:
        return "N/A"
    opcodes = re.findall(r'OP_[A-Z0-9_]+', script)
    return " ".join(opcodes) if opcodes else "No OP codes found"

def detect_multisig(script):
    """Detect M-of-N multi-sig."""
    if "OP_CHECKMULTISIG" not in script:
        return "No Multi-Sig"
    parts = script.split()
    try:
        n = parts[parts.index("OP_CHECKMULTISIG") - 1]
        m = parts[0]
        if m.isdigit() and n.isdigit():
            return f"🔐 Multi-Sig: {m}-of-{n}"
    except (IndexError, ValueError):
        return "🔐 Multi-Sig Detected, but M/N extraction failed"
    return "🔐 Multi-Sig Detected"

def calculate_fees(tx_data):
    """Calculate transaction fee and sats per vByte."""
    total_input = 0
    total_output = sum(vout["value"] for vout in tx_data["vout"])
    
    for vin in tx_data["vin"]:
        prev_tx = get_transaction(vin["txid"]) if "txid" in vin else None
        if prev_tx:
            prev_output = prev_tx["vout"][vin["vout"]]["value"]
            total_input += prev_output
    
    if total_input > 0:
        fee = total_input - total_output
        sats_per_vbyte = (fee * 1e8) / tx_data["vsize"]
        return fee, sats_per_vbyte
    return None, None

def analyze_transaction(tx_data):
    """Analyze a Bitcoin transaction."""
    fee, sats_per_vbyte = calculate_fees(tx_data)
    
    report = []
    report.append(f"### Bitcoin Transaction Analysis")
    report.append(f"TXID: {tx_data['txid']}")
    report.append(f"Version: {tx_data['version']}")
    report.append(f"Size: {tx_data['size']} bytes")
    report.append(f"vSize: {tx_data['vsize']} vbytes")
    report.append(f"Weight: {tx_data['weight']} weight units")
    report.append(f"Locktime: {tx_data['locktime']}")
    report.append(f"Inputs: {len(tx_data['vin'])} | Outputs: {len(tx_data['vout'])}")
    
    if any(vin["sequence"] < 4294967295 for vin in tx_data["vin"]):
        report.append("🚀 **RBF Enabled**")
    else:
        report.append("🚫 **RBF Disabled**")
    
    if fee is not None:
        report.append(f"Fee: {fee:.8f} BTC")
        report.append(f"Sats per vByte: {sats_per_vbyte:.2f} sat/vByte")
    else:
        report.append("Fee: Unknown (input amounts missing)")
    
    report.append("\n---")
    report.append("| #  | Spent TXID | Output Index | Sequence | Decoded ScriptSig | OP Codes |")
    report.append("|----|----------------|--------------|----------|------------------|--------------|")
    
    for i, vin in enumerate(tx_data["vin"]):
        spent_txid = vin.get("txid", "Coinbase")[0:7] + "..." + vin.get("txid", "Coinbase")[-7:]
        script_sig = vin.get("scriptSig", {}).get("asm", "N/A")
        opcodes = extract_opcodes(script_sig)
        report.append(f"| {i+1}  | {spent_txid} | {vin['vout']} | {vin['sequence']} | {script_sig[:15]}... | {opcodes} |")
    
    report.append("\n---")
    report.append("| #  | BTC Value | Script Type | Address | Decoded ScriptPubKey | OP Codes |")
    report.append("|----|---------------|--------------------|---------|---------------------|--------------|")
    
    for i, vout in enumerate(tx_data["vout"]):
        script_pubkey = vout["scriptPubKey"]["asm"]
        opcodes = extract_opcodes(script_pubkey)
        address = vout["scriptPubKey"].get("address", "N/A")[0:7] + "..." + vout["scriptPubKey"].get("address", "N/A")[-7:]
        report.append(f"| {i+1}  | {vout['value']:.8f} BTC | {vout['scriptPubKey']['type']} | {address} | {script_pubkey[:15]}... | {opcodes} |")
    
    return "\n".join(report)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python btc_tx_analyzer.py <txid>")
        sys.exit(1)
    txid = sys.argv[1]
    tx_data = get_transaction(txid)
    report = analyze_transaction(tx_data)
    print(report)

