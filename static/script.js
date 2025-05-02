function addLine() {
  const div = document.createElement('div');
  div.className = 'taf-line';
  div.innerHTML = `
    <h3>Forecast Line</h3>
    <label>Type:</label>
    <select name="type[]" onchange="adjustOptionalFields(this)">
      <option value="BECMG">BECMG</option>
      <option value="TEMPO">TEMPO</option>
    </select>
    <label>Period (DDHH/DDHH):</label>
    <input type="text" name="period[]" placeholder="0520/0521" required>
    <label class="wind-label">Wind:</label>
    <input type="text" name="wind[]" placeholder="18012KT or 18015G25KT" required>
    <label class="vis-label">Visibility:</label>
    <input type="text" name="vis[]" placeholder="7SM" required>
    <label class="wx-label">Weather:</label>
    <input type="text" name="wx[]" placeholder="RA">
    <label class="clouds-label">Clouds:</label>
    <input type="text" name="clouds[]" placeholder="BKN050" required>
    <label class="alt-label">Altimeter:</label>
    <input type="text" name="altimeter[]" placeholder="2986" required>
    <label>Icing (optional):</label>
    <select name="icing_type[]">
      <option value="">None</option>
      <option value="0">0 Trace </option>
      <option value="1">1 LGT Mixed</option>
      <option value="2">2 LGT Rime In Cloud</option>
      <option value="3">3 LGT Clear In Precipitation</option>
      <option value="4">4 MDT Mixed</option>
      <option value="5">5 MDT Rime In Cloud</option>
      <option value="6">6 MDT Clear In Precipitation</option>
      <option value="7">7 SVR Mixed</option>
      <option value="8">8 SVR Rime In Cloud</option>
      <option value="9">9 SVR Clear In Precipitation</option>
    </select>
    <input type="text" name="icing[]" placeholder="Base&Depth(BBBD)">
    <label>Turbulence (optional):</label>
    <select name="turbulence_type[]">
      <option value="">None</option>
      <option value="0">0 None</option>
      <option value="1">1 LGT TURB</option>
      <option value="2">2 MDT TURB in clear, occasional</option>
      <option value="3">3 MDT TURB in clear, frequent</option>
      <option value="4">4 MDT TURB in cloud, occasional</option>
      <option value="5">5 MDT TURB in cloud, frequent</option>
      <option value="6">6 SVR TURB in clear, occasional</option>
      <option value="7">7 SVR TURB in clear, frequent</option>
      <option value="8">8 SVR TURB in cloud, occasional</option>
      <option value="9">9 SVR TURB in cloud, frequent</option>
      <option value="X">X Extreme turbulence</option>
    </select>
    <input type="text" name="turbulence[]" placeholder="Base&Depth(BBBD)">
    <button type="button" onclick="this.parentElement.remove()">Delete Line</button>
  `;
  document.getElementById('taf-lines').appendChild(div);
}

function adjustOptionalFields(selectEl) {
  const parent = selectEl.closest('.taf-line');
  const isTempo = selectEl.value === 'TEMPO';
  const fields = ['wind', 'vis', 'clouds', 'altimeter'];
  const labelMap = {
    wind: 'wind-label',
    vis: 'vis-label',
    wx: 'wx-label',
    clouds: 'clouds-label',
    altimeter: 'alt-label'
  };

  fields.forEach(field => {
    const input = parent.querySelector(`input[name="${field}[]"]`);
    const label = parent.querySelector(`.${labelMap[field]}`);
    if (input) {
      if (isTempo) {
        input.removeAttribute('required');
        input.classList.add('optional');
        if (label) label.classList.add('optional');
      } else {
        input.setAttribute('required', '');
        input.classList.remove('optional');
        if (label) label.classList.remove('optional');
      }
    }
  });
}

window.addEventListener("load", function () {
  const form = document.querySelector("form");
  form.addEventListener("submit", function (e) {
    const winds = document.querySelectorAll('input[name="wind[]"]');
    for (let i = 0; i < winds.length; i++) {
      const wind = winds[i].value.toUpperCase();
      const isGusting = wind.includes("G");
      const steady = /^\d{5}KT$/;
      const gusting = /^\d{5}G\d{2}KT$/;

      if (wind && !((isGusting && gusting.test(wind)) || (!isGusting && steady.test(wind)))) {
        e.preventDefault();
        alert(`Line ${i + 1}: Invalid wind format "${wind}". Must be 5 digits + KT or 5 digits + G + 2 digits + KT.`);
        winds[i].focus();
        return;
      }
    }
  });
});
