# Second-folder recovery note (candidate checkpoint fingerprint)

**Evidence level: unverified one-page summary, not recovered model bytes.**

Source: `掃描檔案含pth的.pdf`; SHA-256 `2472a344f79019e84e9d93e511d7623c8debd58dbf4d53f3d9b3afc4ec94ae7c`. The PDF's own line headed `SHA-256:` contains **no value** for the alleged `.pth`. Its name, size, modification time and bytes are not in this submission. Preserve the real file if found; do not manufacture a checkpoint.

## New checkpoint lead

The note identifies an **Attention ResUNet candidate** with base channels 50, progressive 100/200/400, residual and attention modules, and nine specific key/shape pairs in `pth_candidate_fingerprint.json`. This materially narrows the search compared with the earlier estimated 32/64/128/256 U-Net architecture. The purported ~4.87M parameters is a claim from the note, not calculated from nine incomplete tensors. `outc.weight=[1,50,1,1]` only proves a one-channel head in the candidate; it does **not** prove this is the paper's joint bitmap/quantization generator.

**Do not overwrite** `recovered_note_profile.json` or `architecture_scaffold.py`. Both remain useful as a separate, earlier candidate. A partial shape fingerprint is not sufficient to reconstruct missing code, model topology, training history or published metrics.

## Check any actual `.pth` found on the old PC

1. Copy and preserve the original bytes, location, dates and SHA-256.
2. Default metadata-only inspection (does not unpickle):

```
python3 recovery/checkpoint_fingerprint.py --checkpoint /trusted/path/model.pth --out recovery/local_candidate_metadata.json
```

3. Only after you personally trust the file's origin, use explicitly opt-in `weights_only=True` tensor inspection:

```
python3 recovery/checkpoint_fingerprint.py --checkpoint /trusted/path/model.pth --trusted-weights-only --out recovery/local_candidate_shapes.json
```

It compares all nine exact key/shape fingerprints and reports number of matches. Torch `weights_only=True` reduces code-execution exposure but is not an absolute security guarantee. Do not run unknown full-model pickle loaders. Keep actual weights, checkpoints, full-drive inventories and raw BOSSbase images outside the public GitHub release until provenance, authorization and sharing rights are reviewed.

## Dataset split lead

The one-page note mentions **256×256** preprocessing and four random states (42, 0, 123, 2025), plus three alternatives: 5000/5000, 4000 train + 1000 held-out remainder + 5000 test, and 8000/2000. The article's main experiment says **512×512 and 5000 held-out BOSSbase test images**. This means the 8000/2000 scheme cannot be silently treated as the article's main test protocol; the 256 and 512 resolutions also need version provenance.

The optional `create_candidate_splits.py` produces only **NEW_CANDIDATE_NOT_HISTORICAL_SPLIT** manifests. Without the original ordered list of image IDs and exact preprocessing, a random seed alone cannot recover the old split:

```
python3 recovery/create_candidate_splits.py --boss-manifest /local/BOSSbase_ordered_IDs.txt --seed 42 --scheme half --out-dir /local/candidate_half_seed42
```

No images, weights or invented experimental results are bundled. Neither candidate split nor candidate architecture is evidence for Tables 4/5/10/11.
