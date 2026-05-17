// @ts-check
const { themes: prismThemes } = require('prism-react-renderer');

/** @type {import('@docusaurus/types').Config} */
const config = {
  title: 'Craik',
  tagline: 'Durable agent runtime for governed software work',
  favicon: 'img/favicon.ico',
  url: 'https://eidetic-labs.github.io',
  baseUrl: '/Craik/',
  onBrokenLinks: 'throw',
  i18n: {
    defaultLocale: 'en',
    locales: ['en'],
  },
  markdown: {
    mermaid: true,
    hooks: {
      onBrokenMarkdownLinks: 'warn',
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
  ],
  themes: ['@docusaurus/theme-live-codeblock', '@docusaurus/theme-mermaid'],
  themeConfig: {
    image: 'img/logo.svg',
    navbar: {
      title: 'Craik',
      items: [
        { type: 'docSidebar', sidebarId: 'learnSidebar', label: 'Learn', position: 'left' },
        { type: 'docSidebar', sidebarId: 'buildSidebar', label: 'Build', position: 'left' },
        { type: 'docSidebar', sidebarId: 'operateSidebar', label: 'Operate', position: 'left' },
        { type: 'docSidebar', sidebarId: 'secureSidebar', label: 'Secure', position: 'left' },
        {
          href: 'https://github.com/Eidetic-Labs/Craik',
          label: 'GitHub',
          position: 'right',
        },
      ],
    },
    footer: {
      links: [
        {
          title: 'Docs',
          items: [
            { label: 'Learn', to: '/docs/concepts/project-model' },
            { label: 'Build', to: '/docs/guides/quickstart' },
            { label: 'Operate', to: '/docs/guides/development' },
            { label: 'Secure', to: '/docs/concepts/governance' },
          ],
        },
        {
          title: 'Project',
          items: [
            { label: 'Roadmap', to: '/docs/roadmap' },
            { label: 'MVP Roadmap', to: '/docs/mvp-roadmap' },
            { label: 'Limitations', to: '/docs/limitations' },
          ],
        },
      ],
      copyright: `Copyright © ${new Date().getFullYear()} Eidetic Labs.`,
    },
    prism: {
      theme: prismThemes.github,
      darkTheme: prismThemes.dracula,
    },
  },
};

module.exports = config;
