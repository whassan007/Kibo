# Production Rollback & Disaster Recovery Runbook (`v2026.10.2` -> `v2026.10.1`)

## 1. Immutable Baseline Preservation

- **Baseline Tag**: `v2026.10.1`
- **Immutable Commit SHA**: `e2147b3ec4cc5c6848d2698145f9830d1ae47c20`
- **Guarantee**: Tag `v2026.10.1` has **never** been overwritten, moved, or retagged during the Enterprise Hardening v2 program.

Verify baseline tag integrity at any time:
```bash
git rev-parse v2026.10.1^{commit}
# Expected output: e2147b3ec4cc5c6848d2698145f9830d1ae47c20
```

---

## 2. Pre-Cutover Snapshot Procedure

Before cutting over to the hardened release (`v2026.10.2` / `hardening/v2026.10.1/integration`), create a cryptographically verified backup bundle using [`.kibo/tools/backup_restore.py`](file:///Users/wael/Code/iCloudCode/kibo.is/.kibo/tools/backup_restore.py):

```bash
python3 .kibo/tools/backup_restore.py backup \
  --db-path kibo-is/kibo_state.db \
  --output-dir backups/pre-v2026.10.2
```

This creates a timestamped archive and `manifest.json` containing SHA-256 digests of `kibo_state.db` and the regulatory document store.

---

## 3. Application & Container Rollback Procedure

If an operational anomaly occurs post-deployment:

### Step 1: Stop Active Services
```bash
docker compose down
```

### Step 2: Restore Verified Database & Document Store Snapshot
```bash
python3 .kibo/tools/backup_restore.py restore \
  --bundle-dir backups/pre-v2026.10.2 \
  --target-db-path kibo-is/kibo_state.db
```
`backup_restore.py` verifies the SHA-256 digest of every file in `manifest.json` before overwriting target state and refuses to restore corrupted archives.

### Step 3: Revert Codebase to Immutable Tag `v2026.10.1`
```bash
git checkout v2026.10.1
```

### Step 4: Rebuild & Restart Baseline Containers
```bash
cd kibo-is && npm run build && cd ..
docker compose up -d --build
```

---

## 4. Quarantine Reversal Note (`commissioner_verdicts`)

Note that in `v2026.10.1`, `kibo-is/kibo_state.db` contained 62 LLM-fabricated rows (`verdict-auto-*`) in `commissioner_verdicts`. In `v2026.10.2`, those 62 rows were preserved intact inside `quarantined_commissioner_verdicts` with `quarantine_reason` and `quarantined_at` timestamps. No historical database records were deleted, ensuring zero audit evidence loss during either forward migration or rollback.
