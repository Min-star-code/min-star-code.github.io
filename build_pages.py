"""Write the four project pages from one shared shell.

Standard library only. Run: python3 portfolio-site/build_pages.py
"""

from pathlib import Path

SITE = Path(__file__).resolve().parent
GH = "https://github.com/Min-star-code"

SHELL = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>@@TITLE@@ | Mincheng Li</title>
<meta name="description" content="@@DESC@@">
<script>document.documentElement.classList.add('js')</script>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter+Tight:wght@500;600;700&family=Inter:wght@400;500;600&display=swap" rel="stylesheet">
<link rel="stylesheet" href="../assets/project.css">
</head>
<body>
<nav class="nav" aria-label="Main">
  <strong><a href="../index.html">Mincheng Li</a></strong>
  <span class="links">@@NAV@@</span>
  <a class="pill" href="mailto:mincheng.li@uwaterloo.ca">Email me</a>
</nav>

<main>
  <header class="phead">
    <div class="wash" aria-hidden="true"></div>
    <p class="made rise">@@MADE@@</p>
    <h1 class="rise" style="--i:1">@@TITLE@@</h1>
    <p class="lead rise" style="--i:2">@@LEAD@@</p>
    <div class="cta rise" style="--i:3">@@CTA@@</div>
  </header>

  <div class="wrap">
    <section class="explorer" aria-label="Interactive charts">
      <div class="filters" id="filters"></div>
      <div class="kpis" id="kpis"></div>
      <div class="grid">
@@PANELS@@
      </div>
    </section>
@@PROSE@@
    <nav class="pager" aria-label="Other projects">@@PAGER@@</nav>
  </div>
</main>
<footer>@@FOOT@@</footer>

