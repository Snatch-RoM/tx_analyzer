Current Feature List

Fetch & Decode Transaction Data
. Uses bitcoin-cli getrawtransaction <txid> 1 over SSH.
. Calls decodescript to decode all scripts.

Input & Output Analysis
. Counts Inputs & Outputs (total number reported).
. Extracts previous TXID and output index for each input.
. Reports sequence number for each input.

Advanced Timelock Analysis
. Absolute Timelock (CLTV - CheckLockTimeVerify)
. If locktime is non-zero, reports minimum required block height or timestamp.
. Relative Timelock (CSV - CheckSequenceVerify)
. If any input sequence number is below 0xFFFFFFFE, reports:
    .. Required delay (in blocks or time).
    .. Whether the input is spendable yet.

RBF (Replace-By-Fee) Detection
. If any input has a sequence number below 0xFFFFFFFE, it’s RBF-enabled.
. Displays:
    .. RBF Enabled (if applicable)
    .. RBF Disabled (if all sequence numbers are maxed out 0xFFFFFFFF).

Multi-Sig (M-of-N) Detection
. Detects M-of-N Multi-Sig setups in:
    .. scriptSig
    .. scriptPubKey
    .. Witness scripts
. Extracts M and N values (e.g., 2-of-3).

OP Code Extraction & Script Decoding
. Extracts full OP codes (no shortening!).
. Decodes all scripts:
    .. scriptSig
    .. scriptPubKey
    .. Witness scripts
    .. Previous output scripts
. Reports the full OP code structure in a readable format. Still working on columnar integrity...

Fee & Sats per vByte Calculation
. Computes transaction fee using sum(inputs) - sum(outputs).
. Computes sats per vByte:
. Fee (sats) / vSize (vBytes)

Optimized, Readable Output
. Dynamic column widths (optimized for fixed-width fonts).
. Shortens long hashes, pubkeys, and signatures:
    .. Example: cebb2851...d1dc0
    .. Does not shorten OP codes (displays full OP script). 

Coinbase Transaction Support
. Recognizes coinbase transactions (no vin[].txid).
. Handles coinbase input scripts correctly.

Supports All Bitcoin Script Types
. Recognizes:
. P2PKH (Pay-to-PubKey-Hash)
. P2SH (Pay-to-Script-Hash)
. P2WPKH (Pay-to-Witness-PubKey-Hash)
. P2WSH (Pay-to-Witness-Script-Hash)
. P2TR (Taproot)
. Multisig
. Time-locked transactions
. OP_RETURN (data storage).
