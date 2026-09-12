"use strict";

const LANDMARK_HELP = {
  TD_R: "Point le plus inférieur de la larme acétabulaire droite.",
  TD_L: "Point le plus inférieur de la larme acétabulaire gauche.",
  FHC_R: "Centre du cercle best-fit de la tête fémorale droite.",
  FHC_L: "Centre du cercle best-fit de la tête fémorale gauche.",
  ASL_R: "Extrémité latérale du sourcil droit — pas l’ostéophyte rim.",
  ASL_L: "Extrémité latérale du sourcil gauche — pas l’ostéophyte rim.",
  ASM_R: "Début médial net du sourcil droit ; en cas de doute, v=0.",
  ASM_L: "Début médial net du sourcil gauche ; en cas de doute, v=0.",
  FNM_R: "Milieu de l’axe du col droit, entre les deux corticales.",
  FNM_L: "Milieu de l’axe du col gauche, entre les deux corticales.",
  FSP_R: "Axe diaphysaire droit, juste sous le petit trochanter.",
  FSP_L: "Axe diaphysaire gauche, juste sous le petit trochanter.",
  FSD_R: "Axe diaphysaire droit, au niveau distal fiable le plus bas.",
  FSD_L: "Axe diaphysaire gauche, au niveau distal fiable le plus bas.",
};

const FSD_NAMES = new Set(["FSD_R", "FSD_L"]);
const FSD_REMINDER =
  "Si la diaphyse distale n'est pas suffisamment visible, utiliser v=0 plutôt que de placer un point approximatif.";

const LANDMARK_HOTKEYS = {
  "1": 0,
  "2": 1,
  "3": 2,
  "4": 3,
  "5": 4,
  "6": 5,
  "7": 6,
  "8": 7,
  "9": 8,
  "0": 9,
  q: 10,
  w: 11,
  e: 12,
  r: 13,
};

const canvas = document.querySelector("#annotation-canvas");
const shell = document.querySelector("#canvas-shell");
const ctx = canvas.getContext("2d");
const loading = document.querySelector("#loading");
const caseSelect = document.querySelector("#case-select");
const landmarkList = document.querySelector("#landmark-list");
const validationErrors = document.querySelector("#validation-errors");
const anatomicalWarnings = document.querySelector("#anatomical-warnings");
const saveState = document.querySelector("#save-state");
const finalizeButton = document.querySelector("#finalize");
const undoButton = document.querySelector("#undo");
const markInvisibleButton = document.querySelector("#mark-invisible");

const state = {
  dataset: "pilot",
  datasetLabel: "",
  correctionMode: false,
  correctionCaseIds: [],
  cases: [],
  caseIndex: 0,
  currentCaseInfo: null,
  annotation: null,
  yoloSuggestions: null,
  lastModifiedNs: null,
  image: null,
  currentLandmark: 0,
  dirty: false,
  history: [],
  scale: 1,
  minScale: 0.05,
  maxScale: 20,
  offsetX: 0,
  offsetY: 0,
  spacePressed: false,
  panning: false,
  panStartX: 0,
  panStartY: 0,
  panOriginX: 0,
  panOriginY: 0,
  dragging: {
    active: false,
    landmarkIndex: -1,
    startScreenX: 0,
    startScreenY: 0,
    moved: false,
    previewX: 0,
    previewY: 0,
  },
};

function readLaunchParams() {
  const params = new URLSearchParams(window.location.search);
  return {
    pilotId: params.get("pilot_id") || params.get("case") || "",
    landmarkName: params.get("landmark") || "",
  };
}

function findCaseIndexByPilotId(pilotId) {
  if (!pilotId) return 0;
  const index = state.cases.findIndex((caseInfo) => caseInfo.pilot_id === pilotId);
  return index >= 0 ? index : 0;
}

function findLandmarkIndexByName(name) {
  if (!name || !state.annotation) return -1;
  return state.annotation.landmarks.findIndex((landmark) => landmark.name === name);
}

function updateCorrectionBanner() {
  const banner = document.querySelector("#correction-banner");
  if (!banner) return;
  if (!state.correctionMode) {
    banner.hidden = true;
    return;
  }
  banner.hidden = false;
  banner.textContent =
    `Mode correction — cas autorisés : ${state.correctionCaseIds.join(", ")}. ` +
    "Sélectionnez un landmark, corrigez par clic ou glisser, puis enregistrez.";
}