<script src="../data/@@DATA@@.js"></script>
<script src="../assets/explore.js"></script>
<script>
const { Explorer, filterBar, kpis, bars, cols, heat, dotMap, chrome, int, money, pct, $ } = EX, D = DATA;
chrome();
@@SCRIPT@@
// Panel subtitles that name the current measure
ex.on(() => document.querySelectorAll('[data-mlabel]').forEach(el => el.textContent = ex.m.label));
</script>
</body>
</html>
"""

ORDER = ["ontario", "outbreaks", "ttc", "adventureworks"]
NAMES = {"ontario": "Ontario", "outbreaks": "Outbreaks", "ttc": "TTC", "adventureworks": "AdventureWorks"}
FULL = {
    "ontario": "Ontario infrastructure projects",
    "outbreaks": "Toronto healthcare outbreak records",
    "ttc": "TTC subway delay incidents",
    "adventureworks": "AdventureWorks sales and profitability",
}


def panel(title, body, sub="", note="", wide=False):
    sub = f'<p class="sub">{sub}</p>' if sub else ""
    note = f'<p class="note">{note}</p>' if note else ""
    return f'        <section class="panel{" wide" if wide else ""}"><h2>{title}</h2>{sub}{body}{note}</section>'


def prose(title, body):
    return f'    <section class="prose"><h2>{title}</h2><div>{body}</div></section>'


def table(head, rows, numeric=()):
    th = "".join(f"<th scope=\"col\"{' class=\"n\"' if i in numeric else ''}>{h}</th>" for i, h in enumerate(head))
    tr = "".join("<tr>" + "".join(f"<td{' class=\"n\"' if i in numeric else ''}>{c}</td>" for i, c in enumerate(r)) + "</tr>" for r in rows)
    return f'<div class="scroll"><table class="tbl num"><thead><tr>{th}</tr></thead><tbody>{tr}</tbody></table></div>'


M = '<span data-mlabel></span>'
PAGES = {}

# ---------------------------------------------------------------- Ontario
PAGES["ontario"] = dict(
    desc="Interactive view of 5,935 Ontario infrastructure projects by category, region, status and budget.",
    made="SQL, Python and Tableau Public. October 2026.",
    lead="Where the province's published projects are, what stage they are at, and where the reported budget is concentrated.",
    cta=[("primary", "Open the Tableau dashboard", "https://public.tableau.com/app/profile/mincheng.li/viz/OntarioBuildsInfrastructureProjects"),
         ("ghost", "Read the code", f"{GH}/ontario-infrastructure-analysis"),
         ("ghost", "Read the briefing note", f"{GH}/ontario-infrastructure-analysis/blob/main/reports/briefing_note.md")],
    panels=[
        panel("By category", '<div id="cat"></div>', f"{M} by project category. Click a bar to filter."),
        panel("By region", '<div id="reg"></div>', f"{M} by region."),
        panel("By status", '<div id="sta"></div>', f"{M} by reported status."),
        panel("By target completion year", '<div id="yr"></div>', f"{M} by the year parsed from the completion date.",
              "230 projects have no usable completion year and are not in this chart."),
        panel("Project locations", '<div class="map"><canvas id="map" role="img"></canvas></div><div class="legend"><span><i></i><span id="mapn"></span></span><span><i class="m"></i>All other projects with coordinates</span></div>',
              "Each dot is one project. Dark dots match the current filters.",
              "417 projects have no coordinates and do not appear. For 19 projects with several points, the first is plotted.", wide=True),
    ],
    prose=[
        prose("Cleaning decisions", table(["Issue in the source", "Rows", "Decision"], [
            ["Budget recorded as 0", "2,005", "Treated as not reported, not as a $0 project"],
            ["Completion date in mixed formats (27-Mar, Sep-34, 2026, March 2027)", "5,706", "Reduced to a completion year; one unclear value left empty"],
            ["Completion date \"To Be Determined\"", "229", "Year left empty"],
            ["Region blank or TBD", "626", "Labelled Province-wide / not assigned"],
            ["Status blank", "22", "Labelled Not reported"],
            ["Several coordinates in one cell", "19", "First point kept for mapping, row flagged"],
            ["Coordinates missing", "417", "Left empty"],
            ["Leading or trailing spaces", "1,127 cells", "Trimmed"],
        ], numeric=(1,)) + "<p style=\"margin-top:16px\">No rows are dropped: the clean file has the same 5,935 rows as the source.</p>"),
        prose("What this data cannot show", "<ul><li>This is a list of projects the province chose to publish, not all infrastructure spending.</li>"
              "<li>Budgets are estimated totals over a project's life, not money spent to date, and a third of projects publish none. Category and region totals are lower bounds.</li>"
              "<li>Budget coverage varies from 98% for child care to 20% for recreation, so comparisons between categories are unreliable.</li>"
              "<li>Region totals are not adjusted for population.</li></ul>"),
    ],
    foot='Source: <a href="https://data.ontario.ca/dataset/ontario-builds-key-infrastructure-projects">Ontario Builds: key infrastructure projects</a>, Ontario Data Catalogue, file of 12 June 2026. Contains information licensed under the Open Government Licence – Ontario. Independent analysis, not endorsed by the Government of Ontario.',
    script="""
