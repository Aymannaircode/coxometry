#!/usr/bin/env python3
"""Planification V4 (new_26) — lecture seule, aucun entraînement.

Produit datasets/yolo_pose_new_26/v4_plan.md à partir des audits V2/V3 existants.
Ne modifie ni V2, ni V3, ni labels, ni annotations.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
OUTPUT_MD = PROJECT_ROOT / "datasets" / "yolo_pose_new_26" / "v4_plan.md"

# Baseline officielle V2
V2_RUN = PROJECT_ROOT / "runs" / "pose" / "runs" / "pose" / "runs" / "yolo_pose_new_26_v2-3"
V2_BEST = V2_RUN / "weights" / "best.pt"
V2_BEST_EPOCH = 80
V2_BEST_MAP = 0.692
V2_FINAL_MAP = 0.646

# Métriques pixel-level V2 (train_vs_val + landmark analysis)
V2_BASELINE_PX = {
    "ASL_L_train": 538.18,
    "ASL_L_val": 471.72,
    "ASL_R_train": 142.86,
    "ASL_R_val": 147.73,
    "ASM_L_train": 77.59,
    "ASM_L_val": 80.94,
    "ASM_R_train": 96.81,
    "ASM_R_val": 81.32,
    "FHC_L_train": 52.49,
    "FHC_L_val": 80.94,
    "FNM_L_train": 52.78,
    "FNM_L_val": 81.05,
    "detections": "26/26",
}

# Échec V3
V3_RUN = PROJECT_ROOT / "runs" / "pose" / "yolo_pose_new_26_v3"
V3_DIAGNOSIS = "A"
V3_BEST_EPOCH = 89
V3_BEST_MAP = 0.039
V3_FINAL_MAP = 0.010

DATA_YAML = PROJECT_ROOT / "datasets" / "yolo_pose_new_26" / "data.yaml"
FLIP_IDX = [1, 0, 3, 2, 5, 4, 7, 6, 9, 8, 11, 10, 13, 12]
KEYPOINT_NAMES = [
    "TD_R", "TD_L", "FHC_R", "FHC_L", "ASL_R", "ASL_L",
    "ASM_R", "ASM_L", "FNM_R", "FNM_L", "FSP_R", "FSP_L", "FSD_R", "FSD_L",
]

# Proposition V4 conservative (plan uniquement — non exécuté)
V4_PROPOSED = {
    "run_dir": "runs/pose/yolo_pose_new_26_v4",
    "init_checkpoint": "copie read-only de V2 best.pt (epoch 80 mAP peak)",
    "data": "datasets/yolo_pose_new_26/data.yaml",
    "epochs_max": 30,
    "patience": 10,
    "imgsz": 640,
    "batch": 2,
    "device": "cpu",
    "optimizer": "AdamW",
    "lr0": 0.0001,
    "lrf": 0.01,
    "warmup_epochs": 1.0,
    "cos_lr": True,
    "mosaic": 0.2,
    "auto_augment": None,
    "erasing": 0.0,
    "fliplr": 0.5,
    "pretrained": False,
    "freeze": None,
    "pose_loss_gain": 12.0,
}

# Seuils GO/NO-GO
GO_NO_GO = {
    "asl_l_improve_train_pct": 20.0,
    "asl_l_improve_val_pct": 20.0,
    "other_landmark_max_degrade_pct": 25.0,
    "min_detections": 26,
    "max_map_regression_vs_v2": 0.05,
    "epoch1_landmark_catastrophic_degrade_pct": 25.0,
}


def load_split_counts() -> tuple[int, int]:
    split_path = PROJECT_ROOT / "datasets" / "yolo_pose_new_26" / "meta" / "split.json"
    if not split_path.is_file():
        return 21, 5
    data = json.loads(split_path.read_text(encoding="utf-8"))
    return len(data.get("train", [])), len(data.get("val", []))


def write_plan() -> None:
    now = datetime.now(timezone.utc).isoformat()
    n_train, n_val = load_split_counts()

    lines = [
        "# Plan V4 — fine-tuning doux depuis V2 (new_26)",
        "",
        f"**Généré :** {now}",
        "**Statut :** planification uniquement — **aucun entraînement lancé**",
        "**Baseline officielle :** V2 (`runs/pose/runs/pose/runs/yolo_pose_new_26_v2-3/`)",
        "",
        "---",
        "",
        "## 1. Baseline officielle — V2",
        "",
        "V2 reste le modèle de référence pour toute décision clinique ou technique.",
        "",
        "| Métrique | Valeur |",
        "|----------|--------|",
        f"| Checkpoint | `{V2_BEST.relative_to(PROJECT_ROOT).as_posix()}` |",
        f"| Meilleur epoch (mAP50-95 pose) | **{V2_BEST_EPOCH}** |",
        f"| mAP50-95(P) best | **{V2_BEST_MAP:.3f}** |",
        f"| mAP50-95(P) final (epoch 100) | {V2_FINAL_MAP:.3f} |",
        f"| ASL_L train / val | **{V2_BASELINE_PX['ASL_L_train']:.2f}** / **{V2_BASELINE_PX['ASL_L_val']:.2f}** px |",
        f"| ASL_R train / val | {V2_BASELINE_PX['ASL_R_train']:.2f} / {V2_BASELINE_PX['ASL_R_val']:.2f} px |",
        f"| ASM_L train / val | {V2_BASELINE_PX['ASM_L_train']:.2f} / {V2_BASELINE_PX['ASM_L_val']:.2f} px |",
        f"| Détections 26 cas | {V2_BASELINE_PX['detections']} |",
        f"| Dataset train / val | {n_train} / {n_val} images |",
        "",
        "**Problème connu V2 :** ASL_L sous-appris (~538 px train) malgré labels et mapping corrects.",
        "Tous les autres audits (géométrie, mapping, flip, couverture) sont **OK**.",
        "",
        "---",
        "",
        "## 2. Échec V3 — synthèse",
        "",
        "| Métrique | V3 | vs V2 |",
        "|----------|-----|-------|",
        f"| Diagnostic régression | **{V3_DIAGNOSIS}** (init OK, fine-tuning destructeur) | — |",
        f"| mAP50-95(P) best (epoch {V3_BEST_EPOCH}) | {V3_BEST_MAP:.3f} | −{(V2_BEST_MAP - V3_BEST_MAP):.3f} |",
        f"| mAP50-95(P) final | {V3_FINAL_MAP:.3f} | −{(V2_FINAL_MAP - V3_FINAL_MAP):.3f} |",
        "| ASL_L train / val | 584 / 579 px | **pire** |",
        "| ASL_R train | 952 px | **effondrement global** |",
        "| ASM_L train | 615 px | **effondrement global** |",
        "| Détections | 25/26 (B26_10 absent) | régression |",
        "",
        f"Run V3 conservé (non supprimé) : `{V3_RUN.relative_to(PROJECT_ROOT).as_posix()}/`",
        "",
        "---",
        "",
        "## 3. Hypothèse principale",
        "",
        "**Fine-tuning trop agressif** (verdict audit V3 = A), et non :",
        "",
        "- erreur de checkpoint (init bit-identique à V2) ;",
        "- inversion flip_idx (audit flip = D) ;",
        "- labels / mapping incorrects (audits OK).",
        "",
        "Facteurs identifiés :",
        "",
        "1. **lr0 = 0.01** + AdamW auto (~0.002) — schedule « entraînement neuf » sur modèle convergé ;",
        "2. **mosaic 1.0 → 0.0** — choc d'augmentation dès epoch 1 ;",
        "3. **100 epochs** — sur-apprentissage / dérive prolongée ;",
        "4. **pretrained=false** — sémantique Ultralytics inadaptée au fine-tuning ;",
        "5. mAP agrégé masque l'échec ASL_L — validation pixel-level obligatoire.",
        "",
        "---",
        "",
        "## 4. Expérience V4 proposée — fine-tuning doux",
        "",
        "### Objectif",
        "",
        "Améliorer **ASL_L** (priorité) sans dégrader les 13 autres landmarks ni la géométrie,",
        "en partant du **V2 best.pt** (pic mAP epoch 80).",
        "",
        "### Init (lecture seule sur V2)",
        "",
        f"- Source : `{V2_BEST.relative_to(PROJECT_ROOT).as_posix()}`",
        f"- Copie init V4 : `{V4_PROPOSED['run_dir']}/init/v2_best_mAP_epoch80.pt`",
        "- **Ne jamais modifier** le run V2 ni ses poids.",
        "",
        "### Architecture & dataset (inchangés)",
        "",
        f"- **14 keypoints** : {', '.join(KEYPOINT_NAMES)}",
        f"- **kpt_shape** : `[14, 3]`",
        f"- **flip_idx** : `{FLIP_IDX}` (validé par audit horizontal flip)",
        f"- **data** : `{V4_PROPOSED['data']}`",
        f"- **fliplr** : {V4_PROPOSED['fliplr']}",
        "",
        "### Hyperparamètres conservateurs proposés",
        "",
        "| Param | V2 | V3 (échec) | **V4 proposé** | Rationale |",
        "|-------|----|------------|----------------|-----------|",
        f"| lr0 | 0.01 | 0.01 | **{V4_PROPOSED['lr0']}** | ×100 plus bas — fine-tuning doux |",
        f"| lrf | 0.01 | 0.01 | {V4_PROPOSED['lrf']} | decay final |",
        f"| optimizer | auto | auto | **{V4_PROPOSED['optimizer']}** | explicite, lr contrôlé |",
        f"| warmup_epochs | 3 | 3 | **{V4_PROPOSED['warmup_epochs']}** | warmup minimal |",
        f"| cos_lr | false | false | **{V4_PROPOSED['cos_lr']}** | decay doux |",
        f"| epochs | 100 | 100 | **{V4_PROPOSED['epochs_max']}** | limiter la dérive |",
        f"| patience | 100 | 25 | **{V4_PROPOSED['patience']}** | early stop si plateau |",
        f"| mosaic | 1.0 | 0.0 | **{V4_PROPOSED['mosaic']}** | réduction progressive, pas coupure brutale |",
        f"| auto_augment | randaugment | null | **null** | éviter bruit sur 21 images |",
        f"| erasing | 0.4 | 0.0 | **0.0** | idem |",
        f"| fliplr | 0.5 | 0.5 | **0.5** | conservé (flip_idx validé) |",
        f"| imgsz / batch | 640 / 2 | 640 / 2 | **640 / 2** | identique V2 |",
        f"| pose (loss gain) | 12.0 | 12.0 | **{V4_PROPOSED['pose_loss_gain']}** | inchangé initialement |",
        "",
        "### Garde-fous pendant l'entraînement (implémentés dans `train_yolo_pose_v4_new_26.py`)",
        "",
        "1. **Epoch 0 = checkpoint V2 best.pt** (copie init read-only) ;",
        "2. **Validation epoch 0** : inférence sur 26 cas — les labels doivent correspondre à V2 (`predictions_v2/`) ;",
        "3. **Après epoch 1** : comparaison pixel-level des 14 landmarks vs epoch 0 (pas vs mAP) ;",
        f"   - **Abandon** si dérive catastrophique : ≥1 landmark focus (ASL_R, ASM_L, ASM_R, FHC_L, FHC_R) "
        f"dégradé de >{GO_NO_GO['epoch1_landmark_catastrophic_degrade_pct']:.0f} % vs epoch 0 sur train ;",
        "   - mAP50-95(P) reste **secondaire** pour ce garde-fou ;",
        "4. Sauvegarder `results.csv` + best.pt dans `runs/pose/yolo_pose_new_26_v4/` ;",
        "5. **Ne pas écraser V2 ni V3.**",
        "",
        "---",
        "",
        "## 5. Critères GO / NO-GO (obligatoires post-entraînement)",
        "",
        "La décision **GO** (remplacer V2 par V4) exige **toutes** les conditions suivantes :",
        "",
        "### 5.1 Pixel-level — 14 landmarks (priorité absolue)",
        "",
        "Scripts : `compare_v2_v4_landmarks_new_26.py`, `test_v4_geometry_new_26.py`.",
        "",
        "| Critère | Seuil | Baseline V2 |",
        "|---------|-------|-------------|",
        f"| ASL_L train mean | baisse ≥ **{GO_NO_GO['asl_l_improve_train_pct']:.0f} %** | {V2_BASELINE_PX['ASL_L_train']:.2f} px |",
        f"| ASL_L val mean | baisse ≥ **{GO_NO_GO['asl_l_improve_val_pct']:.0f} %** | {V2_BASELINE_PX['ASL_L_val']:.2f} px |",
        f"| Autres 13 landmarks (train+val mean) | dégradation ≤ **{GO_NO_GO['other_landmark_max_degrade_pct']:.0f} %** chacun | voir V2 landmark analysis |",
        f"| Détections | **{GO_NO_GO['min_detections']}/26** | {V2_BASELINE_PX['detections']} |",
        "",
        "**NO-GO immédiat** si :",
        "",
        "- ASL_L ne baisse pas de ≥20 % sur train **et** val ;",
        "- ASL_R, ASM_L, ASM_R, FHC_L ou FHC_R augmente de >25 % ;",
        "- moins de 26 détections ;",
        "- un landmark médian > 300 px alors que V2 < 200 px.",
        "",
        "### 5.2 Géométrie — VCE / Tönnis / CCD",
        "",
        "Scripts : `test_v4_geometry_new_26.py` + comparaison vs `v2_geometry_results.csv`.",
        "",
        "| Critère | Seuil NO-GO | V2 référence |",
        "|---------|-------------|--------------|",
        "| VCE_L négatifs | ≤ V2 (21/26) ou amélioration | 21/26 |",
        "| Tönnis_L extrêmes | ≤ V2 (6/26) ou amélioration | 6/26 |",
        "| CCD_L / CCD_R | pas de dérive > 20° vs V2 en médiane | — |",
        "",
        "### 5.3 mAP (secondaire — ne pas décider sur mAP seul)",
        "",
        f"- mAP50-95(P) V4 ≥ V2 best − {GO_NO_GO['max_map_regression_vs_v2']:.2f} "
        f"(≥ {V2_BEST_MAP - GO_NO_GO['max_map_regression_vs_v2']:.3f}) — **informatif seulement** ;",
        "- un bon mAP avec ASL_L dégradé = **NO-GO** (leçon V2/V3).",
        "",
        "### 5.4 Verdict final",
        "",
        "| Résultat | Action |",
        "|----------|--------|",
        "| **GO** | V4 devient candidate ; revue manuelle des pires cas ASL_L |",
        "| **NO-GO** | Conserver V2 ; archiver V4 ; documenter |",
        "| **PARTIEL** | ASL_L ↓ mais autre landmark ↓ → NO-GO, analyser |",
        "",
        "---",
        "",
        "## 6. Pipeline post-V4 (à exécuter après entraînement futur)",
        "",
        "Ordre strict :",
        "",
        "1. `train_yolo_pose_v4_new_26.py` — fine-tuning doux (future) ;",
        "2. `run_yolo_pose_inference_v4_new_26.py` — 26 DICOM → `predictions_v4/` ;",
        "3. `test_v4_geometry_new_26.py` — VCE/Tönnis/CCD ;",
        "4. `compare_v2_v4_landmarks_new_26.py` — 14 landmarks train/val ;",
        "5. Rapport GO/NO-GO automatique → `v4_vs_v2_decision.md`.",
        "",
        "---",
        "",
        "## 7. Risques résiduels",
        "",
        "- **21 images train** — variance élevée, un run peut échouer par hasard ;",
        "- ASL_L peut rester difficile même avec LR bas (landmark intrinsèquement dur) ;",
        "- mosaic=0.2 est un compromis conservateur — ajuster si epoch 1 stable mais ASL_L stagnant ;",
        "- Envisager à terme : plus de données, focal loss keypoint, ou callback px/keypoint.",
        "",
        "---",
        "",
        "## 8. Fichiers de référence (lecture seule)",
        "",
        "| Document | Contenu |",
        "|----------|---------|",
        "| `v3_regression_audit.md` | Verdict A, init V2 vérifié |",
        "| `v3_vs_v2_landmark_comparison.md` | Pixel-level V2 vs V3 |",
        "| `train_vs_val_landmark_analysis.md` | ASL_L train/val V2 |",
        "| `horizontal_flip_audit.md` | flip_idx validé |",
        "| `v2_training_behavior.md` | Courbes V2, epoch 80 best |",
        "",
        "---",
        "",
        "## 9. Commande de regénération de ce plan",
        "",
        "```bash",
        ".venv\\Scripts\\python.exe annotation_pilot\\scripts\\prepare_v4_plan_new_26.py",
        "```",
        "",
        "**TRAINING: NOT RUN** — ce document est une planification uniquement.",
    ]

    OUTPUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    write_plan()
    print("V4 PLAN UPDATED")
    print("TRAINING: NOT RUN")
    print("BASELINE: V2")
    print(f"MOSAIC: {V4_PROPOSED['mosaic']}")
    print(f"LR0: {V4_PROPOSED['lr0']}")
    print(f"PLAN={OUTPUT_MD.resolve()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