function setStatus(message, kind = "neutral") {
  saveState.textContent = message;
  saveState.className = `status ${kind}`;
}

function deepCopy(value) {
  return JSON.parse(JSON.stringify(value));
}

function landmarkComplete(landmark) {
  if (landmark.v === 0) {
    return landmark.x === null && landmark.y === null;
  }
  if (landmark.v !== 2 || !Number.isFinite(landmark.x) || !Number.isFinite(landmark.y)) {
    return false;
  }
  if (!state.image) return false;
  return (
    landmark.x >= 0 &&
    landmark.x < state.image.naturalWidth &&
    landmark.y >= 0 &&
    landmark.y < state.image.naturalHeight
  );
}

function incompleteLandmarks() {
  if (!state.annotation) return [];
  return state.annotation.landmarks.filter((landmark) => !landmarkComplete(landmark));
}

function getSuggestion(index) {
  if (!state.yoloSuggestions?.suggestions) return null;
  return state.yoloSuggestions.suggestions[index] || null;
}

function shouldShowSuggestion(index) {
  if (!state.annotation || !state.yoloSuggestions?.available) return false;
  const landmark = state.annotation.landmarks[index];
  if (landmark.v !== null) return false;
  const suggestion = getSuggestion(index);
  return Boolean(suggestion?.visible && Number.isFinite(suggestion.x) && Number.isFinite(suggestion.y));
}

function suggestionPosition(index) {
  const suggestion = getSuggestion(index);
  if (!shouldShowSuggestion(index) || !suggestion) return null;
  return { x: suggestion.x, y: suggestion.y };
}

function updateCaseContext() {
  const remarqueEl = document.querySelector("#verification-remarque");
  const overlayLink = document.querySelector("#yolo-overlay-link");
  const fsdBanner = document.querySelector("#fsd-banner");
  const yoloNote = document.querySelector("#yolo-suggestions-note");
  const caseInfo = state.currentCaseInfo;

  if (remarqueEl) {
    const remarque = caseInfo?.verification_remarque?.trim();
    remarqueEl.textContent = remarque || "Aucune remarque de vérification pour ce cas.";
    remarqueEl.classList.toggle("has-warning", Boolean(remarque));
  }

  if (overlayLink) {
    if (caseInfo?.yolo_overlay_reference) {
      overlayLink.href = caseInfo.yolo_overlay_reference;
      overlayLink.hidden = false;
      overlayLink.title = "Référence visuelle uniquement — ne remplace pas l'annotation manuelle.";
    } else {
      overlayLink.hidden = true;
      overlayLink.removeAttribute("href");
    }
  }

  if (yoloNote) {
    if (state.dataset === "new_26" && state.yoloSuggestions?.available) {
      yoloNote.hidden = false;
      yoloNote.textContent =
        "Suggestions YOLO affichées (bleu pointillé) — à confirmer par clic ou glisser. " +
        "Elles ne sont jamais enregistrées automatiquement.";
    } else if (state.dataset === "new_26" && caseInfo?.yolo_suggestions_available) {
      yoloNote.hidden = false;
      yoloNote.textContent = "Prédiction YOLO indisponible pour ce cas.";
      yoloNote.classList.add("warning");
    } else {
      yoloNote.hidden = true;
      yoloNote.classList.remove("warning");
    }
  }

  if (fsdBanner && state.annotation) {
    const landmark = state.annotation.landmarks[state.currentLandmark];
    const showFsd = state.dataset === "new_26" && landmark && FSD_NAMES.has(landmark.name);
    fsdBanner.hidden = !showFsd;
    if (showFsd) {
      fsdBanner.textContent = FSD_REMINDER;
    }
  }
}