const Y0 = 2005, years = Array.from({ length: 2046 - Y0 + 1 }, (_, i) => String(Y0 + i));
const ex = Explorer({
  n: D.n, measure: 'projects',
  dims: {
    cat: { label: 'Category', all: 'All categories', values: D.cats, of: i => D.cat[i] },
    reg: { label: 'Region', all: 'All regions', values: D.regs, of: i => D.reg[i] },
    sta: { label: 'Status', all: 'All statuses', values: D.stas, of: i => D.sta[i] },
    yr: { label: 'Completion year', all: 'All years', values: years, of: i => D.yr[i] ? D.yr[i] - Y0 : -1 }
  },
  measures: {
    projects: { label: 'Projects', of: () => 1, fmt: int },
    budget: { label: 'Reported budget', of: i => (D.bud[i] || 0) * 1e6, fmt: money }
  }
});
filterBar($('#filters'), ex, { keys: ['cat', 'reg', 'sta'], count: ex => {
  const n = ex.sum(() => 1), y = ex.f.yr != null ? `Completion year ${years[ex.f.yr]}. ` : '';
  return `${int(n)} of 5,935 projects<small>${y}${ex.active().length ? 'Filtered' : 'No filters applied'}</small>`;
} });
kpis($('#kpis'), ex, [
  ex => [int(ex.sum(() => 1)), 'Projects'],
  ex => { const n = ex.sum(() => 1), b = ex.sum(i => D.bud[i] != null ? 1 : 0); return [n ? pct(b / n, 0) : '0%', 'Publish a budget', `${int(b)} of ${int(n)}`]; },
  ex => [money(ex.sum(i => (D.bud[i] || 0) * 1e6)), 'Reported budget', 'A lower bound'],
  ex => [int(ex.sum(i => D.sta[i] > 0 && D.sta[i] < 3 && D.yr[i] && D.yr[i] < 2026 ? 1 : 0)), 'Past their target year', 'Still planning or under construction']
]);
bars($('#cat'), ex, 'cat'); bars($('#reg'), ex, 'reg'); bars($('#sta'), ex, 'sta');
cols($('#yr'), ex, 'yr', { tick: (i, y) => y % 5 === 0 ? y : '' });
const map = $('#map');
map.addEventListener('drawn', e => $('#mapn').textContent = `${int(e.detail.shown)} matching projects`);
dotMap(map, ex, D.lat, D.lon);
""",
)

# ---------------------------------------------------------------- Outbreaks
RULES = [
    ("R1", "Required fields are present", 0), ("R2", "Setting is one of the seven published values", 0),
    ("R3", "Type is Respiratory, Enteric or Other", 0), ("R4", "End date is not before the start date", 0),
    ("R5", "Start year matches the yearly file it came from", 0), ("R6", "Active flag agrees with the end date", 0),
    ("R7", "No duplicate records", 6), ("R8", "Duration is 90 days or less", 18),
    ("R9", "Causative agent was identified", 671), ("R10", "First agent field names a single agent", 4),
    ("R11", "Outbreak type agrees with the agent", 0), ("R12", "Institution name is complete", 100),
]
PAGES["outbreaks"] = dict(
    desc="Interactive view of 7,029 Toronto healthcare outbreak records, 2016 to 2026, with the data quality checks behind them.",
    made="Python, SQL and Excel. October 2026.",
    lead="Eleven yearly files from Toronto Public Health combined into one validated table of 7,029 outbreaks.",
    cta=[("primary", "Read the code", f"{GH}/toronto-outbreak-data-quality"),
         ("ghost", "Read the data dictionary", f"{GH}/toronto-outbreak-data-quality/blob/main/data_dictionary.md"),
         ("ghost", "Read the quality report", f"{GH}/toronto-outbreak-data-quality/blob/main/reports/data_quality_report.md")],
    panels=[
        panel("Outbreaks per year", '<div id="yr"></div>', "By the year of the source file. Click a column to filter.", "2026 covers 1 January to 5 October.", wide=True),
        panel("By causative agent", '<div id="agt"></div>', "66 free-text labels grouped into 13 by keyword rules."),
        panel("By setting", '<div id="set"></div>', "Where the outbreak was declared."),
        panel("By month the outbreak began", '<div id="mon"></div>', "All selected years combined."),
        panel("By duration", '<div id="dur"></div>', "Days from start to declared over.", "Active outbreaks have no end date and are shown separately."),
    ],
    prose=[
        prose("Twelve validation rules", "<p>Each rule is a SQL query that counts the records failing it. Failing records are flagged and kept; nothing is deleted.</p>" + table(
            ["Rule", "Check", "Failing records"],
            [[r, c, f'<span class="{"flag" if n else "ok"}">{n:,}</span>'] for r, c, n in RULES], numeric=(2,))),
        prose("Cleaning decisions", table(["Issue in the source", "Decision"], [
            ["The 2020 file names two columns differently", "Column names aligned before combining"],
            ["Unit appended to the institution name (Michael Garron Hospital - H6)", "Split into facility name and unit; original kept"],
            ["One site under many names", "Not merged by guesswork. Grouped by normalized address and labelled with the most common name there"],
            ["Address punctuation and case vary (St. Clair, St.Clair)", "Compared with punctuation, spaces and case removed"],
            ["Agent labels vary (Enterovirus/Rhinovirus, Enterovirus/ Rhinovirus)", "Grouped by keyword; original kept"],
            ["Second agent blank in 5,711 records and \"None\" in 1,018", "Both stored as empty"],
            ["Active outbreaks have no end date", "Duration left empty, not zero"],
        ])),
        prose("What this data cannot show", "<ul><li>Counts are reported outbreaks, not cases. There is no number of people affected and no facility size, so risk cannot be compared between facilities.</li>"
              "<li>Changes over time partly reflect reporting practice: COVID-19 outbreak definitions and testing changed between 2020 and 2026.</li>"
              "<li>Grouping by address is imperfect. A few addresses host units of several hospitals, and a facility that moved appears as two sites.</li>"
              "<li>2026 is a partial year.</li></ul>"),
    ],
    foot='Source: <a href="https://open.toronto.ca/dataset/outbreaks-in-toronto-healthcare-institutions/">Outbreaks in Toronto Healthcare Institutions</a>, Toronto Public Health, City of Toronto Open Data, downloaded 11 October 2026. Contains information licensed under the Open Government Licence – Toronto. Independent analysis, not endorsed by the City of Toronto.',
    script="""
