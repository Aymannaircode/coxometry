#!/usr/bin/env python3
"""Analyse lecture seule du comportement d'entraînement YOLO V2 (new_26).

Inspecte les artefacts existants dans runs/pose/.../yolo_pose_new_26_v2-3/
sans modifier aucun fichier, poids ou lancer d'entraînement.
"""

from __future__ import annotations

import csv
import json
import statistics
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

import yaml

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
RUN_DIR = PROJECT_ROOT / "runs" / "pose" / "runs" / "pose" / "runs" / "yolo_pose_new_26_v2-3"
RESULTS_CSV = RUN_DIR / "results.csv"
ARGS_YAML = RUN_DIR / "args.yaml"
BEST_PT = RUN_DIR / "weights" / "best.pt"
OUTPUT_MD = PROJECT_ROOT / "datasets" / "yolo_pose_new_26" / "v2_training_behavior.md"

# Référence inference (diagnostic A confirmé)
REF_ASL_L_TRAIN_PX = 538.18
REF_ASL_L_VAL_PX = 471.72
REF_ASL_R_TRAIN_PX = 142.86
REF_ASM_L_TRAIN_PX = 77.59
REF_MEDIAN_LANDMARK_PX = 80.0
GOOD_LANDMARK_PX = 150.0
BAD_LANDMARK_PX = 300.0

POSE_METRIC_COL = "metrics/mAP50-95(P)"
VAL_POSE_LOSS_COL = "val/pose_loss"
TRAIN_POSE_LOSS_COL = "train/pose_loss"
TAIL_EPOCHS = 5


@dataclass
class SeriesSummary:
    column: str
    start: float
    end: float
    best: float
    best_epoch: int
    final_epoch: int
    tail_mean: float
    prev_tail_mean: float

    @property
    def still_improving_lower_is_better(self) -> bool:
        return self.tail_mean < self.prev_tail_mean

    @property
    def still_improving_higher_is_better(self) -> bool:
        return self.tail_mean > self.prev_tail_mean


@dataclass
class TrainingVerdict:
    epochs: int
    final_pose_loss: float
    best_pose_metric: float
    best_epoch: int
    training_still_improving: bool
    global_undertraining: bool
    asl_l_specific: bool
    diagnosis: str
    recommendation: str


def format_num(value: float | None, digits: int = 4) -> str:
    if value is None:
        return "NA"
    return f"{value:.{digits}f}"


def load_results_rows() -> list[dict[str, str]]:
    if not RESULTS_CSV.is_file():
        raise FileNotFoundError(f"results.csv introuvable : {RESULTS_CSV}")
    with RESULTS_CSV.open("r", encoding="utf-8-sig", newline="") as stream:
        return list(csv.DictReader(stream))


def summarize_series(rows: list[dict[str, str]], column: str, minimize: bool) -> SeriesSummary:
    values = [float(row[column]) for row in rows]
    best_index = min(range(len(values)), key=lambda i: values[i]) if minimize else max(range(len(values)), key=lambda i: values[i])
    tail = values[-TAIL_EPOCHS:]
    prev_tail = values[-2 * TAIL_EPOCHS : -TAIL_EPOCHS]
    return SeriesSummary(
        column=column,
        start=values[0],
        end=values[-1],
        best=values[best_index],
        best_epoch=int(float(rows[best_index]["epoch"])),
        final_epoch=int(float(rows[-1]["epoch"])),
        tail_mean=statistics.mean(tail),
        prev_tail_mean=statistics.mean(prev_tail),
    )


def load_args() -> dict:
    if not ARGS_YAML.is_file():
        raise FileNotFoundError(f"args.yaml introuvable : {ARGS_YAML}")
    return yaml.safe_load(ARGS_YAML.read_text(encoding="utf-8"))