async function refreshAnatomicalWarnings() {
  if (!anatomicalWarnings || !state.annotation || !state.image) return;
  anatomicalWarnings.replaceChildren();
  const humanPlaced = state.annotation.landmarks.some((landmark) => landmark.v === 2);
  if (!humanPlaced) return;

  try {
    const response = await fetch("/api/anatomical-checks", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        landmarks: state.annotation.landmarks,
        image_width: state.image.naturalWidth,
        image_height: state.image.naturalHeight,
      }),
    });
    if (!response.ok) return;
    const payload = await response.json();
    for (const warning of payload.warnings || []) {
      const li = document.createElement("li");
      li.textContent = warning.message;
      li.className = "anatomical-warning";
      anatomicalWarnings.append(li);
    }
  } catch {
    // Les avertissements anatomiques sont informatifs uniquement.
  }
}

function updateInterface() {
  if (!state.annotation) return;
  const landmark = state.annotation.landmarks[state.currentLandmark];
  document.querySelector("#current-id").textContent = landmark.id;
  document.querySelector("#current-name").textContent = landmark.name;
  document.querySelector("#current-instruction").textContent = LANDMARK_HELP[landmark.name];
  document.querySelector("#current-side").textContent =
    landmark.side === "right"
      ? "Côté DROIT patient — moitié GAUCHE de l’image"
      : "Côté GAUCHE patient — moitié DROITE de l’image";

  const fsdHint = document.querySelector("#fsd-hint");
  if (fsdHint) {
    const isFsd = FSD_NAMES.has(landmark.name);
    fsdHint.hidden = !isFsd;
    if (isFsd) {
      fsdHint.innerHTML = `<strong>FSD :</strong> ${FSD_REMINDER}`;
    }
  }

  if (markInvisibleButton) {
    markInvisibleButton.classList.toggle("fsd-prominent", FSD_NAMES.has(landmark.name));
    markInvisibleButton.title = FSD_NAMES.has(landmark.name)
      ? `${FSD_REMINDER} (raccourci V)`
      : "Marquer le landmark courant non visible (raccourci V)";
  }

  document.querySelector("#case-title").textContent =
    `${state.annotation.image_id} · ${state.annotation.source_file}`;

  updateCaseContext();

  const completeCount = state.annotation.landmarks.filter(landmarkComplete).length;
  document.querySelector("#progress").textContent = `${completeCount} / 14`;
  finalizeButton.disabled = completeCount !== 14;
  undoButton.disabled = state.history.length === 0;

  landmarkList.replaceChildren();
  state.annotation.landmarks.forEach((item, index) => {
    const row = document.createElement("li");
    const button = document.createElement("button");
    button.type = "button";
    button.className = "landmark-row";
    if (index === state.currentLandmark) button.classList.add("active");
    if (item.v === 0) button.classList.add("invisible");
    if (item.v === 2) button.classList.add("placed");
    if (item.v === null && shouldShowSuggestion(index)) button.classList.add("suggested");

    let status = "à faire";
    if (item.v === 2) status = `(${item.x.toFixed(1)}, ${item.y.toFixed(1)})`;
    else if (item.v === 0) status = "v=0";
    else if (shouldShowSuggestion(index)) status = "suggestion YOLO";

    button.innerHTML =
      `<span class="landmark-code">${item.id}</span>` +
      `<strong>${item.name}</strong><span class="landmark-status">${status}</span>`;
    button.addEventListener("click", () => {
      state.currentLandmark = index;
      updateInterface();
      draw();
    });
    row.append(button);
    landmarkList.append(row);
  });

  validationErrors.replaceChildren();
  for (const item of incompleteLandmarks()) {
    const li = document.createElement("li");
    li.textContent = `${item.id} ${item.name} : confirmation humaine (clic/glisser) ou v=0 requis`;
    validationErrors.append(li);
  }

  refreshAnatomicalWarnings();
  draw();
}

function resizeCanvas() {
  const rect = shell.getBoundingClientRect();
  const ratio = window.devicePixelRatio || 1;
  canvas.width = Math.max(1, Math.floor(rect.width * ratio));
  canvas.height = Math.max(1, Math.floor(rect.height * ratio));
  canvas.style.width = `${rect.width}px`;
  canvas.style.height = `${rect.height}px`;
  draw();
}

