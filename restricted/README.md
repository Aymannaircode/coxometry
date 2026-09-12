# Restricted linkage — EMPTY / NO REAL IDENTITIES

**HIGHLY SENSITIVE when later populated. Currently empty.**

This tree holds the **future** identity-linkage store required by Phase 11B §7.
It is **outside** every training dataset and **outside** `collection/03_DEIDENTIFIED`
through `collection/08_VALIDATED`.

**Never place this mapping in a future training dataset.**

**Allowed later (not now)**

- Mapping needed for legal/clinical trace-back
- Duplicate detection against hospital identity
- HMAC secret **location policy** (secret itself must not live beside YOLO images)

**Forbidden in this tree today**

- Real PatientName / PatientID / DOB / address / phone
- Copying Step D `candidate_inventory.csv` / `selected_cases.csv` / R26 `worklist.csv`
- Any `R27_*` case

**Forbidden forever in ML / training metadata**

- PatientName
- Hospital PatientID
- Full date of birth
- Address, phone, administrative numbers
- Real identity

Training-side key, when later computed: irreversible `patient_pseudonym` only.

Authoritative protocol: `datasets/yolo_pose_new_26/phase11c1_collection_infrastructure.md`
