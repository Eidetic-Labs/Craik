// @ts-check
const { themes: prismThemes } = require('prism-react-renderer');

const isReadTheDocs = process.env.READTHEDOCS === 'True';
const readTheDocsLanguage = process.env.READTHEDOCS_LANGUAGE || 'en';
const readTheDocsVersion = process.env.READTHEDOCS_VERSION || 'latest';

function originOnly(url) {
  return new URL(url).origin;
}

const siteUrl = isReadTheDocs
  ? originOnly(process.env.READTHEDOCS_CANONICAL_URL || 'https://docs.craik.eidetic-labs.com')
  : 'https://eidetic-labs.github.io';
const baseUrl = isReadTheDocs ? `/${readTheDocsLanguage}/${readTheDocsVersion}/` : '/craik/';

/** @type {import('@docusaurus/types').Config} */
const config = {
  title: 'Craik',
  tagline: 'Governed agent-runtime substrate for accountable software work',
  favicon: 'img/brand/favicon.svg',
  url: siteUrl,
  baseUrl,
  trailingSlash: true,
  onBrokenLinks: 'throw',
  i18n: {
    defaultLocale: 'en',
    locales: ['en'],
  },
  markdown: {
    mermaid: true,
    hooks: {
      onBrokenMarkdownLinks: 'throw',
    },
  },
  presets: [
    [
      'classic',
      {
        docs: {
          path: '.',
          routeBasePath: 'docs',
          sidebarPath: './sidebars.js',
          exclude: [
            'README.md',
            'build/**',
            '.docusaurus/**',
            'node_modules/**',
            'package.json',
            'package-lock.json',
            'src/**',
            'static/**',
          ],
          versions: {
            current: {
              label: 'MVP',
              badge: true,
              banner: 'none',
            },
          },
        },
        blog: false,
        theme: {
          customCss: './src/css/custom.css',
        },
      },
    ],
  ],
  plugins: [
    [
      '@easyops-cn/docusaurus-search-local',
      {
        hashed: true,
        indexDocs: true,
        indexPages: true,
      },
    ],
    [
      '@docusaurus/plugin-client-redirects',
      {
        redirects: [
          {
            from: '/docs/getting-started',
            to: '/docs/guides/quickstart',
          },
          {
            from: '/docs/security',
            to: '/docs/concepts/governance',
          },
          {
            from: '/docs/cli',
            to: '/docs/reference/cli',
          },
        ],
      },
    ],
  ],
  themes: ['@docusaurus/theme-live-codeblock', '@docusaurus/theme-mermaid'],
  clientModules: [require.resolve('./src/clientModules/github-stats.js')],
  themeConfig: {
    image: 'img/brand/og-image.png',
    colorMode: {
      defaultMode: 'light',
      respectPrefersColorScheme: true,
    },
    navbar: {
      title: 'Craik',
      logo: {
        alt: 'Craik · product site',
        src: 'img/brand/favicon.svg',
        srcDark: 'img/brand/craik_icon_inverse.svg',
        href: 'https://craik.eidetic-labs.com',
        target: '_self',
      },
      items: [
        { type: 'docSidebar', sidebarId: 'learnSidebar', label: 'Learn', position: 'left' },
        { type: 'docSidebar', sidebarId: 'buildSidebar', label: 'Build', position: 'left' },
        { type: 'docSidebar', sidebarId: 'operateSidebar', label: 'Operate', position: 'left' },
        { type: 'docSidebar', sidebarId: 'secureSidebar', label: 'Secure', position: 'left' },
        {
          type: 'html',
          position: 'right',
          value: [
            '<a class="cdocs-gh-link" href="https://github.com/eidetic-labs/craik" aria-label="Craik on GitHub" target="_blank" rel="noopener">',
            '<svg class="cdocs-gh-icon" viewBox="0 0 24 24" width="18" height="18" aria-hidden="true">',
            '<path fill="currentColor" d="M12 .5C5.65.5.5 5.65.5 12c0 5.08 3.29 9.39 7.86 10.91.58.11.79-.25.79-.56v-2c-3.2.7-3.87-1.36-3.87-1.36-.52-1.32-1.27-1.67-1.27-1.67-1.04-.71.08-.7.08-.7 1.15.08 1.76 1.18 1.76 1.18 1.02 1.75 2.68 1.24 3.34.95.1-.74.4-1.24.73-1.53-2.55-.29-5.24-1.28-5.24-5.71 0-1.26.45-2.29 1.18-3.1-.12-.29-.51-1.46.11-3.04 0 0 .96-.31 3.15 1.18a10.95 10.95 0 0 1 5.74 0c2.19-1.49 3.15-1.18 3.15-1.18.62 1.58.23 2.75.11 3.04.74.81 1.18 1.84 1.18 3.1 0 4.44-2.7 5.42-5.27 5.7.41.36.78 1.07.78 2.16v3.2c0 .31.21.68.8.56 4.57-1.52 7.86-5.83 7.86-10.91C23.5 5.65 18.35.5 12 .5z"/>',
            '</svg>',
            '<span class="cdocs-gh-counts">',
            '<span class="cdocs-gh-stat cdocs-gh-stat--star" data-gh-stars>—</span>',
            '<span class="cdocs-gh-stat cdocs-gh-stat--fork" data-gh-forks>—</span>',
            '</span>',
            '</a>',
          ].join(''),
        },
      ],
    },
    footer: {
      logo: {
        alt: 'Craik · by Eidetic Labs',
        src: 'img/brand/craik_primary.svg',
        srcDark: 'img/brand/craik_primary_inverse.svg',
        href: '/',
        width: 140,
      },
      links: [
        {
          title: 'Learn',
          items: [
            { label: 'Overview', to: '/docs/learn' },
            { label: 'Vision', to: '/docs/vision' },
            { label: 'Concepts', to: '/docs/concepts/project-model' },
            { label: 'Roadmap', to: '/docs/roadmap' },
          ],
        },
        {
          title: 'Build',
          items: [
            { label: 'Overview', to: '/docs/build' },
            { label: 'Quickstart', to: '/docs/guides/quickstart' },
            { label: 'CLI reference', to: '/docs/reference/cli' },
            { label: 'Provider routing', to: '/docs/guides/provider-routing' },
          ],
        },
        {
          title: 'Operate',
          items: [
            { label: 'Overview', to: '/docs/operate' },
            { label: 'Doctor', to: '/docs/guides/doctor' },
            { label: 'Operator surface', to: '/docs/reference/operator-surface' },
            { label: 'Gateway daemon', to: '/docs/reference/gateway-daemon' },
          ],
        },
        {
          title: 'Secure',
          items: [
            { label: 'Overview', to: '/docs/secure' },
            { label: 'Governance', to: '/docs/concepts/governance' },
            { label: 'Policy profiles', to: '/docs/reference/policy-profiles' },
            { label: 'Sandboxes', to: '/docs/reference/sandbox-backends' },
          ],
        },
        {
          title: 'Project',
          items: [
            { label: 'GitHub', href: 'https://github.com/eidetic-labs/craik' },
            { label: 'PyPI · craik', href: 'https://pypi.org/project/craik/' },
            { label: 'Product site', href: 'https://craik.eidetic-labs.com' },
            { label: 'Eidetic Labs', href: 'https://eidetic-labs.com' },
          ],
        },
      ],
      copyright: `© ${new Date().getFullYear()} Eidetic Labs · MIT-licensed runtime · Craik docs`,
    },
    prism: {
      theme: prismThemes.oneLight,
      darkTheme: prismThemes.oneDark,
      additionalLanguages: ['bash', 'json', 'yaml', 'python', 'toml', 'diff', 'ini'],
    },
    tableOfContents: {
      minHeadingLevel: 2,
      maxHeadingLevel: 4,
    },
  },
};

module.exports = config;
