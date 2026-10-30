# Enzo–ABYSS run 11486 logs and initial parameter file

Source: /home/wispedia/AA/isolated/runs/run3-abyss-noFEWBODY on happiness2.
Only DD0000/DD0000 (the parameter file) is included, not the complete checkpoint. The original files remain untouched. Compressed archives larger than 90 MiB are split to fit GitHub file limits.

Reconstruct and extract from this directory:

```bash
cat stderr.11486.happiness2-00.gz.part* > stderr.11486.happiness2-00.gz
gzip -dk stdout.11486.happiness2-00.gz
gzip -dk stderr.11486.happiness2-00.gz
```

Verify tracked payloads before reconstruction with `sha256sum -c SHA256SUMS`.
