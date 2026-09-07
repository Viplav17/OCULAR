# Visual Identity Verification & Cryptographic Blockchain Pipeline (HH Goa 2026 - Task 3)

An automated pipeline that extracts facial embeddings from an input scan, performs reverse visual discovery across web and social media platforms, and anchors confirmed matches into a tamper-evident, cryptographically verified blockchain ledger.

---

## 1. What the Project Does

The pipeline operates in three modular phases:

1. **Face Extraction & Vectorization:** The input image is parsed to isolate the primary face. Features are extracted into a 512-dimensional vector embedding using the ArcFace deep neural network architecture via MTCNN face alignment.
2. **Dynamic Reverse Search & Candidate Verification:** The face scan is submitted to Google Lens via SerpApi. Discovered candidates are dynamically retrieved, re-encoded using identical model parameters, and compared against the target vector using Cosine Distance. Only candidates meeting the similarity threshold are promoted. Global entity name resolution unifies valid human names across candidate metadata.
3. **Cryptographic Blockchain Ingestion & Verification:** Verified social matches (containing source URLs, profile metadata, and cryptographic image fingerprints) are organized into structured blocks. Each block is cryptographically linked to the previous block via SHA-256 header hashes and Merkle root calculations. Tamper-evidence is natively supported via the `Verify_Blockchain_File` method, which rebuilds the chain in memory and independently re-verifies block integrity against the exported JSON state.

---

## 2. Blockchain Architecture

This project implements a **Custom Local Cryptographic Blockchain**:

* **Blockchain Mechanics:** Begins with a deterministic Genesis Block (Height `0`, Previous Hash `0`*64). Subsequent blocks link strictly to the preceding block's header hash.
* **Merkle Integrity:** Block payloads (transaction data) are serialized with key ordering and hashed via double SHA-256 (`hash256`) to construct the Merkle root stored in the `BlockHeader`.
* **Tamper Verification:** The built-in `Verify_Block` and `Verify_Blockchain_File` methods recompute both the Merkle root from stored payload data and the Block Hash from header fields to prove immutability. Any modification to on-chain records invalidates the cryptographic proof.

---

## 3. Challenges & Engineering Solutions

* **Visual Noise & Background Matching:** Full-scene reverse searches frequently failed on cluttered backgrounds. Implemented targeted face detection and cropping in `Face_Extractor.py` before querying the search API to restrict reverse-search indexing to facial geometry.
* **Candidate Resolution Discrepancies:** Thumbnail resolutions from web candidates caused face detectors to fail when `enforce_detection=True`. Refined candidate processing to fall back on frame embeddings, preventing false negatives.
* **Object Graph Linking & Serialization:** Resolved class attribute reference errors across `Block`, `BlockHeader`, and `BlockChain` modules by establishing strict capitalization rules, and resolved JSON serialization failures by storing hashes and metadata instead of in-memory image pointers.


---

## 4. Installation & How to Run

### Prerequisites

* Python 3.10 to 3.12 (TensorFlow compatibility)
* A valid SerpApi token saved in your environment or configuration file (`Searching/API_tk.py`)

### Setup

```bash
# Clone the repository
git clone https://github.com/your-username/your-repo.git
cd your-repo

# Create and activate virtual environment
python -m venv venv
# On Windows:
.\venv\Scripts\activate
# On Unix/macOS:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

```

### How to Run the Application

Once your virtual environment is active and dependencies are installed, execute the interactive application entry point:

```bash
python Main.py

```

This will launch an interactive terminal menu featuring the following options:

1. **Scan a new image and build Blockchain:** Automatically processes the image in the Input_Image folder (containing your target input image), performs the facial vector extraction, queries SerpApi Google Lens, filters matches, resolves identities, and interactively guides you through minting blocks, viewing the chain, and exporting to `blockchain_output.json`.
2. **Verify an existing exported JSON Blockchain:** Automatically invokes the built-in Blockchain verification suite to parse `blockchain_output.json`, reconstruct the chain in memory, recompute Merkle roots and header hashes, and output cryptographic health status.
3. **Exit:** Cleanly terminates the program.
