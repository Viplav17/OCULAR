import os
import sys
import time
import json
import logging

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'
logging.getLogger("tensorflow").setLevel(logging.ERROR)
logging.getLogger("tf_keras").setLevel(logging.ERROR)

def quiet_unraisable_hook(unraisable):
    if issubclass(unraisable.exc_type, ValueError) and "I/O operation on closed file" in str(unraisable.exc_value):
        return
    sys.__unraisablehook__(unraisable)

sys.unraisablehook = quiet_unraisable_hook

from Face_Identification.Face_Extractor import Detect_Encode_Face
from Searching.Search import Search
from Blockchain.Backend.Core.BlockChain import BlockChain

TEST_IMAGE = "Test_Image.png"
LOG_FILE = "test_run_log.json"

def delay_print(message: str, delay: float = 1.0):
    print(message)
    time.sleep(delay)

def run_tests():
    """
    Automated test runner verifying all Task 3 technical requirements:
    1. Face detection and embedding vector generation.
    2. Dynamic web search and threshold candidate filtering.
    3. Blockchain block creation and genesis linkage.
    4. Positive cryptographic verification.
    5. Negative tamper-detection verification (tamper evidence).
    6. Complete execution logging to JSON.
    """
    test_logs = {
        "timestamp": time.time(),
        "tests": []
    }

    print("=========================================================")
    print("      HH GOA 2026 - TASK 3 PIPELINE TEST SUITE          ")
    print("=========================================================\n")
    time.sleep(1.0)

    # TEST 1: Face Detection & Encoding
    delay_print("[TEST 1/5] Testing Face Detection & ArcFace Vectorization...")
    t1_start = time.time()
    try:
        embedding = Detect_Encode_Face(TEST_IMAGE)
        assert len(embedding) == 512, "Embedding dimensionality must be 512"
        t1_status = "PASSED"
        delay_print(f"    [+] Success: Detected face and extracted {len(embedding)}-d vector.")
    except Exception as e:
        t1_status = f"FAILED: {str(e)}"
        delay_print(f"    [-] Failed: {e}")
    
    test_logs["tests"].append({
        "test_name": "Face Detection and Encoding",
        "status": t1_status,
        "duration_sec": round(time.time() - t1_start, 2)
    })
    delay_print("---------------------------------------------------------")

    # TEST 2: Web & Social Search Verification
    delay_print("[TEST 2/5] Testing Reverse Search & Identity Discovery...")
    t2_start = time.time()
    matches = []
    try:
        matches = Search(TEST_IMAGE)
        assert len(matches) > 0, "At least one matching social profile or post must be returned"
        t2_status = "PASSED"
        delay_print(f"    [+] Success: Found {len(matches)} matching target(s).")
        delay_print(f"    [+] Top Result: {matches[0].get('title', 'Unknown')} ({matches[0].get('page_url')})")
    except Exception as e:
        t2_status = f"FAILED: {str(e)}"
        delay_print(f"    [-] Failed: {e}")

    test_logs["tests"].append({
        "test_name": "Web/Social Media Search",
        "status": t2_status,
        "matches_found": len(matches),
        "duration_sec": round(time.time() - t2_start, 2)
    })
    delay_print("---------------------------------------------------------")

    # TEST 3: Blockchain Minting & Ledger Integrity
    delay_print("[TEST 3/5] Testing Blockchain Ingestion & Genesis Continuity...")
    t3_start = time.time()
    bc = BlockChain()
    new_block = None
    try:
        assert len(bc.chain) == 1, "Ledger must initialize with Genesis block"
        test_payload = matches[0:1] if matches else [{"test_data": "sample_record"}]
        new_block = bc.Add_Block(test_payload)
        assert new_block.Height == 1, "New block height must be 1"
        assert new_block.BlockHeader.PrevBlockHash == bc.chain[0].Block_Hash, "Parent hash pointer mismatch"
        t3_status = "PASSED"
        delay_print(f"    [+] Success: Block #1 minted with Hash: {new_block.Block_Hash[:24]}...")
    except Exception as e:
        t3_status = f"FAILED: {str(e)}"
        delay_print(f"    [-] Failed: {e}")

    test_logs["tests"].append({
        "test_name": "Blockchain Ingestion",
        "status": t3_status,
        "duration_sec": round(time.time() - t3_start, 2)
    })
    delay_print("---------------------------------------------------------")

    # TEST 4: Ledger Cryptographic Re-Verification
    delay_print("[TEST 4/5] Testing On-Chain Cryptographic Re-Verification...")
    t4_start = time.time()
    try:
        is_valid = bc.Verify_Block(new_block)
        assert is_valid is True, "Block verification must pass on untampered data"
        t4_status = "PASSED"
        delay_print("    [+] Success: Block verification cryptographically confirmed (PASSED).")
    except Exception as e:
        t4_status = f"FAILED: {str(e)}"
        delay_print(f"    [-] Failed: {e}")

    test_logs["tests"].append({
        "test_name": "Cryptographic Verification",
        "status": t4_status,
        "duration_sec": round(time.time() - t4_start, 2)
    })
    delay_print("---------------------------------------------------------")

    # TEST 5: Tamper-Evident Negative Test (Above & Beyond)
    delay_print("[TEST 5/5] Testing Tamper-Evident Detection (Negative Proof)...")
    t5_start = time.time()
    try:
        delay_print("    [*] Step 1: Grabbing valid Block #1 from the ledger...")
        tampered_block = new_block
        
        delay_print("    [*] Step 2: Injecting malicious mutation into the block's data payload...")
        tampered_block.Data = [{"malicious_actor": "modified_identity_proof"}]
        delay_print(f"        -> New Data injected: {tampered_block.Data}")
        
        delay_print("    [*] Step 3: Triggering the cryptographic verification protocol...")
        # The verify block function calculates the hash of the new data and compares it to the original header
        tamper_detected = not bc.Verify_Block(tampered_block)
        delay_print("    [*] Step 4: Cryptographic hash mismatch detected by the ledger!")
        
        assert tamper_detected is True, "Tampered payload must trigger validation failure"
        t5_status = "PASSED"
        delay_print("    [+] Success: Payload corruption caught. Block rejected cryptographically.")
    except Exception as e:
        t5_status = f"FAILED: {str(e)}"
        delay_print(f"    [-] Failed: {e}")

    test_logs["tests"].append({
        "test_name": "Tamper-Evident Detection",
        "status": t5_status,
        "duration_sec": round(time.time() - t5_start, 2)
    })
    delay_print("=========================================================")

    # Write log to JSON
    with open(LOG_FILE, "w") as f:
        json.dump(test_logs, f, indent=4)
    print(f"\n[✓] All tests concluded. Detailed log written to '{LOG_FILE}'.")

if __name__ == "__main__":
    run_tests()