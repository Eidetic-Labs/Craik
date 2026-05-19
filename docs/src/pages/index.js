import Link from '@docusaurus/Link';
import Layout from '@theme/Layout';
import useBaseUrl from '@docusaurus/useBaseUrl';

const SECTIONS = [
  {
    num: '01',
    label: 'Learn',
    title: 'Concepts & product model',
    description:
      'The thesis, the typed runtime objects, status, ADRs, and where Craik is going.',
    entry: { to: '/docs/learn', label: 'Open Learn' },
    chips: ['vision', 'concepts', 'contracts', 'roadmap', 'adrs'],
  },
  {
    num: '02',
    label: 'Build',
    title: 'Install, integrate, implement',
    description:
      'Install Craik, register projects, connect runners and providers, write skills and plugins.',
    entry: { to: '/docs/build', label: 'Open Build' },
    chips: ['quickstart', 'runners', 'providers', 'cli', 'skills'],
  },
  {
    num: '03',
    label: 'Operate',
    title: 'Run, monitor & maintain',
    description:
      'Operator views, local state, gateway and channels, companion apps, multimodal, locale.',
    entry: { to: '/docs/operate', label: 'Open Operate' },
    chips: ['doctor', 'operator surface', 'gateway', 'learning loops'],
  },
  {
    num: '04',
    label: 'Secure',
    title: 'Govern, identify, audit',
    description:
      'Policy envelopes, capability grants, identity, secrets, redaction, sandboxes, and memory governance.',
    entry: { to: '/docs/secure', label: 'Open Secure' },
    chips: ['governance', 'policy', 'identity', 'sandboxes', 'redaction'],
  },
];

const PATHS = [
  {
    audience: 'New to Craik',
    title: 'Install, register a project, run your first governed task',
    steps: [
      { to: '/docs/guides/installation', text: 'Install Craik' },
      { to: '/docs/guides/quickstart', text: 'Quickstart' },
      { to: '/docs/concepts/case-files', text: 'How case files work' },
    ],
  },
  {
    audience: 'Integrating a runner',
    title: 'Connect Codex, Claude, Gemini, or a provider directly',
    steps: [
      { to: '/docs/reference/runner-adapter-contract', text: 'Runner adapter contract' },
      { to: '/docs/reference/model-providers', text: 'Model providers' },
      { to: '/docs/guides/provider-routing', text: 'Provider routing' },
    ],
  },
  {
    audience: 'Hardening governance',
    title: 'Add operator identity, credential profiles, and policy gates',
    steps: [
      { to: '/docs/concepts/governance', text: 'Governance model' },
      { to: '/docs/reference/policy-profiles', text: 'Policy profiles' },
      { to: '/docs/guides/capability-grants', text: 'Capability grants' },
    ],
  },
];

const PRIMITIVES = [
  {
    name: 'Case file',
    type: 'case_file.task_042',
    blurb:
      'The pre-run brief — evidence, ADRs, contradictions, traps, prior handoffs, and policy bounds.',
    to: '/docs/concepts/case-files',
  },
  {
    name: 'Policy envelope',
    type: 'policy.envelope',
    blurb:
      'Write authority, review gates, credential bindings, and approval surfaces as runtime objects.',
    to: '/docs/concepts/governance',
  },
  {
    name: 'Capability receipt',
    type: 'rcpt_4f1c',
    blurb:
      'A structured record of actor, target, reason, and result. Every provider call, every credential use.',
    to: '/docs/concepts/receipts',
  },
  {
    name: 'Handoff',
    type: 'handoff.task_042',
    blurb:
      'Machine-readable state for the next agent — human or model — to resume work with reasons attached.',
    to: '/docs/concepts/handoffs',
  },
  {
    name: 'Work graph',
    type: 'graph.export',
    blurb:
      'Tasks, PRs, issues, facts, decisions, docs, tools, agents, and artifacts as connected state.',
    to: '/docs/concepts/work-graph',
  },
  {
    name: 'Memory & contradictions',
    type: 'stigmem.facts',
    blurb:
      'Scope-aware fact proposals and a contradiction inbox so truth does not silently overwrite truth.',
    to: '/docs/concepts/memory-and-stigmem',
  },
];