const years = Array.from({ length: 11 }, (_, i) => String(2016 + i));
const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
const settings = D.settings.map(s => s === 'LTCH' ? 'Long-term care home' : s.replace('Hospital-', 'Hospital, ').replace('Care', 'care').replace('Home', 'home').replace('Psychiatric', 'psychiatric').replace('Acute', 'acute').replace('Chronic', 'chronic'));
const buckets = ['0 to 7', '8 to 14', '15 to 21', '22 to 30', '31 to 60', '61 to 90', 'Over 90', 'Active'];
const bucket = d => d == null ? 7 : d <= 7 ? 0 : d <= 14 ? 1 : d <= 21 ? 2 : d <= 30 ? 3 : d <= 60 ? 4 : d <= 90 ? 5 : 6;
const covid = D.agents.indexOf('COVID-19');
const ex = Explorer({
  n: D.n, measure: 'count',
  dims: {
    yr: { label: 'Year', all: 'All years', values: years, of: i => D.yr[i] - 2016 },
    set: { label: 'Setting', all: 'All settings', values: settings, of: i => D.set[i] },
    typ: { label: 'Type', all: 'All types', values: D.types, of: i => D.typ[i] },
    agt: { label: 'Causative agent', all: 'All agents', values: D.agents, of: i => D.agt[i] },
    mon: { label: 'Start month', all: 'All months', values: months, of: i => D.mon[i] - 1 },
    dur: { label: 'Duration', all: 'Any duration', values: buckets, of: i => bucket(D.dur[i]) }
  },
  measures: { count: { label: 'Outbreaks', of: () => 1, fmt: int } }
});
filterBar($('#filters'), ex, { keys: ['yr', 'set', 'typ', 'agt'], count: ex => {
  const extra = ['mon', 'dur'].filter(k => ex.f[k] != null).map(k => `${ex.dims[k].label}: ${ex.dims[k].values[ex.f[k]]}. `).join('');
  return `${int(ex.sum(() => 1))} of 7,029 outbreaks<small>${extra}${ex.active().length ? 'Filtered' : 'No filters applied'}</small>`;
} });
kpis($('#kpis'), ex, [
  ex => [int(ex.sum(() => 1)), 'Outbreaks'],
  ex => { const d = []; ex.each(i => { if (D.dur[i] != null) d.push(D.dur[i]); }); d.sort((a, b) => a - b);
    const m = d.length ? (d.length % 2 ? d[(d.length - 1) / 2] : (d[d.length / 2 - 1] + d[d.length / 2]) / 2) : null;
    return [m == null ? 'n/a' : `${m} days`, 'Median duration', `${int(d.length)} closed outbreaks`]; },
  ex => { let c = 0, l = 0; ex.each(i => { if (D.dur[i] != null) { c++; if (D.dur[i] > 30) l++; } }); return [c ? pct(l / c) : 'n/a', 'Lasted over 30 days', `${int(l)} of ${int(c)} closed`]; },
  ex => { const n = ex.sum(() => 1), c = ex.sum(i => D.agt[i] === covid ? 1 : 0); return [n ? pct(c / n) : 'n/a', 'COVID-19', `${int(c)} outbreaks`]; }
]);
cols($('#yr'), ex, 'yr');
bars($('#agt'), ex, 'agt'); bars($('#set'), ex, 'set');
cols($('#mon'), ex, 'mon');
bars($('#dur'), ex, 'dur', { sort: 'index', keepZero: true });
""",
)

# ---------------------------------------------------------------- TTC
PAGES["ttc"] = dict(
    desc="Interactive view of 25,737 TTC subway incidents in 2025 by cause, line and time of day, counted by incidents or by delay minutes.",
    made="Python, pandas and matplotlib. September 2026.",
    lead="Which recorded incidents accounted for the most delay in 2025, compared by incident count and by delay minutes.",
    cta=[("primary", "Read the code", f"{GH}/ttc-subway-delay-analysis"),
         ("ghost", "Read the findings report", f"{GH}/ttc-subway-delay-analysis/blob/main/reports/findings.md")],
    panels=[
        panel("Top causes", '<div id="cause"></div>', f"{M} for the 12 largest causes under the current filters. Click a bar to filter.", wide=True),
        panel("By line", '<div id="line"></div>', f"{M} by line. Unadjusted totals, not a reliability rate."),
        panel("By month", '<div id="mon"></div>', f"{M} by month of 2025."),
        panel("By day and hour", '<div id="heat"></div><div class="scale" aria-hidden="true">Fewer<i></i>More</div>', f"{M} for each weekday and hour of day. Darker is more.",
              "Raw totals. The first and last hours of service are shorter than a full service hour.", wide=True),
        panel("By hour of day", '<div id="hr"></div>', f"{M} by the hour the incident was logged.", wide=True),
    ],
    prose=[
        prose("Method and data quality", "<p>The analysis joins incident codes to the City's published cause descriptions, parses dates and times, and standardizes line aliases such as YUS and LINE 1.</p>"
              "<p>Zero-minute incidents, missing line labels, multi-line labels and unmatched cause codes all stay visible. 145 records have codes absent from the description table; they are labelled as unmapped and no cause is guessed.</p>"
              "<p>Invalid dates, times or negative delays would be excluded and counted. The 2025 snapshot has zero excluded records. Both input files are verified against SHA-256 checksums before each run.</p>"),
        prose("What this data cannot show", "<ul><li>Delay minutes are summed from individual incident rows. There is no passenger-level delay, train-service volume or other denominator for a reliability rate.</li>"
              "<li>A cause code does not prove why a specific passenger was delayed.</li>"
              "<li>16,642 of 25,737 incidents recorded zero delay minutes. They count as incidents and add nothing to minutes, which is why the two measures rank causes differently.</li>"
              "<li>354 incidents are logged against more than one line and are kept as their own group.</li></ul>"),
    ],
    foot='Source: <a href="https://open.toronto.ca/dataset/996cfe8d-fb35-40ce-b569-698d51fc683b/">TTC Subway Delay Data</a>, City of Toronto Open Data, 2025 rows. Contains information licensed under the Open Government Licence – Toronto. Independent analysis, not endorsed by the City of Toronto or the TTC.',
    script="""