function fitImage() {
  if (!state.image) return;
  const rect = shell.getBoundingClientRect();
  const margin = 28;
  const availableWidth = Math.max(1, rect.width - margin * 2);
  const availableHeight = Math.max(1, rect.height - margin * 2);
  state.scale = Math.min(
    availableWidth / state.image.naturalWidth,
    availableHeight / state.image.naturalHeight
  );
  state.minScale = Math.max(0.01, state.scale * 0.25);
  state.maxScale = Math.max(8, state.scale * 30);
  state.offsetX = (rect.width - state.image.naturalWidth * state.scale) / 2;
  state.offsetY = (rect.height - state.image.naturalHeight * state.scale) / 2;
  draw();
}

function zoomAt(factor, screenX, screenY) {
  if (!state.image) return;
  const oldScale = state.scale;
  const newScale = Math.min(state.maxScale, Math.max(state.minScale, oldScale * factor));
  const imageX = (screenX - state.offsetX) / oldScale;
  const imageY = (screenY - state.offsetY) / oldScale;
  state.scale = newScale;
  state.offsetX = screenX - imageX * newScale;
  state.offsetY = screenY - imageY * newScale;
  draw();
}

function drawPointLabel(x, y, radius, id, name, active, human) {
  ctx.font = `${Math.max(11 / state.scale, 7)}px system-ui`;
  const label = `${id} ${name}`;
  ctx.fillStyle = active ? "#ffd166" : human ? "#ffffff" : "#9ecfff";
  ctx.fillText(label, x + radius * 1.6, y - radius * 1.4);
}

function drawHumanLandmark(landmark, index, radius, lineWidth) {
  const active = index === state.currentLandmark;
  const draggingThis = state.dragging.active && state.dragging.landmarkIndex === index;
  let x = landmark.x;
  let y = landmark.y;
  if (draggingThis) {
    x = state.dragging.previewX;
    y = state.dragging.previewY;
  }

  ctx.beginPath();
  ctx.arc(x, y, radius * (active ? 1.4 : 1), 0, Math.PI * 2);
  ctx.fillStyle = active ? "#ffd166" : "#38d9a9";
  ctx.fill();
  ctx.lineWidth = lineWidth;
  ctx.strokeStyle = "#081018";
  ctx.stroke();
  drawPointLabel(x, y, radius, landmark.id, landmark.name, active, true);
}

function drawSuggestionLandmark(landmark, index, radius, lineWidth) {
  const suggestion = suggestionPosition(index);
  if (!suggestion) return;

  const active = index === state.currentLandmark;
  let x = suggestion.x;
  let y = suggestion.y;
  if (state.dragging.active && state.dragging.landmarkIndex === index) {
    x = state.dragging.previewX;
    y = state.dragging.previewY;
  }

  ctx.setLineDash([Math.max(4 / state.scale, 2), Math.max(3 / state.scale, 2)]);
  ctx.beginPath();
  ctx.arc(x, y, radius * (active ? 1.35 : 1), 0, Math.PI * 2);
  ctx.fillStyle = active ? "rgba(100, 181, 246, 0.35)" : "rgba(100, 181, 246, 0.18)";
  ctx.fill();
  ctx.lineWidth = lineWidth;
  ctx.strokeStyle = active ? "#64b5f6" : "#4a8fd4";
  ctx.stroke();
  ctx.setLineDash([]);
  drawPointLabel(x, y, radius, landmark.id, landmark.name, active, false);
}

function draw() {
  const ratio = window.devicePixelRatio || 1;
  const width = canvas.width / ratio;
  const height = canvas.height / ratio;
  ctx.setTransform(ratio, 0, 0, ratio, 0, 0);
  ctx.clearRect(0, 0, width, height);
  ctx.fillStyle = "#11161c";
  ctx.fillRect(0, 0, width, height);
  if (!state.image || !state.annotation) return;

  ctx.save();
  ctx.translate(state.offsetX, state.offsetY);
  ctx.scale(state.scale, state.scale);
  ctx.drawImage(state.image, 0, 0);

  const radius = Math.max(3.5 / state.scale, 2);
  const lineWidth = Math.max(2 / state.scale, 1);

  state.annotation.landmarks.forEach((landmark, index) => {
    if (shouldShowSuggestion(index)) {
      drawSuggestionLandmark(landmark, index, radius, lineWidth);
    }
  });

  state.annotation.landmarks.forEach((landmark, index) => {
    if (landmark.v === 2) {
      drawHumanLandmark(landmark, index, radius, lineWidth);
    }
  });
  ctx.restore();

  ctx.font = "700 13px system-ui";
  ctx.fillStyle = "rgba(8, 16, 24, 0.82)";
  ctx.fillRect(12, 12, 170, 30);
  ctx.fillRect(width - 182, 12, 170, 30);
  ctx.fillStyle = "#ffffff";
  ctx.fillText("DROITE PATIENT (R)", 24, 32);
  ctx.fillText("GAUCHE PATIENT (L)", width - 170, 32);
  document.querySelector("#zoom-level").textContent = `${Math.round(state.scale * 100)} %`;
}

