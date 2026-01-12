import pandas as pd
from pathlib import Path
from datetime import datetime

FILES = {
    "Mac Araçatuba Recepção e Conferência.xlsx": "Araçatuba",
    "Mac Birigui Recepção e Conferência.xlsx": "Birigui",
    "Mac Prudente Recepção e Conferência.xlsx": "Prudente",
}

OUTPUT_XLSX = "Acompanhamento_recepcao_mac.xlsx"
OUTPUT_HTML = "Acompanhamento_recepcao_mac.html"


def normalize_header(value):
    if pd.isna(value):
        return ""
    return str(value).strip().upper().replace("\n", " ")


def find_col(columns, targets):
    targets_upper = [t.upper() for t in targets]
    for col in columns:
        col_norm = normalize_header(col)
        if col_norm in targets_upper:
            return col
    return None


def extract_table(path, city):
    df = pd.read_excel(path, sheet_name=-1, header=None)
    header_idx = None
    max_scan = min(len(df), 25)
    for i in range(max_scan):
        row_norm = [normalize_header(v) for v in df.iloc[i].tolist()]
        if ("N.F." in row_norm or "NF" in row_norm) and "DATA" in row_norm:
            header_idx = i
            break
    if header_idx is None:
        raise ValueError(f"Header row not found in {path}")

    header = df.iloc[header_idx].tolist()
    data = df.iloc[header_idx + 1 :].copy()
    data.columns = header
    data = data.dropna(how="all")

    cols = list(data.columns)
    col_nf = find_col(cols, ["N.F.", "NF"])
    col_data = find_col(cols, ["DATA"])
    col_nome = find_col(cols, ["NOME DO FORNECEDOR"])
    col_fin = find_col(cols, ["FIN.", "FIN"])
    col_lib = find_col(cols, ["LIB.", "LIB"])

    if col_nf is None or col_data is None or col_nome is None:
        raise ValueError(f"Required columns not found in {path}")

    out = pd.DataFrame(
        {
            "CIDADE": city,
            "N.F.": data[col_nf],
            "DATA": data[col_data],
            "NOME DO FORNECEDOR": data[col_nome],
            "FIN.": data[col_fin] if col_fin else "",
            "LIB.": data[col_lib] if col_lib else "",
        }
    )

    out = out.dropna(
        how="all", subset=["N.F.", "DATA", "NOME DO FORNECEDOR"]
    )
    return out


def format_nf(series):
    def fix(value):
        if pd.isna(value):
            return ""
        if isinstance(value, float) and value.is_integer():
            return str(int(value))
        return str(value).strip()

    return series.map(fix)


def format_date(series):
    def fix(value):
        if pd.isna(value):
            return ""
        if hasattr(value, "strftime"):
            return value.strftime("%d/%m/%Y")
        return str(value).strip()

    return series.map(fix)


frames = []
for file_name, city in FILES.items():
    frames.append(extract_table(file_name, city))

result = pd.concat(frames, ignore_index=True)

result["N.F."] = format_nf(result["N.F."])
result["DATA"] = format_date(result["DATA"])
result["NOME DO FORNECEDOR"] = (
    result["NOME DO FORNECEDOR"].fillna("").astype(str).str.strip()
)
result["FIN."] = result["FIN."].fillna("").astype(str).str.strip()
result["LIB."] = result["LIB."].fillna("").astype(str).str.strip()

result.to_excel(OUTPUT_XLSX, index=False)

city_values = (
    result["CIDADE"]
    .fillna("")
    .astype(str)
    .str.strip()
    .replace("", pd.NA)
    .dropna()
    .unique()
)
options_html = "\n".join(
    f'      <option value="{city}">{city}</option>' for city in city_values
)

