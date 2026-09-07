import os, logging, sys, json, time

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'

logging.getLogger("tensorflow").setLevel(logging.ERROR)
logging.getLogger("tf_keras").setLevel(logging.ERROR)

from Searching.Search import Search
from Blockchain.Backend.Core.BlockChain import BlockChain
from Blockchain.Backend.util.util import hash256

def delay_print(message: str = "", delay: float = 0.5):
    """Prints a message followed by a brief pause to maintain clean output pacing."""
    print(message)
    time.sleep(delay)

def quiet_unraisable_hook(unraisable):
    if issubclass(unraisable.exc_type, ValueError) and "I/O operation on closed file" in str(unraisable.exc_value):
        return  
    sys.__unraisablehook__(unraisable)  

sys.unraisablehook = quiet_unraisable_hook

def looks_like_human_name(name_str):
    if not name_str or name_str in ["Unknown", "No Title", "Identity Not Explicitly Named"]:
        return False
    words = name_str.strip().split()
    if len(words) > 3 or len(words) == 0:
        return False
    if not all(word[0].isupper() for word in words if word.isalpha()):
        return False
    return True

def get_input_image_path(folder_name="Input_Image"):
    """Dynamically scans the Input_Image folder for any supported image file."""
    if not os.path.exists(folder_name):
        return None
    
    supported_extensions = ('.png', '.jpg', '.jpeg')
    for file in os.listdir(folder_name):
        if file.lower().endswith(supported_extensions):
            return os.path.join(folder_name, file)
    return None

def run_pipeline(input_image: str):
    delay_print("\n[1] Initializing Blockchain...", 0.6)
    BC = BlockChain()
    delay_print(f"    -> Genesis Block created (Hash: {BC.chain[0].Block_Hash[:16]}...)", 0.6)
    
    input("\n[?] Press Enter to begin facial extraction and web search...")

    delay_print(f"\n[2] Searching web matches for {input_image}...", 0.8)
    matches, identified_person = Search(input_image)

    if not matches:
        delay_print("[!] No confident facial matches found online.", 0.5)
        return

    static_name = "Identity Not Explicitly Named"
    if looks_like_human_name(identified_person):
        static_name = identified_person
    else:
        for match in matches:
            name = match.get("identified_name", "")
            if looks_like_human_name(name):
                static_name = name
                break 

    for match in matches:
        match["identified_name"] = static_name

    if static_name != "Identity Not Explicitly Named":
        delay_print(f"    [+] GLOBAL ENTITY RECOGNIZED: '{static_name}' (Applied to all blocks)", 0.7)
    else:
        delay_print("    [-] Identity not explicitly named. Proceeding with unnamed visual matches.", 0.6)

    delay_print(f"    [+] Found {len(matches)} valid match(es).", 0.6)
    
    mint_choice = input(f"\n[?] Ready to mint {len(matches)} blocks to the blockchain. Proceed? (y/n): ")
    if mint_choice.lower() != 'y':
        delay_print("Operation cancelled by user.", 0.4)
        return

    step = 3
    for match in matches:
        print(f"\n[{step}] Minting block for: {match['title'][:50]}...")
        new_block = BC.Add_Block([match])
        print(f"    -> Block #{new_block.Height} created! Hash: {new_block.Block_Hash}")
        
        is_valid = BC.Verify_Block(new_block)
        print(f"    -> Blockchain Verification Status: {'PASSED (Valid)' if is_valid else 'FAILED'}")
        step += 1

    delay_print("\n[+] All matches successfully minted.", 0.6)
    
    print_choice = input("\n[?] Do you want to print the complete blockchain Blockchain to the terminal? (y/n): ")
    if print_choice.lower() == 'y':
        delay_print("\n--- Complete Blockchain Blockchain ---", 0.5)
        BC.Print_Chain()

    export_choice = input("\n[?] Do you want to export the blockchain to 'blockchain_output.json'? (y/n): ")
    if export_choice.lower() == 'y':
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
        delay_print("    -> Export successful!", 0.5)
    
    delay_print("\n[✓] Pipeline execution finished.", 0.6)

def main_menu():
    while True:
        delay_print("\n=== HH GOA 2026: Identity Verification Pipeline ===", 0.3)
        print("1. Scan a new image and build blockchain")
        print("2. Verify an existing exported JSON blockchain")
        print("3. Exit")
        
        choice = input("Select an option (1-3): ")
        
        if choice == '1':
            target_image = get_input_image_path("Input_Image")
            if not target_image:
                delay_print("\n[!] Error: No image file (.png, .jpg, .jpeg) found inside the 'Input_Image' folder.", 0.5)
            else:
                delay_print(f"\n[+] Target image located: {target_image}", 0.4)
                run_pipeline(target_image)
        elif choice == '2':
            delay_print("\n=== BLOCKCHAIN INTEGRITY VERIFICATION SUITE ===", 0.3)
            verifier = BlockChain()
            # Ensure this matches your method name inside BlockChain class (e.g., Verify_Blockchain_File)
            verifier.Verify_Blockchain_File("blockchain_output.json")
        elif choice == '3':
            delay_print("Exiting...", 0.3)
            sys.exit(0)
        else:
            delay_print("Invalid selection. Please enter 1, 2, or 3.", 0.4)

if __name__ == "__main__":
    main_menu()