function canvasPoint(event) {
  const rect = canvas.getBoundingClientRect();
  return { x: event.clientX - rect.left, y: event.clientY - rect.top };
}

function screenToImage(screenX, screenY) {
  return {
    x: (screenX - state.offsetX) / state.scale,
    y: (screenY - state.offsetY) / state.scale,
  };
}

function imageOnCanvas(imageX, imageY) {
  return (
    imageX >= 0 &&
    imageX < state.image.naturalWidth &&
    imageY >= 0 &&
    imageY < state.image.naturalHeight
  );
}

function hitRadiusImage() {
  return Math.max(10 / state.scale, 6);
}

function landmarkImagePosition(index) {
  const landmark = state.annotation.landmarks[index];
  if (landmark.v === 2) {
    return { x: landmark.x, y: landmark.y, kind: "human" };
  }
  const suggestion = suggestionPosition(index);
  if (suggestion) {
    return { x: suggestion.x, y: suggestion.y, kind: "suggestion" };
  }
  return null;
}

function hitTestLandmark(screenX, screenY) {
  if (!state.annotation) return null;
  const imagePoint = screenToImage(screenX, screenY);
  const hitRadius = hitRadiusImage();
  let best = null;
  let bestDistance = hitRadius;

  for (let index = state.annotation.landmarks.length - 1; index >= 0; index -= 1) {
    const position = landmarkImagePosition(index);
    if (!position) continue;
    const distance = Math.hypot(imagePoint.x - position.x, imagePoint.y - position.y);
    if (distance <= bestDistance) {
      best = { index, kind: position.kind };
      bestDistance = distance;
    }
  }
  return best;
}

function pushHistory() {
  state.history.push({
    landmarks: deepCopy(state.annotation.landmarks),
    currentLandmark: state.currentLandmark,
  });
  if (state.history.length > 50) state.history.shift();
}

function selectLandmark(index) {
  if (index < 0 || index >= 14) return;
  state.currentLandmark = index;
  updateInterface();
}

function selectNextIncomplete() {
  const landmarks = state.annotation.landmarks;
  for (let step = 1; step <= landmarks.length; step += 1) {
    const index = (state.currentLandmark + step) % landmarks.length;
    if (!landmarkComplete(landmarks[index])) {
      state.currentLandmark = index;
      return;
    }
  }
}

function confirmLandmarkAt(index, imageX, imageY, sourceLabel) {
  if (!state.image || !state.annotation) return false;
  if (!imageOnCanvas(imageX, imageY)) {
    setStatus("Position hors de l’image : aucun point confirmé.", "warning");
    return false;
  }

  pushHistory();
  const landmark = state.annotation.landmarks[index];
  landmark.x = Math.round(imageX * 100) / 100;
  landmark.y = Math.round(imageY * 100) / 100;
  landmark.v = 2;
  state.annotation.image_width = state.image.naturalWidth;
  state.annotation.image_height = state.image.naturalHeight;
  state.currentLandmark = index;
  state.dirty = true;
  setStatus(
    `${landmark.id} ${landmark.name} confirmé (${sourceLabel}) — brouillon non enregistré.`,
    "dirty"
  );
  if (!state.correctionMode) {
    selectNextIncomplete();
  }
  updateInterface();
  return true;
}

function placeCurrentLandmark(screenX, screenY) {
  const imagePoint = screenToImage(screenX, screenY);
  confirmLandmarkAt(state.currentLandmark, imagePoint.x, imagePoint.y, "clic humain");
}

