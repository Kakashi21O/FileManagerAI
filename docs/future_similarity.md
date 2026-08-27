# Image & Content Similarity Architecture

This document describes the planned progression for similarity analysis in FileManagerAI.

---

## Active in Current Version

### Level 1: Exact Content Hash & Metadata
- **Algorithm**: Cryptographic SHA-256 with chunked streaming ($O(B)$ time, $O(1)$ memory).
- **Scope**: Detects 100% byte-for-byte identical files regardless of file names or dates.
- **Action**: Candidate duplicates are flagged and queued for human-reviewed relocation to `_FileManagerAI_Review/Duplicates/`. No automatic deletion is ever performed.

---

## Future Levels (Documented Only — Not Implemented)

### Level 2: Perceptual Hashing (pHash / dHash / aHash)
- **Concept**: Downscales images, computes DCT (Discrete Cosine Transform) or gradient gradients to produce compact bit-hashes.
- **Application**: Identifies resized, mildly re-compressed, or watermarked image variations.
- **Safety Policy**: Hamming distance matches with $\le 5$ bits difference flagged as **Possible Similar** with high confidence ($90\%+$), requiring explicit human review.

### Level 3: Visual & Structural Feature Extraction
- **Concept**: Color histograms, edge orientation histograms, or keypoint matching (ORB/SIFT).
- **Application**: Detects cropped, rotated, or color-adjusted images.
- **Safety Policy**: Classified under `_FileManagerAI_Review/Similar/` with similarity score for manual inspection.

### Level 4: Deep Learning / Embedding-Based Similarity
- **Concept**: Vision models (e.g. CLIP / MobileNet) or Sentence Transformers for semantic content similarity.
- **Application**: Cluster photos by subject or conceptual equivalence.
- **Safety Policy**: Requires high threshold confidence. Never moves files automatically without an interactive user confirmation stage.