def load_checkpoint_metadata() -> dict:
    if not BEST_PT.is_file():
        return {"available": False, "error": f"best.pt introuvable : {BEST_PT}"}
    try:
        import torch

        ckpt = torch.load(BEST_PT, map_location="cpu", weights_only=False)
        if not isinstance(ckpt, dict):
            return {"available": True, "type": str(type(ckpt))}
        meta = {
            "available": True,
            "epoch": ckpt.get("epoch"),
            "best_fitness": ckpt.get("best_fitness"),
            "date": ckpt.get("date"),
            "version": ckpt.get("version"),
            "updates": ckpt.get("updates"),
        }
        train_args = ckpt.get("train_args")
        if isinstance(train_args, dict):
            meta["checkpoint_train_args"] = {
                key: train_args.get(key)
                for key in (
                    "epochs", "imgsz", "batch", "model", "data", "optimizer",
                    "lr0", "lrf", "patience", "pretrained", "pose", "device",
                )
            }
        return meta
    except Exception as exc:
        return {"available": False, "error": str(exc)}


def list_artifacts() -> dict[str, list[str]]:
    groups: dict[str, list[str]] = {
        "config": [],
        "metrics": [],
        "curves": [],
        "visual_debug": [],
        "weights": [],
        "other": [],
    }
    if not RUN_DIR.is_dir():
        return groups
    for path in sorted(RUN_DIR.rglob("*")):
        if not path.is_file():
            continue
        rel = path.relative_to(RUN_DIR).as_posix()
        lower = rel.lower()
        if lower.endswith((".pt",)):
            groups["weights"].append(rel)
        elif lower in {"args.yaml", "results.csv"}:
            groups["config"].append(rel)
        elif "results" in lower and lower.endswith(".png"):
            groups["metrics"].append(rel)
        elif any(token in lower for token in ("pose", "box", "confusion", "curve", "pr_", "f1")):
            groups["curves"].append(rel)
        elif any(token in lower for token in ("batch", "labels.jpg")):
            groups["visual_debug"].append(rel)
        else:
            groups["other"].append(rel)
    return groups


def loss_converged(train_pose: SeriesSummary, val_pose: SeriesSummary) -> tuple[bool, str]:
    train_drop = (train_pose.start - train_pose.end) / train_pose.start
    val_drop = (val_pose.start - val_pose.end) / val_pose.start
    plateau = abs(val_pose.tail_mean - val_pose.prev_tail_mean) / max(val_pose.prev_tail_mean, 1e-6) < 0.03
    if train_drop > 0.5 and val_drop > 0.4:
        state = "convergée globalement"
        if plateau:
            state += ", plateau val en fin de run"
        return True, state
    return False, "convergence partielle ou insuffisante"


def assess_verdict(
    rows: list[dict[str, str]],
    train_pose: SeriesSummary,
    val_pose: SeriesSummary,
    pose_metric: SeriesSummary,
) -> TrainingVerdict:
    converged, _ = loss_converged(train_pose, val_pose)
    improving = val_pose.still_improving_lower_is_better and pose_metric.still_improving_higher_is_better

    # mAP pose agrégé ~0.65 mais ASL_L ~538 px sur train → pas un sous-apprentissage global
    global_under = (
        pose_metric.end < 0.35
        or (not converged and val_pose.end > 2.5)
    )
    asl_l_specific = REF_ASL_L_TRAIN_PX >= BAD_LANDMARK_PX and REF_ASM_L_TRAIN_PX < GOOD_LANDMARK_PX

    if asl_l_specific and not global_under:
        diagnosis = (
            "Sous-apprentissage **localisé sur ASL_L** malgré convergence des losses agrégées "
            "et mAP pose acceptable (~0.65). Le problème n'est pas une généralisation train/val."
        )
        recommendation = (
            "V3 : repartir du checkpoint epoch 80 (meilleur mAP50-95 pose), renforcer l'apprentissage "
            "ASL_L (audit augmentations miroir, pose loss, plus de données ou focalisation keypoint), "
            "réduire l'augmentation agressive sur petit lot (mosaic/randaugment), et valider en px GT "
            "par keypoint — les métriques Ultralytics agrégées masquent l'échec ASL_L."
        )
    elif global_under:
        diagnosis = "Sous-apprentissage global de la tête pose."
        recommendation = "V3 : plus d'epochs, lr schedule, dataset élargi, entraînement GPU si possible."
    else:
        diagnosis = "Entraînement globalement acceptable ; investiguer pipeline ou landmark spécifique."
        recommendation = "V3 : analyse keypoint-level systématique pendant l'entraînement."

    return TrainingVerdict(
        epochs=int(float(rows[-1]["epoch"])),
        final_pose_loss=val_pose.end,
        best_pose_metric=pose_metric.best,
        best_epoch=pose_metric.best_epoch,
        training_still_improving=improving,
        global_undertraining=global_under,
        asl_l_specific=asl_l_specific,
        diagnosis=diagnosis,
        recommendation=recommendation,
    )