function markInvisible() {
  if (!state.annotation) return;
  const landmark = state.annotation.landmarks[state.currentLandmark];
  if (FSD_NAMES.has(landmark.name) && landmark.v !== 0) {
    const ok = window.confirm(
      `${landmark.id} ${landmark.name} : confirmer v=0 ?\n\n${FSD_REMINDER}`
    );
    if (!ok) return;
  }
  pushHistory();
  landmark.x = null;
  landmark.y = null;
  landmark.v = 0;
  state.dirty = true;
  setStatus(`${landmark.id} marqué non visible (v=0).`, "dirty");
  selectNextIncomplete();
  updateInterface();
}

function undo() {
  const previous = state.history.pop();
  if (!previous) return;
  state.annotation.landmarks = previous.landmarks;
  state.currentLandmark = previous.currentLandmark;
  state.dirty = true;
  setStatus("Dernière action annulée — brouillon non enregistré.", "dirty");
  updateInterface();
}

async function confirmDiscard() {
  if (!state.dirty) return true;
  const dialog = document.querySelector("#confirm-dialog");
  dialog.showModal();
  const result = await new Promise((resolve) => {
    dialog.addEventListener("close", () => resolve(dialog.returnValue), { once: true });
  });
  return result === "discard";
}

async function loadYoloSuggestions(caseInfo, width, height) {
  state.yoloSuggestions = null;
  if (state.dataset !== "new_26" || !caseInfo?.pilot_id) return;
  try {
    const url =
      `/api/yolo-suggestions?pilot_id=${encodeURIComponent(caseInfo.pilot_id)}` +
      `&width=${encodeURIComponent(width)}&height=${encodeURIComponent(height)}`;
    const response = await fetch(url);
    if (!response.ok) return;
    state.yoloSuggestions = await response.json();
  } catch {
    state.yoloSuggestions = null;
  }
}

async function loadCase(index, launchLandmarkName = "") {
  if (index < 0 || index >= state.cases.length) return;
  if (!(await confirmDiscard())) {
    caseSelect.value = String(state.caseIndex);
    return;
  }

  loading.hidden = false;
  const caseInfo = state.cases[index];
  try {
    const response = await fetch(`/api/annotation?file=${encodeURIComponent(caseInfo.annotation_name)}`);
    if (!response.ok) throw new Error((await response.json()).error || "Chargement JSON impossible.");
    const payload = await response.json();

    const image = new Image();
    image.src = `/images/${encodeURIComponent(caseInfo.image_name)}`;
    await image.decode();

    state.caseIndex = index;
    state.currentCaseInfo = caseInfo;
    state.annotation = payload.annotation;
    if (!state.annotation.annotator_id) {
      state.annotation.annotator_id = "annotator_A";
    }
    state.lastModifiedNs = payload.last_modified_ns;
    state.image = image;
    await loadYoloSuggestions(caseInfo, image.naturalWidth, image.naturalHeight);

    const landmarkIndex = findLandmarkIndexByName(launchLandmarkName);
    if (landmarkIndex >= 0) {
      state.currentLandmark = landmarkIndex;
    } else {
      const firstIncomplete = state.annotation.landmarks.findIndex((landmark) => !landmarkComplete(landmark));
      state.currentLandmark = firstIncomplete >= 0 ? firstIncomplete : 0;
    }
    state.dirty = false;
    state.history = [];
    caseSelect.value = String(index);
    fitImage();
    if (state.correctionMode) {
      setStatus(
        "Mode correction — corrigez par clic ou glisser, puis enregistrez.",
        "neutral"
      );
    } else if (state.yoloSuggestions?.available) {
      setStatus(
        "Suggestions YOLO chargées — confirmez chaque point par clic ou glisser avant validation.",
        "neutral"
      );
    } else {
      setStatus("Fichier chargé — aucune modification locale.", "neutral");
    }
    updateInterface();
  } catch (error) {
    setStatus(error.message, "error");
  } finally {
    loading.hidden = true;
  }
}

