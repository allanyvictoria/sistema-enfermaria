// =========================================================
// Painel (Dashboard) - indicadores e graficos do mes
// =========================================================

let _chartsAtivos = [];

function destruirCharts() {
  _chartsAtivos.forEach(c => c.destroy());
  _chartsAtivos = [];
}

async function renderDashboard() {
  const usuario = AuthStore.getUsuario();
  const content = renderAppShell({
    titulo: `Olá, ${usuario.nome.split(" ")[0]}`,
    subtitulo: "Aqui está o resumo dos atendimentos deste mês."
  });

  content.innerHTML = loaderHtml("Preparando o painel...");

  let dados;
  try {
    dados = await Api.dashboard.resumo();
  } catch (err) {
    if (!document.body.contains(content)) return; // 👈 ADICIONADO
    content.innerHTML = emptyStateHtml("Não foi possível carregar o painel", err.message);
    return;
  }

  if (!document.body.contains(content)) return; // 👈 ADICIONADO

  const ind = dados.indicadores || {};
  const g = dados.graficos || {};

  content.innerHTML = `
    <div class="stat-grid">
      <div class="stat-card">
        <div class="icon-wrap">${Icon.clipboardCross}</div>
        <div>
          <div class="stat-value">${ind.atendimentos_mes ?? 0}</div>
          <div class="stat-label">Atendimentos no mês</div>
        </div>
      </div>
      <div class="stat-card mint">
        <div class="icon-wrap">${Icon.kids}</div>
        <div>
          <div class="stat-value">${ind.criancas_atendidas ?? 0}</div>
          <div class="stat-label">Crianças atendidas</div>
        </div>
      </div>
      <div class="stat-card coral">
        <div class="icon-wrap">${Icon.door}</div>
        <div>
          <div class="stat-value">${ind.salas_envolvidas ?? 0}</div>
          <div class="stat-label">Salas envolvidas</div>
        </div>
      </div>
    </div>

    <div class="chart-grid">
      <div class="card">
        <h3>${Icon.reportChart} Atendimentos ao longo do mês</h3>
        <canvas id="chart-por-dia" height="90"></canvas>
      </div>
      <div class="card">
        <h3>${Icon.bandage} Por tipo de ocorrência</h3>
        <canvas id="chart-por-tipo" height="90"></canvas>
      </div>
    </div>

    <div class="chart-row-2">
      <div class="card">
        <h3>${Icon.door} Por professor e turma</h3>
        <canvas id="chart-por-sala" height="100"></canvas>
      </div>
      <div class="card">
        <h3>${Icon.calendar} Por turno</h3>
        <canvas id="chart-por-turno" height="100"></canvas>
      </div>
    </div>
  `;

  destruirCharts();

  const paletaAzuis = ["#57BCF3", "#2FA1DE", "#8FD1FB", "#1C84C0", "#BFE3FD", "#166A9C"];
  const paletaMista = ["#57BCF3", "#FF9E80", "#4FD1A5", "#FFC24B", "#FF6B8B", "#8FD1FB"];

  if (window.Chart) {
    Chart.defaults.font.family = "Nunito, sans-serif";
    Chart.defaults.color = "#5C7A8C";

    // Por dia (linha)
    const porDia = g.por_dia || [];
    _chartsAtivos.push(new Chart(document.getElementById("chart-por-dia"), {
      type: "line",
      data: {
        labels: porDia.map(d => formatarData(d.data)),
        datasets: [{
          label: "Atendimentos",
          data: porDia.map(d => d.quantidade),
          borderColor: "#2FA1DE",
          backgroundColor: "rgba(87,188,243,0.18)",
          fill: true,
          tension: 0.35,
          pointBackgroundColor: "#2FA1DE",
          pointRadius: 4
        }]
      },
      options: {
        plugins: { legend: { display: false } },
        scales: { y: { beginAtZero: true, ticks: { precision: 0 } } }
      }
    }));

    // Por tipo (doughnut)
    const porTipo = g.por_tipo || [];
    _chartsAtivos.push(new Chart(document.getElementById("chart-por-tipo"), {
      type: "doughnut",
      data: {
        labels: porTipo.map(t => t.tipo),
        datasets: [{ data: porTipo.map(t => t.quantidade), backgroundColor: paletaMista, borderWidth: 3, borderColor: "#fff" }]
      },
      options: { plugins: { legend: { position: "bottom", labels: { boxWidth: 12, padding: 12 } } }, cutout: "62%" }
    }));

    // Por sala (barra)
    const porSala = g.por_sala || [];
    _chartsAtivos.push(new Chart(document.getElementById("chart-por-sala"), {
      type: "bar",
      data: {
        labels: porSala.map(s => s.sala),
        datasets: [{ label: "Atendimentos", data: porSala.map(s => s.quantidade), backgroundColor: paletaAzuis, borderRadius: 8, maxBarThickness: 46 }]
      },
      options: { plugins: { legend: { display: false } }, scales: { y: { beginAtZero: true, ticks: { precision: 0 } } } }
    }));

    // Por turno (pizza)
    const porTurno = g.por_turno || [];
    _chartsAtivos.push(new Chart(document.getElementById("chart-por-turno"), {
      type: "pie",
      data: {
        labels: porTurno.map(t => t.turno),
        datasets: [{ data: porTurno.map(t => t.quantidade), backgroundColor: ["#FFC24B", "#57BCF3", "#4FD1A5"], borderWidth: 3, borderColor: "#fff" }]
      },
      options: { responsive: true,
        aspectRatio: 2,
        plugins: { 
          legend: {
            position: "bottom", labels: { 
              boxWidth: 12, padding: 12 
            } 
          } 
        } 
      }
    }));
  }
}