const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
const hours = Array.from({ length: 24 }, (_, h) => `${String(h).padStart(2, '0')}:00`);
const sentence = s => (s.charAt(0) + s.slice(1).toLowerCase()).replace(/\\b(ttc|opto|paa|esa|atc)\\b/gi, m => m.toUpperCase());
const ex = Explorer({
  n: D.n, measure: 'incidents',
  dims: {
    line: { label: 'Line', all: 'All lines', values: D.lines, of: i => D.line[i] },
    cause: { label: 'Cause', all: 'All causes', values: D.causes.map(sentence), of: i => D.cause[i] },
    day: { label: 'Day', all: 'All days', values: D.days, of: i => D.day[i] },
    mon: { label: 'Month', all: 'All months', values: months, of: i => D.mon[i] - 1 },
    hr: { label: 'Hour', all: 'All hours', values: hours, of: i => D.hr[i] }
  },
  measures: {
    incidents: { label: 'Incidents', of: () => 1, fmt: int },
    minutes: { label: 'Delay minutes', of: i => D.min[i], fmt: int }
  }
});
filterBar($('#filters'), ex, { keys: ['line', 'day', 'mon'], count: ex => {
  const extra = ['cause', 'hr'].filter(k => ex.f[k] != null).map(k => `${ex.dims[k].label}: ${ex.dims[k].values[ex.f[k]]}. `).join('');
  return `${int(ex.sum(() => 1))} of 25,737 incidents<small>${extra}${ex.active().length ? 'Filtered' : 'No filters applied'}</small>`;
} });
kpis($('#kpis'), ex, [
  ex => [int(ex.sum(() => 1)), 'Recorded incidents'],
  ex => [int(ex.sum(i => D.min[i])), 'Recorded delay minutes'],
  ex => { const n = ex.sum(() => 1), z = ex.sum(i => D.min[i] === 0 ? 1 : 0); return [n ? pct(z / n) : 'n/a', 'Recorded zero delay', `${int(z)} incidents`]; },
  ex => { const p = ex.sum(i => D.min[i] > 0 ? 1 : 0), m = ex.sum(i => D.min[i]); return [p ? (m / p).toFixed(1) : 'n/a', 'Minutes per delaying incident', `${int(p)} incidents with a delay`]; }
]);
bars($('#cause'), ex, 'cause', { top: 12 });
bars($('#line'), ex, 'line');
cols($('#mon'), ex, 'mon');
heat($('#heat'), ex, 'day', 'hr', { tick: j => j % 3 === 0 ? j : '', row: d => d.slice(0, 3), col: j => hours[j] });
cols($('#hr'), ex, 'hr', { tick: i => i % 3 === 0 ? i : '' });
""",
)

# ---------------------------------------------------------------- AdventureWorks
PAGES["adventureworks"] = dict(
    desc="Interactive view of AdventureWorks sample sales: revenue and estimated gross profit by channel, category, territory and discount.",
    made="SQL, Excel, Power Query and Python. September 2026.",
    lead="Which channel, product groups and territories generated revenue, and where revenue failed to turn into estimated gross profit.",
    cta=[("primary", "Read the code", f"{GH}/adventureworks-sales-analysis"),
         ("ghost", "See the Excel dashboard", f"{GH}/adventureworks-sales-analysis/blob/main/assets/dashboard.png")],
    panels=[
        panel("By month", '<div id="mon"></div>', f"{M} by order month. Click a column to filter.", "The first and last months are partial.", wide=True),
        panel("By product category", '<div id="cat"></div>', f"{M} by category."),
        panel("By territory", '<div id="terr"></div>', f"{M} by sales territory."),
        panel("Gross margin by channel", '<div id="mch"></div>', "Estimated gross profit divided by revenue."),
        panel("Gross margin by discount band", '<div id="mband"></div>', "Estimated gross profit divided by revenue, by unit-price discount.",
              "A descriptive comparison. It does not show that discounts caused the losses."),
    ],
    prose=[
        prose("How the numbers are defined", "<p>Eight source tables are loaded into SQLite. The model keeps shipped orders only and joins each of the 121,317 order lines to the product's standard cost on its order date. On 64 lines no cost interval matches, so the current standard cost is used and flagged.</p>"
              "<ul><li><b>Revenue</b> is line revenue after the unit-price discount, excluding tax and freight.</li>"
              "<li><b>Estimated gross profit</b> is revenue minus quantity times standard cost. It is not net profit.</li>"
              "<li><b>Gross margin</b> is estimated gross profit divided by revenue.</li></ul>"
              "<p style=\"margin-top:14px\">The Excel dashboard imports six SQL exports through Power Query and reconciles its totals to the SQL controls on a QA sheet. Seventeen Python tests cover the pipeline.</p>"),
        prose("What this data cannot show", "<ul><li>AdventureWorks is Microsoft's fictional sample, not a real business. Orders run from 30 May 2022 to 29 June 2025.</li>"
              "<li>Gross profit uses standard cost and excludes operating expenses and returns.</li>"
              "<li>Discount-band comparisons are observational; channel mix and product mix could explain some of the difference.</li>"
              "<li>Order and customer counts are left out of this page because they cannot be added across categories.</li></ul>"),
    ],
    foot='Source: <a href="https://github.com/microsoft/sql-server-samples/tree/master/samples/databases/adventure-works/oltp-install-script">Microsoft AdventureWorks OLTP sample data</a> (MIT licence). Independent analysis, not endorsed by Microsoft.',
    script="""
