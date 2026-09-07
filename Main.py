import os, logging, sys, json

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'

logging.getLogger("tensorflow").setLevel(logging.ERROR)
logging.getLogger("tf_keras").setLevel(logging.ERROR)

from Searching.Search import Search
from Blockchain.Backend.Core.BlockChain import BlockChain
from Blockchain.Backend.util.util import hash256

def quiet_unraisable_hook(unraisable):
    """
    Intercepts background garbage collection exceptions.
    Silently drops lz4 closed file I/O errors to keep the terminal clean
    while allowing legitimate unhandled exceptions to print normally.
    """
    if issubclass(unraisable.exc_type, ValueError) and "I/O operation on closed file" in str(unraisable.exc_value):
        return  
    sys.__unraisablehook__(unraisable)  

sys.unraisablehook = quiet_unraisable_hook

def run_pipeline(input_image: str):
    """
    Executes the end-to-end identity verification pipeline.
    
    1. Initializes the Blockchain ledger and generates the foundational Genesis block.
    2. Runs face detection on the input image, queries Google Lens/Knowledge Graph, and searches for matching identities online.
    3. Displays explicit person identification if recognized.
    4. Iterates over valid matches and mints a new cryptographic block for each record.
    5. Automatically runs a tamper-evident ledger verification check on newly minted blocks.
    6. Prints the full structured blockchain ledger to standard output.
    7. Formats and exports the entire blockchain state into a local 'blockchain_output.json' file.
    """
    print("=== HH GOA 2026: Identity Verification Pipeline ===")
    
    BC = BlockChain()
    print(f"[0] Blockchain initialized (Genesis Hash: {BC.chain[0].Block_Hash[:16]}...)")

    print(f"[1] Searching web matches for {input_image}...")
    matches, identified_person = Search(input_image)

    if not matches:
        print("[!] No confident facial matches found online.")
        return

    # --- STATIC NAME UNIFICATION LOGIC ---
    static_name = "Identity Not Explicitly Named"
    
    # 1. Prioritize Google's Explicit Knowledge Graph Name
    if identified_person and identified_person != "Unknown":
        static_name = identified_person
    else:
        # 2. Scan all matches for a valid fallback name
        for match in matches:
            name = match.get("identified_name", "")
            if name not in ["Identity Not Explicitly Named", "Unknown", "No Title"]:
                static_name = name
                break  # Stop looking once we find the first valid name

    # 3. Force EVERY block in the ledger to use this static name
    for match in matches:
        match["identified_name"] = static_name

    # 4. Print the final unified identity to the terminal
    if static_name != "Identity Not Explicitly Named":
        print(f"    [+] GLOBAL ENTITY RECOGNIZED: '{static_name}' (Applied to all blocks)")
    else:
        print("    [-] Identity not explicitly named. Proceeding with unnamed visual matches.")
    # -------------------------------------

    print(f"\n[+] Found {len(matches)} valid match(es). Proceeding to mint blocks...")

    step = 2
    for match in matches:
        # The line `match = identified_person + match` has been removed to fix the TypeError. 
        # The dictionary is already updated with the static name in the loop above.
        print(f"\n[{step}] Minting block for: {match['title']} ({match['page_url']})")
        new_block = BC.Add_Block([match])
        print(f"    -> Block #{new_block.Height} created! Hash: {new_block.Block_Hash}")
        step += 1

        print(f"[{step}] Performing tamper-evident ledger verification...")
        is_valid = BC.Verify_Block(new_block)
        print(f"    -> Ledger Verification Status: {'PASSED (Cryptographically Valid)' if is_valid else 'FAILED'}")
        step += 1

    print(f"\n[{step}] Complete Blockchain Ledger:")
    BC.Print_Chain()
    step += 1

    print(f"\n[{step}] Exporting Blockchain to 'blockchain_output.json'...")
    chain_data = []
    for block in BC.chain:
        chain_data.append({
            "Height": block.Height,
            "Block_Hash": block.Block_Hash,
            "Previous_Hash": block.BlockHeader.PrevBlockHash,
            "Timestamp": block.BlockHeader.TimeStamp,
            "Data": block.Data
        })
        
    with open("blockchain_output.json", "w") as f:
        json.dump(chain_data, f, indent=4)
    print("    -> Export successful!")

if __name__ == "__main__":
    run_pipeline("Test_Image.png")