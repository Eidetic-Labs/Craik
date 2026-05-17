import Link from '@docusaurus/Link';
import Layout from '@theme/Layout';

const sections = [
  {
    title: 'Learn',
    description: 'Understand Craik concepts, roadmap, and the robust MVP target.',
    to: '/docs/concepts/project-model',
  },
  {
    title: 'Build',
    description: 'Use the CLI, contracts, providers, case files, and runner workflows.',
    to: '/docs/guides/quickstart',
  },
  {
    title: 'Operate',
    description: 'Run local workflows, inspect state, and follow release-quality checks.',
    to: '/docs/guides/development',
  },
  {
    title: 'Secure',
    description: 'Apply policy, grants, redaction, receipts, and public-boundary rules.',
    to: '/docs/concepts/governance',
  },
];

export default function Home() {
  return (
    <Layout title="Craik" description="Durable agent runtime for governed software work">
      <main className="craik-home">
        <section className="craik-home__hero">
          <h1>Craik</h1>
          <p>Durable agent runtime for governed software work.</p>
          <Link className="button button--primary" to="/docs/mvp-roadmap">
            Robust MVP Roadmap
          </Link>
        </section>
        <section className="craik-home__grid" aria-label="Documentation sections">
          {sections.map((section) => (
            <Link className="craik-home__card" key={section.title} to={section.to}>
              <h2>{section.title}</h2>
              <p>{section.description}</p>
            </Link>
          ))}
        </section>
      </main>
    </Layout>
  );
}
