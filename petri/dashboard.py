DASHBOARD_HTML = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Petri</title>
<style>
  :root { --line:#e5e7eb; --muted:#6b7280; --bg:#fafafa; --accent:#111827; }
  * { box-sizing:border-box; }
  body { margin:0; font:14px/1.5 system-ui,-apple-system,sans-serif; color:#111827; background:var(--bg); }
  header { padding:20px 24px; border-bottom:1px solid var(--line); background:#fff; }
  header h1 { margin:0; font-size:18px; letter-spacing:-0.01em; }
  header span { color:var(--muted); }
  main { padding:24px; max-width:1100px; margin:0 auto; }
  .tabs { display:flex; gap:8px; margin-bottom:16px; }
  .tabs button { padding:6px 14px; border:1px solid var(--line); background:#fff; border-radius:6px; cursor:pointer; font:inherit; }
  .tabs button.active { background:var(--accent); color:#fff; border-color:var(--accent); }
  table { width:100%; border-collapse:collapse; background:#fff; border:1px solid var(--line); border-radius:8px; overflow:hidden; }
  th, td { text-align:left; padding:10px 12px; border-bottom:1px solid var(--line); white-space:nowrap; }
  th { font-size:12px; text-transform:uppercase; letter-spacing:0.04em; color:var(--muted); background:#fff; }
  tbody tr:last-child td { border-bottom:none; }
  tbody tr.clickable { cursor:pointer; }
  tbody tr.clickable:hover { background:#f9fafb; }
  .mono { font-family:ui-monospace,SFMono-Regular,Menlo,monospace; }
  .pill { display:inline-block; padding:2px 8px; border-radius:999px; font-size:12px; background:#f3f4f6; }
  .pill.running { background:#dcfce7; color:#166534; }
  .pill.error { background:#fee2e2; color:#991b1b; }
  .pill.deleted { background:#f3f4f6; color:#9ca3af; }
  .pager { display:flex; gap:8px; align-items:center; margin-top:12px; }
  .pager button { padding:5px 12px; border:1px solid var(--line); background:#fff; border-radius:6px; cursor:pointer; font:inherit; }
  .pager button:disabled { opacity:0.4; cursor:default; }
  .panel { margin-top:24px; }
  .panel h2 { font-size:14px; margin:0 0 10px; }
  .ok { color:#166534; }
  .fail { color:#991b1b; }
  .empty { color:var(--muted); padding:16px 0; }
</style>
</head>
<body>
<header><h1>Petri <span>· dashboard</span></h1></header>
<main>
  <div class="tabs">
    <button id="tab-active" class="active" onclick="show('active')">Active</button>
    <button id="tab-history" onclick="show('history')">History</button>
  </div>
  <div id="list"></div>
  <div class="pager" id="pager" style="display:none">
    <button id="prev" onclick="page(-1)">Prev</button>
    <span class="mono" id="page-label"></span>
    <button id="next" onclick="page(1)">Next</button>
  </div>
  <div class="panel" id="runs"></div>
</main>
<script>
  const LIMIT = 50;
  let view = "active";
  let offset = 0;

  const fmt = ts => ts ? ts.replace("T", " ").slice(0, 19) : "—";
  const shortId = id => id.length > 18 ? id.slice(0, 18) + "…" : id;

  function statusPill(s) {
    const cls = ["running","error","deleted"].includes(s) ? s : "";
    return `<span class="pill ${cls}">${s}</span>`;
  }

  function renderSandboxes(rows) {
    if (!rows.length) return `<p class="empty">No sandboxes.</p>`;
    const body = rows.map(s => `
      <tr class="clickable" onclick="showRuns('${s.id}')">
        <td class="mono" title="${s.id}">${shortId(s.id)}</td>
        <td>${s.language}</td>
        <td>${statusPill(s.status)}</td>
        <td>${s.agent || "—"}</td>
        <td>${s.created_by}</td>
        <td class="mono">${fmt(s.created_at)}</td>
        <td class="mono">${fmt(s.expires_at)}</td>
      </tr>`).join("");
    return `<table>
      <thead><tr><th>ID</th><th>Lang</th><th>Status</th><th>Agent</th><th>Created by</th><th>Created</th><th>Expires</th></tr></thead>
      <tbody>${body}</tbody></table>`;
  }

  async function load() {
    const url = view === "active"
      ? "/v1/sandboxes/active"
      : `/v1/sandboxes?limit=${LIMIT}&offset=${offset}`;
    const rows = await (await fetch(url)).json();
    document.getElementById("list").innerHTML = renderSandboxes(rows);

    const pager = document.getElementById("pager");
    if (view === "history") {
      pager.style.display = "flex";
      document.getElementById("prev").disabled = offset === 0;
      document.getElementById("next").disabled = rows.length < LIMIT;
      document.getElementById("page-label").textContent =
        `${offset + 1}–${offset + rows.length}`;
    } else {
      pager.style.display = "none";
    }
  }

  function show(v) {
    view = v;
    offset = 0;
    document.getElementById("runs").innerHTML = "";
    document.getElementById("tab-active").classList.toggle("active", v === "active");
    document.getElementById("tab-history").classList.toggle("active", v === "history");
    load();
  }

  function page(dir) {
    offset = Math.max(0, offset + dir * LIMIT);
    load();
  }

  async function showRuns(id) {
    const runs = await (await fetch(`/v1/sandboxes/${id}/runs`)).json();
    const panel = document.getElementById("runs");
    if (!runs.length) {
      panel.innerHTML = `<h2>Runs · ${shortId(id)}</h2><p class="empty">No runs yet.</p>`;
      return;
    }
    const body = runs.map(r => `
      <tr>
        <td class="mono">${r.id}</td>
        <td class="mono">${fmt(r.started_at)}</td>
        <td class="mono">${r.duration_ms ?? "—"} ms</td>
        <td class="${r.exit_code === 0 ? "ok" : "fail"}">${r.exit_code}</td>
        <td>${r.error || "—"}</td>
      </tr>`).join("");
    panel.innerHTML = `<h2>Runs · <span class="mono">${shortId(id)}</span></h2>
      <table>
        <thead><tr><th>Run</th><th>Started</th><th>Duration</th><th>Exit</th><th>Error</th></tr></thead>
        <tbody>${body}</tbody></table>`;
  }

  load();
</script>
</body>
</html>"""
