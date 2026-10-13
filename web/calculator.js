"use strict";

/* Pure, dependency-free scoring logic shared by the browser and Node tests. */
(function (root) {
  const criteria = Object.freeze({
    dvt: [
      ["active_cancer", 1, "Active cancer (treatment ongoing, within 6 months, or palliative)"],
      ["paralysis_paresis", 1, "Paralysis, paresis, or plaster immobilization of the lower limb"],
      ["recently_bedridden", 1, "Bedridden for at least 3 days, or major surgery under anesthesia within 12 weeks"],
      ["localized_tenderness", 1, "Tenderness along the deep venous system"],
      ["entire_leg_swollen", 1, "Entire leg swollen"],
      ["calf_swelling_3cm", 1, "Calf swelling ≥3 cm versus the asymptomatic leg (10 cm below tibial tuberosity)"],
      ["pitting_edema", 1, "Pitting edema confined to the symptomatic leg"],
      ["collateral_veins", 1, "Collateral superficial veins (non-varicose)"],
      ["previous_dvt", 1, "Previously documented DVT"],
      ["alternative_diagnosis", -2, "An alternative diagnosis is at least as likely as DVT"]
    ],
    pe: [
      ["clinical_dvt_signs", 3, "Clinical signs of DVT (leg swelling and deep-vein tenderness)"],
      ["pe_most_likely", 3, "Alternative diagnosis is less likely than PE"],
      ["heart_rate_100", 1.5, "Heart rate >100 beats/min"],
      ["immobilization_surgery", 1.5, "Immobilization ≥3 days, or surgery within 4 weeks"],
      ["previous_dvt_pe", 1.5, "Previous DVT or PE"],
      ["hemoptysis", 1, "Hemoptysis"],
      ["malignancy", 1, "Active malignancy (treatment within 6 months or palliative)"]
    ],
    geneva: [
      ["previous_dvt_pe", 3, "Previous DVT or PE"],
      ["heart_rate_75_94", 3, "Heart rate 75–94 beats/min"],
      ["heart_rate_95_plus", 5, "Heart rate ≥95 beats/min"],
      ["surgery_fracture_1mo", 2, "Surgery or lower-limb fracture within one month"],
      ["hemoptysis", 2, "Hemoptysis"],
      ["active_cancer", 2, "Active cancer"],
      ["unilateral_leg_pain", 3, "Unilateral lower-limb pain"],
      ["pain_on_palpation", 4, "Deep venous palpation pain and unilateral edema"],
      ["age_over_65", 1, "Age >65 years"]
    ]
  });

  function calculate(type, selected) {
    if (!Object.prototype.hasOwnProperty.call(criteria, type)) {
      throw new Error("Unknown scoring rule");
    }
    if (!selected || typeof selected !== "object" || Array.isArray(selected)) {
      throw new Error("Criteria must be an object");
    }
    const known = new Set(criteria[type].map(function (row) { return row[0]; }));
    Object.keys(selected).forEach(function (key) {
      if (!known.has(key) || typeof selected[key] !== "boolean") {
        throw new Error("Invalid criterion: " + key);
      }
    });
    if (type === "geneva" && selected.heart_rate_75_94 && selected.heart_rate_95_plus) {
      throw new Error("Select only one Geneva heart-rate range");
    }
    const met = criteria[type].filter(function (row) { return selected[row[0]] === true; });
    const score = met.reduce(function (sum, row) { return sum + row[1]; }, 0);
    let two, three, next;
    if (type === "dvt") {
      two = score <= 1 ? "DVT unlikely" : "DVT likely";
      three = score <= 0 ? "Low probability" : score <= 2 ? "Moderate probability" : "High probability";
      next = score <= 1
        ? "DVT unlikely: follow the D-dimer pathway in the appropriate clinical context. A positive D-dimer generally requires ultrasound."
        : "DVT likely: arrange proximal venous ultrasound. A negative initial scan may require further testing per the diagnostic pathway.";
    } else if (type === "pe") {
      two = score <= 4 ? "PE unlikely" : "PE likely";
      three = score < 2 ? "Low probability" : score <= 6 ? "Moderate probability" : "High probability";
      next = score <= 4
        ? "PE unlikely: consider an appropriate D-dimer strategy. A positive result requires further evaluation."
        : "PE likely: obtain appropriate diagnostic imaging (usually CTPA, or V/Q when indicated).";
    } else {
      two = score <= 5 ? "PE unlikely" : "PE likely";
      three = score <= 3 ? "Low probability" : score <= 10 ? "Moderate probability" : "High probability";
      next = "Revised Geneva estimates clinical pretest probability; use with a validated diagnostic pathway. Do not diagnose or exclude PE using the score alone.";
    }
    return { score: score, twoTier: two, threeTier: three, next: next, met: met };
  }

  const api = { criteria: criteria, calculate: calculate };
  if (typeof module !== "undefined" && module.exports) module.exports = api;
  if (root) root.WellsCalculator = api;
})(typeof window !== "undefined" ? window : null);