def augmentation_summary(args: dict) -> list[str]:
    keys = (
        "hsv_h", "hsv_s", "hsv_v", "degrees", "translate", "scale", "shear", "perspective",
        "flipud", "fliplr", "mosaic", "mixup", "cutmix", "copy_paste", "auto_augment", "erasing",
        "close_mosaic",
    )
    lines = []
    for key in keys:
        if key in args:
            lines.append(f"- `{key}` : **{args[key]}**")
    return lines


def write_markdown(
    rows: list[dict[str, str]],
    args: dict,
    ckpt_meta: dict,
    artifacts: dict[str, list[str]],
    train_pose: SeriesSummary,
    val_pose: SeriesSummary,
    pose_metric: SeriesSummary,
    verdict: TrainingVerdict,
) -> None:
    converged, convergence_text = loss_converged(train_pose, val_pose)
    now = datetime.now(timezone.utc).isoformat()

    lines = [
        "# Comportement d'entraînement V2 — new_26",
        "",
        f"**Généré :** {now}",
        f"**Run :** `{RUN_DIR.relative_to(PROJECT_ROOT).as_posix()}/`",
        "**Mode :** lecture seule — aucun fichier modifié",
        "",
        "## Synthèse exécutive",
        "",
        f"- **Epochs :** {verdict.epochs}",
        f"- **Loss pose val finale :** {format_num(verdict.final_pose_loss, 3)}",
        f"- **Meilleure métrique pose (mAP50-95) :** {format_num(verdict.best_pose_metric, 3)} "
        f"(epoch **{verdict.best_epoch}**)",
        f"- **Loss pose train finale :** {format_num(train_pose.end, 3)} "
        f"(début {format_num(train_pose.start, 3)})",
        f"- **Convergence loss pose :** {'Oui' if converged else 'Partielle'} — {convergence_text}",
        f"- **Amélioration fin de run :** {'OUI' if verdict.training_still_improving else 'NON'} "
        f"(val/pose_loss dernières {TAIL_EPOCHS} epochs : {format_num(val_pose.tail_mean, 3)} vs "
        f"{format_num(val_pose.prev_tail_mean, 3)} ; mAP50-95(P) : {format_num(pose_metric.tail_mean, 3)} vs "
        f"{format_num(pose_metric.prev_tail_mean, 3)})",
        f"- **Sous-apprentissage global :** {'OUI' if verdict.global_undertraining else 'NON'}",
        f"- **Problème spécifique ASL_L :** {'OUI' if verdict.asl_l_specific else 'NON'}",
        "",
        "### Lien avec l'inference (diagnostic A confirmé)",
        "",
        "| Landmark | TRAIN (px) | VAL (px) | Commentaire |",
        "|----------|------------|----------|-------------|",
        f"| ASL_L | {REF_ASL_L_TRAIN_PX:.2f} | {REF_ASL_L_VAL_PX:.2f} | Échec train + val |",
        f"| ASL_R | {REF_ASL_R_TRAIN_PX:.2f} | 147.73 | Dégradé mais 4× mieux que ASL_L |",
        f"| ASM_L | {REF_ASM_L_TRAIN_PX:.2f} | 80.94 | Bon — sourcil médial appris |",
        "",
        "**Conclusion :** les métriques Ultralytics agrégées (mAP pose ~0.65) **masquent** "
        "l'échec pixel-level sur ASL_L. Ce n'est pas un problème de généralisation val.",
        "",
        f"## Recommandation V3",
        "",
        verdict.recommendation,
        "",
        "## Paramètres d'entraînement V2",
        "",
        "| Paramètre | Valeur |",
        "|-----------|--------|",
        f"| model | `{args.get('model', 'NA')}` |",
        f"| pretrained | **{args.get('pretrained', 'NA')}** |",
        f"| data | `{args.get('data', 'NA')}` |",
        f"| epochs | **{args.get('epochs', 'NA')}** |",
        f"| imgsz | **{args.get('imgsz', 'NA')}** |",
        f"| batch | **{args.get('batch', 'NA')}** |",
        f"| device | **{args.get('device', 'NA')}** |",
        f"| optimizer | **{args.get('optimizer', 'NA')}** |",
        f"| lr0 | **{args.get('lr0', 'NA')}** |",
        f"| lrf | **{args.get('lrf', 'NA')}** |",
        f"| patience | **{args.get('patience', 'NA')}** |",
        f"| pose (loss gain) | **{args.get('pose', 'NA')}** |",
        f"| kobj | **{args.get('kobj', 'NA')}** |",
        f"| box | **{args.get('box', 'NA')}** |",
        f"| cos_lr | **{args.get('cos_lr', 'NA')}** |",
        f"| amp | **{args.get('amp', 'NA')}** |",
        f"| seed | **{args.get('seed', 'NA')}** |",
        "",
        "### Augmentations",
        "",
    ]
    lines.extend(augmentation_summary(args))

    lines.extend(
        [
            "",
            "## Courbes et convergence",
            "",
            "### Loss pose",
            "",
            "| Split | Début | Fin | Meilleur | Epoch best |",
            "|-------|-------|-----|----------|------------|",
            f"| train/pose_loss | {format_num(train_pose.start, 3)} | {format_num(train_pose.end, 3)} | "
            f"{format_num(train_pose.best, 3)} | {train_pose.best_epoch} |",
            f"| val/pose_loss | {format_num(val_pose.start, 3)} | {format_num(val_pose.end, 3)} | "
            f"{format_num(val_pose.best, 3)} | {val_pose.best_epoch} |",
            "",
            "### Métriques pose (agrégées, toutes keypoints)",
            "",
            f"- **mAP50(P) final :** {format_num(float(rows[-1]['metrics/mAP50(P)']), 3)} "
            f"(max dès epoch 1 — peu discriminant sur 5 val)",
            f"- **mAP50-95(P) final :** {format_num(pose_metric.end, 3)}",
            f"- **mAP50-95(P) best :** {format_num(pose_metric.best, 3)} @ epoch **{pose_metric.best_epoch}**",
            "",
            "**Note :** chute mAP50(P) à epoch 13 (~0.20) puis récupération — instabilité early training "
            "typique d'un très petit val set (5 images).",
            "",
            "### Dernières epochs",
            "",
            "| Epoch | train/pose | val/pose | mAP50-95(P) |",
            "|------:|-----------:|---------:|------------:|",
        ]
    )
    for row in rows[-10:]:
        lines.append(
            f"| {row['epoch']} | {format_num(float(row[TRAIN_POSE_LOSS_COL]), 3)} | "
            f"{format_num(float(row[VAL_POSE_LOSS_COL]), 3)} | "
            f"{format_num(float(row[POSE_METRIC_COL]), 3)} |"
        )

    lines.extend(
        [
            "",
            "**Observation :** best mAP50-95(P) à epoch **80** (0.692), puis légère dégradation "
            "jusqu'à epoch 100 (0.646). `best.pt` et `last.pt` ont la même taille/timestamp — "
            "vérifier si le meilleur checkpoint correspond bien à epoch 80 pour V3.",
            "",
            "## Métadonnées best.pt (lecture seule)",
            "",
            "```json",
            json.dumps(ckpt_meta, indent=2, ensure_ascii=False),
            "```",
            "",
            "## Artefacts disponibles",
            "",
        ]
    )
    for group, files in artifacts.items():
        if not files:
            continue
        lines.append(f"### {group}")
        lines.append("")
        for rel in files:
            lines.append(f"- `{rel}`")
        lines.append("")

    lines.extend(
        [
            "## Métriques keypoint-level pendant l'entraînement",
            "",
            "**Non disponibles** dans les artefacts Ultralytics standard de ce run.",
            "",
            "Ce run expose uniquement :",
            "- losses agrégées (`train/pose_loss`, `val/pose_loss`) — **pas par keypoint** ;",
            "- mAP pose globaux (`metrics/mAP50(P)`, `metrics/mAP50-95(P)`) — **pas par landmark** ;",
            "- visualisations batch (`val_batch0_pred.jpg`, `train_batch*.jpg`) — inspection visuelle possible ;",
            "- courbes `PoseP_curve.png`, `PoseR_curve.png`, `PoseF1_curve.png`, `results.png`.",
            "",
            "Pour V3, prévoir une **validation px/keypoint** (comme `analyze_v2_train_vs_val_new_26.py`) "
            "à intervalles réguliers — seule métrique fiable pour ASL_L sur ce dataset.",
            "",
            "## Réponses aux 5 questions",
            "",
            f"1. **Loss pose/keypoint converge ?** "
            f"Loss agrégée : **{'Oui' if converged else 'Partiellement'}** "
            f"(train {format_num(train_pose.start, 2)}→{format_num(train_pose.end, 2)}, "
            f"val {format_num(val_pose.start, 2)}→{format_num(val_pose.end, 2)}). "
            "Pas de métrique keypoint-level dans le run.",
            f"2. **Dernières epochs encore en amélioration ?** "
            f"**{'Oui' if verdict.training_still_improving else 'Non'}** — plateau/dégradation légère "
            f"après epoch {verdict.best_epoch}.",
            f"3. **Modèle sous-entraîné globalement ?** "
            f"**{'Oui' if verdict.global_undertraining else 'Non'}** — mAP pose ~0.65, la plupart des "
            f"landmarks < {GOOD_LANDMARK_PX} px en inference.",
            f"4. **Problème ASL_L isolé ?** "
            f"**{'Oui' if verdict.asl_l_specific else 'Non'}** — ASL_L ~538 px train vs ASM_L ~78 px, "
            "autres landmarks ~60–170 px.",
            "5. **Paramètres V2 :** voir tableau ci-dessus (`epochs=100`, `batch=2`, `imgsz=640`, "
            "`device=cpu`, finetune depuis V1 `best.pt`, augmentations fortes).",
            "",
            "## Regénérer",
            "",
            "```bash",
            ".venv\\Scripts\\python.exe annotation_pilot\\scripts\\analyze_v2_training_behavior_new_26.py",
            "```",
        ]
    )
    OUTPUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    rows = load_results_rows()
    args = load_args()
    ckpt_meta = load_checkpoint_metadata()
    artifacts = list_artifacts()

    train_pose = summarize_series(rows, TRAIN_POSE_LOSS_COL, minimize=True)
    val_pose = summarize_series(rows, VAL_POSE_LOSS_COL, minimize=True)
    pose_metric = summarize_series(rows, POSE_METRIC_COL, minimize=False)
    verdict = assess_verdict(rows, train_pose, val_pose, pose_metric)

    write_markdown(rows, args, ckpt_meta, artifacts, train_pose, val_pose, pose_metric, verdict)

    print("V2 TRAINING BEHAVIOR COMPLETE")
    print("")
    print(f"Epochs: {verdict.epochs}")
    print(f"Final pose loss: {format_num(verdict.final_pose_loss, 3)}")
    print(f"Best pose metric: {format_num(verdict.best_pose_metric, 3)}")
    print(f"Best epoch: {verdict.best_epoch}")
    print(f"Training still improving: {'YES' if verdict.training_still_improving else 'NO'}")
    print(f"Global undertraining: {'YES' if verdict.global_undertraining else 'NO'}")
    print(f"ASL_L-specific problem: {'YES' if verdict.asl_l_specific else 'NO'}")
    print(f"Recommendation: {verdict.recommendation}")
    print(f"MD={OUTPUT_MD}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