const mnames = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
const months = D.months.map(m => `${mnames[+m.slice(5) - 1]} ${m.slice(0, 4)}`);
const ex = Explorer({
  n: D.n, measure: 'rev',
  dims: {
    ch: { label: 'Channel', all: 'All channels', values: D.chans, of: i => D.ch[i] },
    cat: { label: 'Category', all: 'All categories', values: D.cats, of: i => D.cat[i] },
    terr: { label: 'Territory', all: 'All territories', values: D.terrs, of: i => D.terr[i] },
    band: { label: 'Discount', all: 'Any discount', values: D.bands, of: i => D.band[i] },
    mon: { label: 'Month', all: 'All months', values: months, of: i => D.mon[i] }
  },
  measures: {
    rev: { label: 'Revenue', of: i => D.rev[i], fmt: money },
    gp: { label: 'Estimated gross profit', of: i => D.gp[i], fmt: money }
  }
});
filterBar($('#filters'), ex, { keys: ['ch', 'cat', 'terr', 'band'], count: ex => {
  const m = ex.f.mon != null ? `${months[ex.f.mon]}. ` : '';
  return `${money(ex.sum(i => D.rev[i]))} of $110M revenue<small>${m}${ex.active().length ? 'Filtered' : 'No filters applied'}</small>`;
} });
kpis($('#kpis'), ex, [
  ex => [money(ex.sum(i => D.rev[i])), 'Revenue'],
  ex => [money(ex.sum(i => D.gp[i])), 'Estimated gross profit'],
  ex => { const r = ex.sum(i => D.rev[i]); return [r ? pct(ex.sum(i => D.gp[i]) / r) : 'n/a', 'Gross margin']; },
  ex => [int(ex.sum(i => D.units[i])), 'Units shipped']
]);
const margin = k => ex => {
  const r = ex.group(k, i => D.rev[i]), g = ex.group(k, i => D.gp[i]);
  return { vals: r.map((v, j) => v ? g[j] / v : 0), fmt: v => pct(v), tip: (j, v) => `${ex.dims[k].values[j]}: ${pct(v)} margin on ${money(r[j])} revenue` };
};
cols($('#mon'), ex, 'mon', { tick: (i, m) => m.startsWith('Jan') ? m.slice(4) : '' });
bars($('#cat'), ex, 'cat'); bars($('#terr'), ex, 'terr');
bars($('#mch'), ex, 'ch', { sort: 'index', value: margin('ch') });
bars($('#mband'), ex, 'band', { sort: 'index', value: margin('band') });
""",
)


def build():
    out = SITE / "projects"
    out.mkdir(exist_ok=True)
    for i, key in enumerate(ORDER):
        p = PAGES[key]
        nav = "".join(f'<a href="{k}.html"{" aria-current=\"page\"" if k == key else ""}>{NAMES[k]}</a>' for k in ORDER)
        prev, nxt = ORDER[i - 1], ORDER[(i + 1) % len(ORDER)]
        pager = (f'<a href="{prev}.html"><small>Previous project</small><b>{FULL[prev]}</b></a>'
                 f'<a href="{nxt}.html"><small>Next project</small><b>{FULL[nxt]}</b></a>')
        html = SHELL
        for token, value in {
            "TITLE": FULL[key], "DESC": p["desc"], "NAV": nav, "MADE": p["made"], "LEAD": p["lead"],
            "CTA": "".join(f'<a class="btn {c}" href="{u}">{t}</a>' for c, t, u in p["cta"]),
            "PANELS": "\n".join(p["panels"]), "PROSE": "\n".join(p["prose"]), "PAGER": pager,
            "FOOT": p["foot"], "DATA": key, "SCRIPT": p["script"].strip(),
        }.items():
            html = html.replace(f"@@{token}@@", value)
        (out / f"{key}.html").write_text(html, encoding="utf-8")
        print(f"projects/{key}.html")


if __name__ == "__main__":
    build()