async function saveAnnotation(finalize) {
  if (!state.annotation) return;
  const caseInfo = state.cases[state.caseIndex];
  setStatus(finalize ? "Validation en cours…" : "Enregistrement en cours…", "neutral");
  try {
    const response = await fetch(
      `/api/annotation?file=${encodeURIComponent(caseInfo.annotation_name)}`,
      {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          annotation: state.annotation,
          finalize,
          last_modified_ns: state.lastModifiedNs,
        }),
      }
    );
    const payload = await response.json();
    if (!response.ok) {
      const details = payload.details ? ` ${payload.details.join(" ")}` : "";
      throw new Error(`${payload.error || "Sauvegarde refusée."}${details}`);
    }
    state.lastModifiedNs = payload.last_modified_ns;
    state.dirty = false;
    state.history = [];
    setStatus(
      finalize ? "Image complète validée et enregistrée." : "Brouillon enregistré.",
      "success"
    );
    updateInterface();
  } catch (error) {
    setStatus(error.message, "error");
  }
}

function caseLabel(caseInfo) {
  if (caseInfo.dicom_name) {
    const suffix = caseInfo.dicom_name.slice(-12);
    return `${caseInfo.pilot_id} — …${suffix}`;
  }
  return `${caseInfo.pilot_id} — ${caseInfo.image_name}`;
}

function isTypingTarget(event) {
  const target = event.target;
  return target instanceof HTMLElement && (target.tagName === "INPUT" || target.tagName === "TEXTAREA");
}

async function initialize() {
  const launch = readLaunchParams();
  try {
    const response = await fetch("/api/cases");
    if (!response.ok) throw new Error("Impossible de charger la liste des cas.");
    const payload = await response.json();
    state.dataset = payload.dataset || "pilot";
    state.datasetLabel = payload.label || state.dataset;
    state.correctionMode = payload.correction_mode === true;
    state.correctionCaseIds = payload.correction_case_ids || [];
    state.cases = payload.cases;
    const datasetLabel = document.querySelector("#dataset-label");
    if (datasetLabel) {
      datasetLabel.textContent = state.correctionMode
        ? `${state.datasetLabel.toUpperCase()} · MODE CORRECTION`
        : state.datasetLabel.toUpperCase();
    }
    document.title = state.correctionMode
      ? `${state.datasetLabel} — Correction manuelle`
      : `${state.datasetLabel} — Annotation manuelle`;
    updateCorrectionBanner();
    state.cases.forEach((caseInfo, index) => {
      const option = document.createElement("option");
      option.value = String(index);
      option.textContent = caseLabel(caseInfo);
      caseSelect.append(option);
    });
    const initialIndex = findCaseIndexByPilotId(launch.pilotId);
    await loadCase(initialIndex, launch.landmarkName);
  } catch (error) {
    loading.textContent = error.message;
    setStatus(error.message, "error");
  }
}

canvas.addEventListener("contextmenu", (event) => event.preventDefault());
canvas.addEventListener("mousedown", (event) => {
  const point = canvasPoint(event);
  if (event.button === 2 || event.button === 1 || (event.button === 0 && state.spacePressed)) {
    state.panning = true;
    state.panStartX = point.x;
    state.panStartY = point.y;
    state.panOriginX = state.offsetX;
    state.panOriginY = state.offsetY;
    canvas.classList.add("panning");
    event.preventDefault();
    return;
  }

  if (event.button === 0) {
    const hit = hitTestLandmark(point.x, point.y);
    if (hit) {
      state.currentLandmark = hit.index;
      const position = landmarkImagePosition(hit.index);
      state.dragging.active = true;
      state.dragging.landmarkIndex = hit.index;
      state.dragging.startScreenX = point.x;
      state.dragging.startScreenY = point.y;
      state.dragging.moved = false;
      state.dragging.previewX = position.x;
      state.dragging.previewY = position.y;
      canvas.classList.add("dragging");
      updateInterface();
      return;
    }
    placeCurrentLandmark(point.x, point.y);
  }
});

