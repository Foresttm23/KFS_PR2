function toggleAdmin() {
  let admin_panel_button = document.getElementById("admin");
  let admin_panel = document.getElementById("adminPanel");
  let user_panel = document.getElementById("userPanel");

  if (admin_panel.style.display === "none") {
    admin_panel.style.display = "block";
    user_panel.style.display = "none";
    admin_panel_button.textContent = "Вийти з адмін-панелі";
  } else {
    admin_panel.style.display = "none";
    user_panel.style.display = "block";
    admin_panel_button.textContent = "Показати адмін-панель";
  }
}

function toggle_data_generator_js() {
  fetch("/toggle_data_generator", { method: "POST" })
    .then((response) => response.json())
    .then((data) => {
      let btn = document.getElementById("data_generator");
      if (data.status === "started") {
        btn.innerText = "Зупинити процес";
      } else {
        btn.innerText = "Запустити процес";
      }
    });
}

function insert_meter_data() {
  let data = {
    meter_id: parseInt(document.getElementById("meter_id").value) || 0,
    day_reading: parseInt(document.getElementById("day_reading").value) || 0,
    night_reading:
      parseInt(document.getElementById("night_reading").value) || 0,
    type: "insert",
  };

  fetch("/send_reading_py", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  })
    .then((response) => response.json())
    .then((data) => {
      document.getElementById("meter_data").innerHTML = `
                <h3><b>${data.message}</b></h3>
            `;
    })
    .catch(console.error);
}
// ---------------------------------------------------------------------------------------
function update_meter_data_js() {
  let data = {
    id_update: parseInt(document.getElementById("id_update").value) || 0,
    day_reading_update:
      parseInt(document.getElementById("day_reading_update").value) || 0,
    night_reading_update:
      parseInt(document.getElementById("night_reading_update").value) || 0,
    bill_update: parseInt(document.getElementById("bill_update").value) || 0,
    type: "update",
  };

  fetch("/send_reading_py", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  })
    .then((response) => response.json())
    .then((data) => {
      document.getElementById("update_meter_data").innerHTML = `
                <h3><b>${data.message}</b></h3>
            `;
    })
    .catch(console.error);
}

function delete_meter_data_js() {
  let data = {
    id_delete: parseInt(document.getElementById("id_delete").value) || 0,
    type: "delete",
  };

  fetch("/send_reading_py", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  })
    .then((response) => response.json())
    .then((data) => {
      document.getElementById("delete_meter_data").innerHTML = `
                <h3><b>${data.message}</b></h3>
            `;
    })
    .catch(console.error);
}

// ---------------------------------------------------------------------------------------

function insert_tarriffs() {
  let data = {
    day_tariff: parseFloat(document.getElementById("day_tariff").value) || 0,
    night_tariff:
      parseFloat(document.getElementById("night_tariff").value) || 0,
    day_adjustment:
      parseInt(document.getElementById("day_adjustment").value) || 0,
    night_adjustment:
      parseInt(document.getElementById("night_adjustment").value) || 0,
    type: "tariffs",
  };

  fetch("/send_reading_py", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  })
    .then((response) => response.json())
    .then((data) => {
      document.getElementById("new_tarrifs").innerHTML = `
                <h3><b>${data.message}</b></h3>
            `;
    })
    .catch(console.error);
}

function get_tables_data_js() {
  fetch("/get_tables_data")
    .then((response) => response.json())
    .then((data) => {
      const tariffs = data.tariffs;
      const meters_history = data.meters_history;

      // Виведення даних таблиці tariffs
      const tariffsTable = document.getElementById("tariffs_table");
      tariffsTable.innerHTML = `
                                <table>
                                  <thead>
                                    <tr>
                                      <th>ID</th>
                                      <th>day_tariff</th>
                                      <th>night_tariff</th>
                                      <th>day_adjustment</th>
                                      <th>night_adjustment</th>
                                      <th>date</th>
                                    </tr>
                                  </thead>
                                  <tbody></tbody>
                                </table>
                              `;
      const tariffsBody = tariffsTable.querySelector("tbody");
      tariffs.forEach((tariff) => {
        const row = document.createElement("tr");
        row.innerHTML = ` 
                          <td>${tariff.id}</td>
                          <td>${tariff.day_tariff}</td>
                          <td>${tariff.night_tariff}</td>
                          <td>${tariff.day_adjustment}</td>
                          <td>${tariff.night_adjustment}</td>
                          <td>${tariff.date}</td>
                        `;
        tariffsBody.appendChild(row);
      });

      // Виведення даних таблиці meters_history
      const metersHistoryTable = document.getElementById(
        "meters_history_table"
      );
      metersHistoryTable.innerHTML = `
                                      <table>
                                        <thead>
                                          <tr>
                                            <th>ID</th>
                                            <th>meter_id</th>
                                            <th>day_reading</th>
                                            <th>night_reading</th>
                                            <th>bill</th>
                                            <th>tariff_id</th>
                                            <th>date</th>
                                          </tr>
                                        </thead>
                                        <tbody></tbody>
                                      </table>
                                    `;
      const metersHistoryBody = metersHistoryTable.querySelector("tbody");
      meters_history.forEach((meter) => {
        const row = document.createElement("tr");
        row.innerHTML = `
                          <td>${meter.id}</td>
                          <td>${meter.meter_id}</td>
                          <td>${meter.day_reading}</td>
                          <td>${meter.night_reading}</td>
                          <td>${meter.bill}</td>
                          <td>${meter.tariff_id}</td>
                          <td>${meter.date}</td>
                        `;
        metersHistoryBody.appendChild(row);
      });
    })
    .catch(console.error);
}

function get_meter_preview() {
  let data = {
    meter_id: parseInt(document.getElementById("meter_id").value) || 0,
  };

  fetch("/get_meter_preview_py", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  })
    .then((response) => response.json())
    .then((data) => {
      if (data) {
        document.getElementById("day_reading_preview").innerHTML = `
          <h3>Минулий показник ДНЯ для лічильника <b>${data.meter_id}: ${data.day_reading}</b></h3>
        `;
        document.getElementById("night_reading_preview").innerHTML = `
          <h3>Минулий показник НОЧІ для лічильника <b>${data.meter_id}: ${data.night_reading}</b></h3>
        `;
      } else {
        document.getElementById(
          "day_reading_preview"
        ).innerHTML = `<h3>Немає даних</h3>`;
        document.getElementById(
          "night_reading_preview"
        ).innerHTML = `<h3>Немає даних</h3>`;
      }
    })
    .catch(console.error);
}

// В реальному часі
document
  .getElementById("meter_id")
  .addEventListener("input", get_meter_preview);

// Фільтрація таблиць
function filter_tariffs() {
  const searchValue = document
    .getElementById("tariffs_search")
    .value.toLowerCase();
  const rows = document.querySelectorAll("#tariffs_table tbody tr");

  rows.forEach((row) => {
    const rowData = row.innerText.toLowerCase();
    row.style.display = rowData.includes(searchValue) ? "" : "none"; // Показати або приховати рядок
  });
}

function filter_meters_history() {
  const searchValue = document
    .getElementById("meters_history_search")
    .value.toLowerCase();
  const rows = document.querySelectorAll("#meters_history_table tbody tr");

  rows.forEach((row) => {
    const rowData = row.innerText.toLowerCase();
    row.style.display = rowData.includes(searchValue) ? "" : "none"; // Показати або приховати рядок
  });
}

// В реальному часі
document
  .getElementById("tariffs_search")
  .addEventListener("input", filter_tariffs);
document
  .getElementById("meters_history_search")
  .addEventListener("input", filter_meters_history);
