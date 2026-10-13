"use strict";

(function () {
  const calculator = window.WellsCalculator;
  if (!calculator) throw new Error("Scoring library is unavailable");

  const names = { dvt: "Wells DVT criteria", pe: "Wells PE criteria", geneva: "Revised Geneva criteria" };
  const state = { dvt: {}, pe: {}, geneva: {} };
  let current = "dvt";
  const list = document.getElementById("criteria-list");

  function render() {
    document.querySelectorAll("[data-score]").forEach(function (button) {
      const active = button.dataset.score === current;
      button.classList.toggle("active", active);
      button.setAttribute("aria-pressed", String(active));
    });
    document.getElementById("criteria-legend").textContent = names[current];
    list.replaceChildren();
    calculator.criteria[current].forEach(function (criterion) {
      const key = criterion[0], points = criterion[1], description = criterion[2];
      const label = document.createElement("label");
      label.className = "criterion";
      const input = document.createElement("input");
      input.type = "checkbox";
      input.name = key;
      input.checked = Boolean(state[current][key]);
      input.addEventListener("change", function () {
        state[current][key] = input.checked;
        if (current === "geneva" && input.checked) {
          const opposite = key === "heart_rate_75_94" ? "heart_rate_95_plus"
            : key === "heart_rate_95_plus" ? "heart_rate_75_94" : null;
          if (opposite) {
            state.geneva[opposite] = false;
            const other = list.querySelector('input[name="' + opposite + '"]');
            if (other) other.checked = false;
          }
        }
        update();
      });
      const text = document.createElement("span");
      text.className = "desc";
      text.textContent = description;
      const point = document.createElement("span");
      point.className = "points" + (points < 0 ? " negative" : "");
      point.textContent = (points > 0 ? "+" : "") + String(points);
      label.append(input, text, point);
      list.append(label);
    });
    update();
  }

  function update() {
    const result = calculator.calculate(current, state[current]);
    document.getElementById("score").textContent = String(result.score);
    document.getElementById("two-tier").textContent = result.twoTier;
    document.getElementById("three-tier").textContent = result.threeTier;
    document.getElementById("guidance").textContent = result.next;
  }

  document.querySelectorAll("[data-score]").forEach(function (button) {
    button.addEventListener("click", function () {
      current = button.dataset.score;
      render();
    });
  });
  document.getElementById("clear").addEventListener("click", function () {
    state[current] = {};
    render();
  });
  render();
})();
