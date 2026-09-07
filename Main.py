import os, logging

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'

logging.getLogger("tensorflow").setLevel(logging.ERROR)
logging.getLogger("tf_keras").setLevel(logging.ERROR)

from Searching.Search import Search
from Blockchain.Backend.Core.BlockChain import BlockChain
from Blockchain.Backend.util.util import hash256

def run_pipeline(input_image: str):
    print("=== HH GOA 2026: Identity Verification Pipeline ===")
    
    # 1. Initialize Blockchain
    ledger = BlockChain()
    print(f"[0] Blockchain initialized (Genesis Hash: {ledger.chain[0].Block_Hash[:16]}...)")

    # 2. Extract & Search Web
    print(f"[1] Searching web matches for {input_image}...")
    matches = Search(input_image)
    
    if not matches:
        print("[!] No confident facial matches found online.")
        return

    print(f"[+] Found {len(matches)} valid match(es).")

    # 3. Mint Blocks for Discovered Matches
    for match in matches:
        print(f"\n[2] Minting block for: {match['title']} ({match['page_url']})")
        new_block = ledger.Add_Block([match])
        print(f"    -> Block #{new_block.Height} created! Hash: {new_block.Block_Hash}")

        # 4. Demonstrate Cryptographic Re-Verification
        print("[3] Performing tamper-evident ledger verification...")
        is_valid = ledger.Verify_Block(new_block)
        print(f"    -> Ledger Verification Status: {'PASSED (Cryptographically Valid)' if is_valid else 'FAILED'}")

    # 5. Output Complete Chain Ledger
    print("\n[4] Complete Blockchain Ledger:")
    ledger.Print_Chain()

if __name__ == "__main__":
    run_pipeline("Test_Image.png")