"use strict";
const assert = require("node:assert/strict");
const { calculate, criteria } = require("./calculator.js");

function classify(type, input) { return calculate(type, input); }

assert.equal(classify("dvt", {}).score, 0);
assert.equal(classify("dvt", { alternative_diagnosis: true }).score, -2);
assert.equal(classify("dvt", { active_cancer: true }).twoTier, "DVT unlikely");
assert.equal(classify("dvt", { active_cancer: true, previous_dvt: true }).twoTier, "DVT likely");
assert.equal(classify("dvt", { active_cancer: true, previous_dvt: true }).threeTier, "Moderate probability");
assert.equal(classify("dvt", { active_cancer: true, previous_dvt: true, pitting_edema: true }).threeTier, "High probability");
assert.equal(classify("pe", { clinical_dvt_signs: true, hemoptysis: true }).score, 4);
assert.equal(classify("pe", { clinical_dvt_signs: true, hemoptysis: true }).twoTier, "PE unlikely");
assert.equal(classify("pe", { clinical_dvt_signs: true, heart_rate_100: true }).twoTier, "PE likely");
assert.equal(classify("pe", { heart_rate_100: true }).threeTier, "Low probability");
assert.equal(classify("pe", { hemoptysis: true, malignancy: true }).threeTier, "Moderate probability");
assert.equal(classify("pe", { clinical_dvt_signs: true, pe_most_likely: true, hemoptysis: true }).threeTier, "High probability");
assert.equal(classify("geneva", { age_over_65: true, previous_dvt_pe: true }).threeTier, "Moderate probability");
assert.equal(classify("geneva", { heart_rate_95_plus: true, pain_on_palpation: true }).threeTier, "Moderate probability");
assert.equal(classify("geneva", { heart_rate_95_plus: true, pain_on_palpation: true, active_cancer: true }).threeTier, "High probability");
assert.equal(classify("geneva", { heart_rate_95_plus: true, pain_on_palpation: true, active_cancer: true }).twoTier, "PE likely");
assert.throws(() => classify("geneva", { heart_rate_75_94: true, heart_rate_95_plus: true }), /heart-rate/);
assert.throws(() => classify("dvt", { typo: true }), /Invalid criterion/);
assert.throws(() => classify("pe", { hemoptysis: "yes" }), /Invalid criterion/);
assert.equal(criteria.dvt.length, 10);
assert.equal(criteria.pe.length, 7);
assert.equal(criteria.geneva.length, 9);
console.log("21 browser-scoring checks passed");