window.addEventListener("mousemove", (event) => {
  if (state.dragging.active) {
    const rect = canvas.getBoundingClientRect();
    const x = event.clientX - rect.left;
    const y = event.clientY - rect.top;
    if (Math.hypot(x - state.dragging.startScreenX, y - state.dragging.startScreenY) > 3) {
      state.dragging.moved = true;
    }
    const imagePoint = screenToImage(x, y);
    state.dragging.previewX = imagePoint.x;
    state.dragging.previewY = imagePoint.y;
    draw();
    return;
  }

  if (!state.panning) return;
  const rect = canvas.getBoundingClientRect();
  const x = event.clientX - rect.left;
  const y = event.clientY - rect.top;
  state.offsetX = state.panOriginX + x - state.panStartX;
  state.offsetY = state.panOriginY + y - state.panStartY;
  draw();
});

window.addEventListener("mouseup", (event) => {
  if (state.dragging.active) {
    const index = state.dragging.landmarkIndex;
    const previewX = state.dragging.previewX;
    const previewY = state.dragging.previewY;
    const moved = state.dragging.moved;
    state.dragging.active = false;
    state.dragging.landmarkIndex = -1;
    canvas.classList.remove("dragging");

    if (moved) {
      confirmLandmarkAt(index, previewX, previewY, "glisser humain");
    } else {
      const landmark = state.annotation.landmarks[index];
      if (landmark.v === 2) {
        confirmLandmarkAt(index, previewX, previewY, "clic humain");
      } else {
        confirmLandmarkAt(index, previewX, previewY, "confirmation suggestion YOLO");
      }
    }
    return;
  }

  state.panning = false;
  canvas.classList.remove("panning");
});

canvas.addEventListener(
  "wheel",
  (event) => {
    event.preventDefault();
    const point = canvasPoint(event);
    zoomAt(event.deltaY < 0 ? 1.15 : 1 / 1.15, point.x, point.y);
  },
  { passive: false }
);

window.addEventListener("keydown", (event) => {
  if (isTypingTarget(event)) return;

  if (event.code === "Space") {
    state.spacePressed = true;
    canvas.classList.add("pan-ready");
    event.preventDefault();
  }
  if ((event.ctrlKey || event.metaKey) && event.key.toLowerCase() === "z") {
    event.preventDefault();
    undo();
    return;
  }
  if (event.key.toLowerCase() === "v") {
    event.preventDefault();
    markInvisible();
    return;
  }
  if (event.key === "[") {
    event.preventDefault();
    selectLandmark((state.currentLandmark + 13) % 14);
    return;
  }
  if (event.key === "]") {
    event.preventDefault();
    selectLandmark((state.currentLandmark + 1) % 14);
    return;
  }
  const hotkey = event.key.length === 1 ? event.key.toLowerCase() : "";
  if (Object.prototype.hasOwnProperty.call(LANDMARK_HOTKEYS, hotkey)) {
    event.preventDefault();
    selectLandmark(LANDMARK_HOTKEYS[hotkey]);
  }
});

window.addEventListener("keyup", (event) => {
  if (event.code === "Space") {
    state.spacePressed = false;
    canvas.classList.remove("pan-ready");
  }
});

window.addEventListener("beforeunload", (event) => {
  if (!state.dirty) return;
  event.preventDefault();
  event.returnValue = "";
});

caseSelect.addEventListener("change", () => loadCase(Number(caseSelect.value)));
document.querySelector("#previous-case").addEventListener("click", () => loadCase(state.caseIndex - 1));
document.querySelector("#next-case").addEventListener("click", () => loadCase(state.caseIndex + 1));
document.querySelector("#previous-landmark").addEventListener("click", () => {
  selectLandmark((state.currentLandmark + 13) % 14);
});
document.querySelector("#mark-invisible").addEventListener("click", markInvisible);
document.querySelector("#undo").addEventListener("click", undo);
document.querySelector("#fit-image").addEventListener("click", fitImage);
document.querySelector("#zoom-in").addEventListener("click", () => {
  const rect = shell.getBoundingClientRect();
  zoomAt(1.2, rect.width / 2, rect.height / 2);
});
document.querySelector("#zoom-out").addEventListener("click", () => {
  const rect = shell.getBoundingClientRect();
  zoomAt(1 / 1.2, rect.width / 2, rect.height / 2);
});
document.querySelector("#save-draft").addEventListener("click", () => saveAnnotation(false));
document.querySelector("#finalize").addEventListener("click", () => saveAnnotation(true));

new ResizeObserver(resizeCanvas).observe(shell);
initialize();