html_table = result.to_html(index=False, border=0, escape=False)
html_table = html_table.replace(
    '<table border="0" class="dataframe">',
    '<table border="0" class="dataframe" id="dados">',
    1,
)
html = f"""<!doctype html>
<html lang=\"pt-br\">
<head>
  <meta charset=\"utf-8\" />
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />
  <title>Acompanhamento Recepção MAC</title>
  <link rel=\"stylesheet\" href=\"https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;500;700&display=swap\">
  <link rel=\"stylesheet\" href=\"https://fonts.googleapis.com/icon?family=Material+Icons\">
  <style>
    * {{
      margin: 0;
      padding: 0;
      box-sizing: border-box;
    }}

    body {{
      font-family: 'Roboto', sans-serif;
      background: #fafafa;
      color: #212121;
      padding: 24px;
      line-height: 1.5;
    }}

    .container {{
      max-width: 1400px;
      margin: 0 auto;
    }}

    header {{
      background: #ffffff;
      padding: 24px;
      border-radius: 8px;
      box-shadow: 0 2px 4px rgba(0,0,0,0.1);
      margin-bottom: 24px;
      display: flex;
      justify-content: space-between;
      align-items: center;
      flex-wrap: wrap;
      gap: 16px;
    }}

    .header-content {{
      flex: 1;
    }}

    h1 {{
      font-size: 28px;
      font-weight: 500;
      color: #212121;
      margin-bottom: 8px;
    }}

    .subtitle {{
      color: #757575;
      font-size: 14px;
    }}

    .last-update {{
      display: flex;
      align-items: center;
      gap: 8px;
      color: #757575;
      font-size: 13px;
      white-space: nowrap;
    }}

    .last-update .material-icons {{
      font-size: 18px;
      color: #9e9e9e;
    }}

    .update-time {{
      color: #424242;
      font-weight: 500;
    }}

    .controls {{
      background: #ffffff;
      padding: 20px 24px;
      border-radius: 8px;
      box-shadow: 0 2px 4px rgba(0,0,0,0.1);
      margin-bottom: 24px;
      display: flex;
      align-items: center;
      gap: 16px;
      flex-wrap: wrap;
    }}

    .controls label {{
      font-weight: 500;
      color: #424242;
      font-size: 14px;
    }}

    .controls select {{
      padding: 10px 16px;
      border: 1px solid #e0e0e0;
      border-radius: 4px;
      background: #ffffff;
      font-family: 'Roboto', sans-serif;
      font-size: 14px;
      color: #212121;
      cursor: pointer;
      transition: all 0.2s;
      min-width: 180px;
    }}

    .controls select:hover {{
      border-color: #9e9e9e;
    }}

    .controls select:focus {{
      outline: none;
      border-color: #424242;
    }}

    .stats {{
      display: flex;
      gap: 24px;
      margin-left: auto;
    }}

    .stat-card {{
      display: flex;
      align-items: center;
      gap: 8px;
    }}

    .stat-label {{
      font-size: 12px;
      color: #757575;
      text-transform: uppercase;
      letter-spacing: 0.5px;
    }}

    .stat-value {{
      font-size: 20px;
      font-weight: 500;
      color: #212121;
    }}

    .table-container {{
      background: #ffffff;
      border-radius: 8px;
      box-shadow: 0 2px 4px rgba(0,0,0,0.1);
      overflow: hidden;
    }}

    .table-wrap {{
      overflow-x: auto;
    }}

    table {{
      width: 100%;
      border-collapse: collapse;
    }}

    thead {{
      background: #f5f5f5;
      position: sticky;
      top: 0;
      z-index: 10;
    }}

    thead th {{
      padding: 16px;
      text-align: left;
      font-weight: 500;
      font-size: 13px;
      color: #616161;
      text-transform: uppercase;
      letter-spacing: 0.5px;
      border-bottom: 2px solid #e0e0e0;
    }}

    tbody td {{
      padding: 16px;
      font-size: 14px;
      border-bottom: 1px solid #f5f5f5;
      color: #424242;
    }}

    tbody tr {{
      transition: background-color 0.2s;
    }}

    tbody tr:hover {{
      background: #f9f9f9;
    }}

    /* Cores por cidade */
    tbody tr[data-city="Araçatuba"] {{
      border-left: 4px solid #2196F3;
      background: rgba(33, 150, 243, 0.04);
    }}

    tbody tr[data-city="Araçatuba"]:hover {{
      background: rgba(33, 150, 243, 0.08);
    }}

    tbody tr[data-city="Prudente"] {{
      border-left: 4px solid #4CAF50;
      background: rgba(76, 175, 80, 0.04);
    }}

    tbody tr[data-city="Prudente"]:hover {{
      background: rgba(76, 175, 80, 0.08);
    }}

    tbody tr[data-city="Birigui"] {{
      border-left: 4px solid #FF9800;
      background: rgba(255, 152, 0, 0.04);
    }}

    tbody tr[data-city="Birigui"]:hover {{
      background: rgba(255, 152, 0, 0.08);
    }}

    /* Status badge */
    .status-badge {{
      display: inline-flex;
      align-items: center;
      gap: 4px;
      padding: 4px 12px;
      border-radius: 12px;
      font-size: 12px;
      font-weight: 500;
    }}

    .status-ready {{
      background: #E8F5E9;
      color: #2E7D32;
    }}

    .status-pending {{
      background: #FFF3E0;
      color: #E65100;
    }}

    .status-icon {{
      font-size: 16px;
    }}

    /* Legend */
    .legend {{
      background: #ffffff;
      padding: 16px 24px;
      border-radius: 8px;
      box-shadow: 0 2px 4px rgba(0,0,0,0.1);
      margin-top: 24px;
      display: flex;
      gap: 24px;
      align-items: center;
      flex-wrap: wrap;
    }}

    .legend-title {{
      font-weight: 500;
      color: #424242;
      font-size: 14px;
    }}

    .legend-items {{
      display: flex;
      gap: 20px;
      flex-wrap: wrap;
    }}

    .legend-item {{
      display: flex;
      align-items: center;
      gap: 8px;
      font-size: 13px;
      color: #616161;
    }}

    .legend-color {{
      width: 20px;
      height: 20px;
      border-radius: 3px;
    }}

    .color-aracatuba {{ background: #2196F3; }}
    .color-prudente {{ background: #4CAF50; }}
    .color-birigui {{ background: #FF9800; }}

    @media (max-width: 768px) {{
      body {{ padding: 12px; }}
      h1 {{ font-size: 24px; }}
      header {{ flex-direction: column; align-items: flex-start; }}
      .last-update {{ font-size: 12px; }}
      .controls {{ flex-direction: column; align-items: stretch; }}
      .stats {{ margin-left: 0; width: 100%; justify-content: space-around; }}
      thead th, tbody td {{ padding: 12px 8px; font-size: 12px; }}
    }}
  </style>
</head>
<body>
  <div class=\"container\">
    <header>
      <div class=\"header-content\">
        <h1>Acompanhamento Recepção MAC</h1>
        <div class=\"subtitle\">Sistema de controle de recepção e conferência de mercadorias</div>
      </div>
      <div class=\"last-update\">
        <span class=\"material-icons\">schedule</span>
        <span>Atualizado em <span class=\"update-time\">{datetime.now().strftime('%d/%m/%Y às %H:%M')}</span></span>
      </div>
    </header>

    <div class=\"controls\">
      <label for=\"city-filter\">Cidade:</label>
      <select id=\"city-filter\">
        <option value=\"ALL\">Todas</option>
{options_html}
      </select>

      <label for=\"status-filter\">Status:</label>
      <select id=\"status-filter\">
        <option value=\"ALL\">Todos</option>
        <option value=\"READY\">Prontas</option>
        <option value=\"PENDING\">Pendentes</option>
      </select>

      <label for=\"date-filter\">Período:</label>
      <select id=\"date-filter\">
        <option value=\"ALL\">Todos</option>
        <option value=\"TODAY\">Hoje</option>
        <option value=\"WEEK\">Última semana</option>
        <option value=\"MONTH\">Último mês</option>
        <option value=\"CUSTOM\">Personalizado</option>
      </select>

      <div id=\"custom-date-range\" style=\"display: none; gap: 8px;\">
        <input type=\"date\" id=\"date-start\" style=\"padding: 8px; border: 1px solid #e0e0e0; border-radius: 4px; font-family: 'Roboto', sans-serif; font-size: 14px;\">
        <span style=\"color: #757575;\">até</span>
        <input type=\"date\" id=\"date-end\" style=\"padding: 8px; border: 1px solid #e0e0e0; border-radius: 4px; font-family: 'Roboto', sans-serif; font-size: 14px;\">
      </div>

      <div class=\"stats\">
        <div class=\"stat-card\">
          <div>
            <div class=\"stat-label\">Total</div>
            <div class=\"stat-value\" id=\"total-count\">0</div>
          </div>
        </div>
        <div class=\"stat-card\">
          <div>
            <div class=\"stat-label\">Prontas</div>
            <div class=\"stat-value\" id=\"ready-count\">0</div>
          </div>
        </div>
        <div class=\"stat-card\">
          <div>
            <div class=\"stat-label\">Pendentes</div>
            <div class=\"stat-value\" id=\"pending-count\">0</div>
          </div>
        </div>
      </div>
    </div>

    <div class=\"table-container\">
      <div class=\"table-wrap\">
        {html_table}
      </div>
    </div>

    <div class=\"legend\">
      <span class=\"legend-title\">Legenda:</span>
      <div class=\"legend-items\">
        <div class=\"legend-item\">
          <div class=\"legend-color color-aracatuba\"></div>
          <span>Araçatuba</span>
        </div>
        <div class=\"legend-item\">
          <div class=\"legend-color color-prudente\"></div>
          <span>Prudente</span>
        </div>
        <div class=\"legend-item\">
          <div class=\"legend-color color-birigui\"></div>
          <span>Birigui</span>
        </div>
      </div>
    </div>
  </div>

  <script>
    (function () {{
      var table = document.querySelector("table");
      if (!table) return;

      var headers = table.querySelectorAll("thead th");
      var cityIndex = -1;
      var finIndex = -1;
      var libIndex = -1;

      headers.forEach(function (th, idx) {{
        var text = th.textContent.trim().toUpperCase();
        if (text === "CIDADE") cityIndex = idx;
        if (text === "FIN.") finIndex = idx;
        if (text === "LIB.") libIndex = idx;
      }});

      if (cityIndex === -1) return;

      // Adicionar coluna de status
      var headerRow = table.querySelector("thead tr");
      var statusHeader = document.createElement("th");
      statusHeader.textContent = "STATUS";
      headerRow.appendChild(statusHeader);

      // Processar cada linha
      var rows = Array.prototype.slice.call(table.querySelectorAll("tbody tr"));
      var dataIndex = -1;
      headers.forEach(function (th, idx) {{
        if (th.textContent.trim().toUpperCase() === "DATA") dataIndex = idx;
      }});

      rows.forEach(function (row) {{
        var cells = row.querySelectorAll("td");
        var city = (cells[cityIndex]?.textContent || "").trim();
        var fin = (cells[finIndex]?.textContent || "").trim();
        var lib = (cells[libIndex]?.textContent || "").trim();
        var dateText = (cells[dataIndex]?.textContent || "").trim();

        // Adicionar atributos para filtros
        row.setAttribute("data-city", city);
        row.setAttribute("data-date", dateText);

        // Criar célula de status
        var statusCell = document.createElement("td");
        var isReady = fin !== "" && lib !== "";

        if (isReady) {{
          statusCell.innerHTML = '<span class=\"status-badge status-ready\"><span class=\"material-icons status-icon\">check_circle</span>Pronta</span>';
          row.setAttribute("data-ready", "true");
        }} else {{
          statusCell.innerHTML = '<span class=\"status-badge status-pending\"><span class=\"material-icons status-icon\">pending</span>Pendente</span>';
          row.setAttribute("data-ready", "false");
        }}

        row.appendChild(statusCell);
      }});

      // Controles de filtro
      var cityFilter = document.getElementById("city-filter");
      var statusFilter = document.getElementById("status-filter");
      var dateFilter = document.getElementById("date-filter");
      var customDateRange = document.getElementById("custom-date-range");
      var dateStart = document.getElementById("date-start");
      var dateEnd = document.getElementById("date-end");
      var totalCount = document.getElementById("total-count");
      var readyCount = document.getElementById("ready-count");
      var pendingCount = document.getElementById("pending-count");

      // Função para converter data brasileira para objeto Date
      function parseDate(dateStr) {{
        if (!dateStr) return null;
        var parts = dateStr.split("/");
        if (parts.length === 3) {{
          return new Date(parts[2], parts[1] - 1, parts[0]);
        }}
        return null;
      }}

      // Função para verificar se a data está no intervalo
      function isDateInRange(dateStr, filterType, customStart, customEnd) {{
        if (filterType === "ALL") return true;

        var date = parseDate(dateStr);
        if (!date) return false;

        var today = new Date();
        today.setHours(0, 0, 0, 0);

        if (filterType === "TODAY") {{
          var checkDate = new Date(date);
          checkDate.setHours(0, 0, 0, 0);
          return checkDate.getTime() === today.getTime();
        }}

        if (filterType === "WEEK") {{
          var weekAgo = new Date(today);
          weekAgo.setDate(weekAgo.getDate() - 7);
          return date >= weekAgo && date <= today;
        }}

        if (filterType === "MONTH") {{
          var monthAgo = new Date(today);
          monthAgo.setMonth(monthAgo.getMonth() - 1);
          return date >= monthAgo && date <= today;
        }}

        if (filterType === "CUSTOM" && customStart && customEnd) {{
          var start = new Date(customStart);
          var end = new Date(customEnd);
          end.setHours(23, 59, 59, 999);
          return date >= start && date <= end;
        }}

        return true;
      }}

      function updateStats() {{
        var visibleRows = rows.filter(function (row) {{
          return row.style.display !== "none";
        }});

        var total = visibleRows.length;
        var ready = visibleRows.filter(function (row) {{
          return row.getAttribute("data-ready") === "true";
        }}).length;
        var pending = total - ready;

        totalCount.textContent = total;
        readyCount.textContent = ready;
        pendingCount.textContent = pending;
      }}

      function applyFilters() {{
        var cityValue = cityFilter.value;
        var statusValue = statusFilter.value;
        var dateValue = dateFilter.value;
        var startDate = dateStart.value;
        var endDate = dateEnd.value;

        rows.forEach(function (row) {{
          var city = row.getAttribute("data-city");
          var ready = row.getAttribute("data-ready");
          var dateText = row.getAttribute("data-date");

          var cityMatch = cityValue === "ALL" || city === cityValue;
          var statusMatch = statusValue === "ALL" ||
                           (statusValue === "READY" && ready === "true") ||
                           (statusValue === "PENDING" && ready === "false");
          var dateMatch = isDateInRange(dateText, dateValue, startDate, endDate);

          if (cityMatch && statusMatch && dateMatch) {{
            row.style.display = "";
          }} else {{
            row.style.display = "none";
          }}
        }});

        updateStats();
      }}

      // Mostrar/ocultar campos de data personalizada
      dateFilter.addEventListener("change", function() {{
        if (this.value === "CUSTOM") {{
          customDateRange.style.display = "flex";
        }} else {{
          customDateRange.style.display = "none";
        }}
        applyFilters();
      }});

      cityFilter.addEventListener("change", applyFilters);
      statusFilter.addEventListener("change", applyFilters);
      dateFilter.addEventListener("change", applyFilters);
      dateStart.addEventListener("change", applyFilters);
      dateEnd.addEventListener("change", applyFilters);

      applyFilters();
    }})();
  </script>
</body>
</html>"""

Path(OUTPUT_HTML).write_text(html, encoding="utf-8")
print(f"Gerado: {OUTPUT_XLSX}")
print(f"Gerado: {OUTPUT_HTML}")