function BrandMark({ size = 28 }) {
  return (
    <svg
      viewBox="-40 -40 80 80"
      width={size}
      height={size}
      className="cdocs-brand-mark"
      aria-hidden="true"
    >
      <path
        d="M 29.564 -12.246 A 32 32 0 1 0 29.564 12.246"
        fill="none"
        stroke="currentColor"
        strokeWidth="16"
        strokeLinecap="round"
      />
      <circle cx="0" cy="0" r="18" fill="#B4ACE6" className="cdocs-brand-dot" />
    </svg>
  );
}

function Arrow({ size = 14 }) {
  return (
    <svg viewBox="0 0 24 24" width={size} height={size} aria-hidden="true">
      <path
        d="M5 12h14M13 5l7 7-7 7"
        stroke="currentColor"
        strokeWidth="2"
        fill="none"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
    </svg>
  );
}

export default function Home() {
  const ogImage = useBaseUrl('/img/brand/og-image.png');

  return (
    <Layout
      title="Craik Documentation"
      description="Documentation for Craik — the governed agent operating layer from Eidetic Labs."
      image={ogImage}
    >
      <main className="cdocs-home">
        {/* ─────────── Hero ─────────── */}
        <section className="cdocs-hero" aria-labelledby="cdocs-hero-title">
          <div className="cdocs-hero__grid" aria-hidden="true" />
          <div className="cdocs-hero__copy">
            <p className="cdocs-eyebrow">
              <span className="cdocs-eyebrow__dot" />
              Documentation · v0.1.x · MVP
            </p>
            <h1 id="cdocs-hero-title">
              <span className="cdocs-hero__line">The governed agent</span>
              <span className="cdocs-hero__line cdocs-hero__line--accent">
                operating layer.
              </span>
            </h1>
            <p className="cdocs-hero__lede">
              Craik turns coding agents from isolated chat sessions into governed
              project workers with shared context, explicit authority, durable
              receipts, and handoffs the next agent can trust. These docs cover the
              CLI, contracts, provider paths, policy model, and the roadmap toward
              durable agent operations.
            </p>
            <div className="cdocs-hero__actions">
              <Link className="cdocs-button cdocs-button--primary" to="/docs/guides/quickstart">
                <span>Quickstart</span>
                <Arrow />
              </Link>
              <Link className="cdocs-button cdocs-button--ghost" to="/docs/concepts/project-model">
                <span>Read the model</span>
              </Link>
              <code className="cdocs-snippet">
                <span className="cdocs-snippet__prompt">$</span>
                <span>pip install craik</span>
              </code>
            </div>
            <dl className="cdocs-hero__stats">
              <div>
                <dt>Runners</dt>
                <dd>codex · claude · gemini</dd>
              </div>
              <div>
                <dt>Providers</dt>
                <dd>openai · anthropic · oai-compatible</dd>
              </div>
              <div>
                <dt>Status</dt>
                <dd>
                  <span className="cdocs-pulse" />
                  0.1.x · governed MVP
                </dd>
              </div>
            </dl>
          </div>

          {/* Stage: layered “stack” diagram */}
          <aside className="cdocs-hero__stage" aria-label="The Craik runtime stack">
            <div className="cdocs-stack">
              <div className="cdocs-stack__chrome">
                <span className="cdocs-stack__dot cdocs-stack__dot--r" />
                <span className="cdocs-stack__dot cdocs-stack__dot--y" />
                <span className="cdocs-stack__dot cdocs-stack__dot--g" />
                <span className="cdocs-stack__path">~/craik · runtime</span>
              </div>
              <ol className="cdocs-stack__layers">
                <li className="cdocs-stack__layer cdocs-stack__layer--1">
                  <span>L5</span>
                  <strong>Handoff</strong>
                  <code>state · reasons · next</code>
                </li>
                <li className="cdocs-stack__layer cdocs-stack__layer--2">
                  <span>L4</span>
                  <strong>Receipts</strong>
                  <code>actor · cred · target · result</code>
                </li>
                <li className="cdocs-stack__layer cdocs-stack__layer--3">
                  <span>L3</span>
                  <strong>Runner</strong>
                  <code>codex · claude · gemini</code>
                </li>
                <li className="cdocs-stack__layer cdocs-stack__layer--4">
                  <span>L2</span>
                  <strong>Policy envelope</strong>
                  <code>grants · gates · cred</code>
                </li>
                <li className="cdocs-stack__layer cdocs-stack__layer--5">
                  <span>L1</span>
                  <strong>Case file</strong>
                  <code>evidence · contradictions · traps</code>
                </li>
                <li className="cdocs-stack__layer cdocs-stack__layer--6">
                  <span>L0</span>
                  <strong>Project model</strong>
                  <code>repo · adrs · facts · graph</code>
                </li>
              </ol>
            </div>
          </aside>
        </section>

        {/* ─────────── Section navigator ─────────── */}
        <section className="cdocs-nav" aria-labelledby="cdocs-nav-title">
          <header className="cdocs-section-head">
            <p className="cdocs-eyebrow">
              <span className="cdocs-eyebrow__num">§</span> Navigate
            </p>
            <h2 id="cdocs-nav-title">Four entry points into the runtime.</h2>
          </header>
          <ol className="cdocs-nav-grid" role="list">
            {SECTIONS.map((s) => (
              <li key={s.label}>
                <Link className="cdocs-nav-card" to={s.entry.to}>
                  <div className="cdocs-nav-card__head">
                    <span className="cdocs-nav-card__num">{s.num}</span>
                    <span className="cdocs-nav-card__label">{s.label}</span>
                  </div>
                  <h3>{s.title}</h3>
                  <p>{s.description}</p>
                  <ul className="cdocs-chips" aria-label={`${s.label} topics`}>
                    {s.chips.map((c) => (
                      <li key={c}>{c}</li>
                    ))}
                  </ul>
                  <span className="cdocs-nav-card__cta">
                    {s.entry.label}
                    <Arrow size={12} />
                  </span>
                </Link>
              </li>
            ))}
          </ol>
        </section>

        {/* ─────────── Pick a path ─────────── */}
        <section className="cdocs-paths" aria-labelledby="cdocs-paths-title">
          <header className="cdocs-section-head cdocs-section-head--split">
            <div>
              <p className="cdocs-eyebrow">
                <span className="cdocs-eyebrow__num">§</span> Pick a path
              </p>
              <h2 id="cdocs-paths-title">Where are you trying to go?</h2>
            </div>
            <p className="cdocs-section-head__lede">
              Curated reading paths for the three things people most commonly do with
              the Craik MVP. Each path lands you at a working surface in three docs.
            </p>
          </header>
          <ol className="cdocs-paths-grid" role="list">
            {PATHS.map((p, i) => (
              <li className="cdocs-path" key={p.audience}>
                <p className="cdocs-path__audience">
                  <span>0{i + 1}</span>
                  {p.audience}
                </p>
                <h3>{p.title}</h3>
                <ol className="cdocs-path__steps">
                  {p.steps.map((step, j) => (
                    <li key={step.to}>
                      <Link to={step.to}>
                        <span className="cdocs-path__step-num">
                          {String(j + 1).padStart(2, '0')}
                        </span>
                        <span className="cdocs-path__step-text">{step.text}</span>
                        <Arrow size={12} />
                      </Link>
                    </li>
                  ))}
                </ol>
              </li>
            ))}
          </ol>
        </section>

        {/* ─────────── Primitives reference ─────────── */}
        <section className="cdocs-primitives" aria-labelledby="cdocs-primitives-title">
          <header className="cdocs-section-head">
            <p className="cdocs-eyebrow">
              <span className="cdocs-eyebrow__num">§</span> Primitives
            </p>
            <h2 id="cdocs-primitives-title">
              The runtime is six durable, typed objects.
            </h2>
            <p className="cdocs-section-head__lede">
              Everything in Craik composes from these. Each is queryable, exportable,
              and bound to an operator identity.
            </p>
          </header>
          <ul className="cdocs-primitive-grid" role="list">
            {PRIMITIVES.map((p) => (
              <li key={p.name}>
                <Link className="cdocs-primitive" to={p.to}>
                  <p className="cdocs-primitive__type">{p.type}</p>
                  <h3>{p.name}</h3>
                  <p>{p.blurb}</p>
                  <span className="cdocs-primitive__cta">
                    Read <Arrow size={12} />
                  </span>
                </Link>
              </li>
            ))}
          </ul>
        </section>

        {/* ─────────── Quickstart panel ─────────── */}
        <section className="cdocs-quickstart" aria-labelledby="cdocs-qs-title">
          <header className="cdocs-section-head">
            <p className="cdocs-eyebrow">
              <span className="cdocs-eyebrow__num">§</span> First five commands
            </p>
            <h2 id="cdocs-qs-title">From install to first governed run.</h2>
          </header>
          <div className="cdocs-quickstart__body">
            <article className="cdocs-terminal" aria-label="Craik CLI quickstart">
              <header className="cdocs-terminal__chrome">
                <span className="cdocs-terminal__dot cdocs-terminal__dot--r" />
                <span className="cdocs-terminal__dot cdocs-terminal__dot--y" />
                <span className="cdocs-terminal__dot cdocs-terminal__dot--g" />
                <span className="cdocs-terminal__path">~/repos/product</span>
              </header>
              <div className="cdocs-terminal__body">
                <p>
                  <span className="prompt">$</span> pip install craik
                </p>
                <p className="comment">→ installs craik · CLI on PATH</p>
                <p>
                  <span className="prompt">$</span> craik login
                </p>
                <p className="comment">→ device-code OIDC · operator: alice@acme</p>
                <p>
                  <span className="prompt">$</span> craik project add ./repo --name product
                </p>
                <p className="comment">→ project registered · pid_8b3 · 4 ADRs indexed</p>
                <p>
                  <span className="prompt">$</span> craik case build task_042
                </p>
                <p className="comment">→ case file built · 12 evidence refs · 3 contradictions</p>
                <p>
                  <span className="prompt">$</span> craik run task_042 --runner codex
                  <span className="caret">▌</span>
                </p>
              </div>
            </article>
            <aside className="cdocs-quickstart__side">
              <h3>What you get</h3>
              <ul>
                <li>
                  <span className="cdocs-tag">receipts/</span>
                  Per-call structured records bound to operator + credential identity.
                </li>
                <li>
                  <span className="cdocs-tag">handoff.md</span>
                  Machine-readable state the next agent (or you) can resume from.
                </li>
                <li>
                  <span className="cdocs-tag">graph.dot</span>
                  Exportable work graph of tasks, decisions, facts, and artifacts.
                </li>
                <li>
                  <span className="cdocs-tag">case_file/</span>
                  The pre-run brief, sealed and re-runnable for audit and replay.
                </li>
              </ul>
              <Link className="cdocs-button cdocs-button--ghost" to="/docs/guides/quickstart">
                <span>Full quickstart</span>
                <Arrow />
              </Link>
            </aside>
          </div>
        </section>

        {/* ─────────── Footer band ─────────── */}
        <section className="cdocs-band" aria-labelledby="cdocs-band-title">
          <div>
            <p className="cdocs-eyebrow">
              <span className="cdocs-eyebrow__dot" />
              Eidetic Labs
            </p>
            <h2 id="cdocs-band-title">
              Looking for the marketing page or the source?
            </h2>
            <p className="cdocs-band__lede">
              The marketing page covers vision and positioning. The repository is
              the source of truth for the runtime and these docs.
            </p>
          </div>
          <div className="cdocs-band__actions">
            <Link className="cdocs-button cdocs-button--primary" to="https://craik.eidetic-labs.com">
              <span>craik.eidetic-labs.com</span>
              <Arrow />
            </Link>
            <Link className="cdocs-button cdocs-button--ghost" to="https://github.com/eidetic-labs/craik">
              <span>github · eidetic-labs/craik</span>
            </Link>
            <Link className="cdocs-button cdocs-button--ghost" to="https://pypi.org/project/craik/">
              <span>pypi · craik</span>
            </Link>
          </div>
        </section>
      </main>
    </Layout>
  );
}
