from Blockchain.Backend.Core.Block import Block
from Blockchain.Backend.Core.BlockHeader import BlockHeader
from Blockchain.Backend.util.util import hash256
import time
import json as js
import os

ZERO_HASH = "0" * 64

class BlockChain:
    def __init__(self):
        self.chain = [self.Genesis_Block()]

    def Genesis_Block(self):
        Gen_Block_Head = BlockHeader(
            0,
            ZERO_HASH,
            ZERO_HASH,
            0,
            time.time()
            )
        
        Gen_Block = Block(
            0,
            0,
            Gen_Block_Head
            )
        
        return Gen_Block

    def Add_Block(self, data: list):
        prev_block = self.chain[-1]
        prev_hash = prev_block.Block_Hash

        Encoded_data = js.dumps(data, sort_keys=True)
        merkle_root = hash256(Encoded_data).hex()

        Block_Header = BlockHeader(
            1,
            prev_hash,
            merkle_root,
            0,
            time.time()
            )
        
        New_Block = Block(
            len(self.chain),
            len(Encoded_data),
            Block_Header,
            data
            )

        self.chain.append(New_Block)
        return New_Block

    def Verify_Block(self, Block):
        if Block.Height == 0:
            return Block.BlockHeader.PrevBlockHash == ZERO_HASH

        Prev_Block = self.chain[Block.Height - 1]

        if Block.BlockHeader.PrevBlockHash != Prev_Block.Block_Hash:
            return False

        block_encoded_data = js.dumps(Block.Data, sort_keys=True)
        block_merkle_root = hash256(block_encoded_data).hex()

        if Block.BlockHeader.merkleroot != block_merkle_root:
            return False

        if Block.Block_Hash != Block.BlockHeader.To_Hash():
            return False

        return True

    def Print_Chain(self):  
        for Block in self.chain:
            print(f"\n--- Block {Block.Height} ---")
            print(js.dumps(Block.Data, indent=4, sort_keys=True))

    def Verify_Ledger_File(self, filepath="blockchain_output.json"):
        """Reads a JSON ledger, reconstructs the chain in memory, and verifies integrity."""
        if not os.path.exists(filepath):
            print(f"[-] FAILED: '{filepath}' does not exist.")
            return False

        with open(filepath, "r") as f:
            try:
                ledger = js.load(f)
            except js.JSONDecodeError:
                print(f"[-] FAILED: '{filepath}' contains invalid JSON.")
                return False

        if not ledger:
            print("[-] FAILED: Ledger is empty.")
            return False

        self.chain = []

        print(f"[*] Reconstructing and verifying {len(ledger)} blocks from {filepath}...")

        for i, json_block in enumerate(ledger):
            data_payload = json_block["Data"]
            encoded_data = js.dumps(data_payload, sort_keys=True)
            merkle_root = hash256(encoded_data).hex() if i > 0 else ZERO_HASH

            header = BlockHeader(
                Version=0 if i == 0 else 1,
                PrevBlockHash=json_block["Previous_Hash"],
                merkleroot=merkle_root,
                bits=0,
                TimeStamp=json_block["Timestamp"]
            )

            reconstructed_block = Block(
                Height=json_block["Height"],
                Blocksize=len(encoded_data) if i > 0 else 0,
                BlockHeader=header,
                Data=data_payload
            )
            
            reconstructed_block.Block_Hash = json_block["Block_Hash"]

            self.chain.append(reconstructed_block)

            if not self.Verify_Block(reconstructed_block):
                print(f"    [-] TAMPER DETECTED: Cryptographic failure at Block #{reconstructed_block.Height}!")
                return False

        print("    [+] LEDGER VERIFIED: All cryptographic links and payloads are mathematically intact.")
        return True