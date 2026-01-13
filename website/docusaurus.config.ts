import { themes as prismThemes } from 'prism-react-renderer';
import type { Config } from '@docusaurus/types';
import type * as Preset from '@docusaurus/preset-classic';
import remarkMath from 'remark-math';
import rehypeKatex from 'rehype-katex';

const config: Config = {
  title: 'astr0',
  tagline: 'Per aspera ad astra — Through hardships to the stars',
  favicon: 'img/favicon.ico',

  url: 'https://oddurs.github.io',
  baseUrl: '/astr0/',

  organizationName: 'oddurs',
  projectName: 'astr0',
  deploymentBranch: 'gh-pages',
  trailingSlash: false,

  onBrokenLinks: 'throw',
  onBrokenMarkdownLinks: 'warn',

  // Structured data for search engines
  headTags: [
    {
      tagName: 'script',
      attributes: { type: 'application/ld+json' },
      innerHTML: JSON.stringify({
        '@context': 'https://schema.org/',
        '@type': 'SoftwareApplication',
        name: 'astr0',
        description: 'Professional astronomy calculation toolkit for Python',
        applicationCategory: 'DeveloperApplication',
        operatingSystem: 'Cross-platform',
        url: 'https://oddurs.github.io/astr0/',
        offers: {
          '@type': 'Offer',
          price: '0',
          priceCurrency: 'USD',
        },
      }),
    },
  ],

  // Future flags for v4 compatibility
  future: {
    v4: {
      removeLegacyPostBuildHeadAttribute: true,
    },
    experimental_faster: {
      swcJsLoader: true,
      swcJsMinimizer: true,
      swcHtmlMinimizer: true,
      lightningCssMinimizer: true,
    },
  },

  i18n: {
    defaultLocale: 'en',
    locales: ['en'],
  },

  stylesheets: [
    {
      href: 'https://cdn.jsdelivr.net/npm/katex@0.13.24/dist/katex.min.css',
      type: 'text/css',
      integrity: 'sha384-odtC+0UGzzFL/6PNoE8rX/SPcQDXBJ+uRepguP4QkPCm2LBxH3FA3y+fKSiJ+AmM',
      crossorigin: 'anonymous',
    },
    {
      href: 'https://fonts.googleapis.com/css2?family=DM+Mono:ital,wght@0,300;0,400;0,500;1,300;1,400;1,500&family=Space+Grotesk:wght@300;400;500;600;700&display=swap',
      type: 'text/css',
    },
  ],

  presets: [
    [
      'classic',
      {
        docs: {
          path: '../docs',
          sidebarPath: './sidebars.ts',
          editUrl: 'https://github.com/oddurs/astr0/tree/master/',
          routeBasePath: '/',
          showLastUpdateTime: true,
          showLastUpdateAuthor: true,
          breadcrumbs: true,
          remarkPlugins: [
            remarkMath,
            [require('@docusaurus/remark-plugin-npm2yarn'), { sync: true }],
          ],
          rehypePlugins: [rehypeKatex],
        },
        blog: false,
        theme: {
          customCss: './src/css/custom.css',
        },
        sitemap: {
          lastmod: 'date',
          changefreq: 'weekly',
          priority: 0.5,
        },
      } satisfies Preset.Options,
    ],
  ],

  themeConfig: {
    // SEO metadata
    metadata: [
      { name: 'keywords', content: 'astronomy, python, cli, julian date, coordinates, sun, moon, planets, ephemeris' },
      { name: 'twitter:card', content: 'summary_large_image' },
    ],

    image: 'img/astr0-social-card.png',

    // Announcement bar for v0.3.0 release
    announcementBar: {
      id: 'v0.3.0',
      content: 'astr0 v0.3.0 released with planets module! <a href="/astr0/module-guides/planets">Learn more</a>',
      backgroundColor: '#7c3aed',
      textColor: '#ffffff',
      isCloseable: true,
    },

    navbar: {
      title: 'astr0',
      hideOnScroll: true,
      items: [
        {
          type: 'docSidebar',
          sidebarId: 'docs',
          position: 'left',
          label: 'Documentation',
        },
        {
          href: 'https://github.com/oddurs/astr0',
          label: 'GitHub',
          position: 'right',
        },
        {
          href: 'https://pypi.org/project/astr0/',
          label: 'PyPI',
          position: 'right',
        },
      ],
    },

    footer: {
      style: 'dark',
      links: [
        {
          title: 'Documentation',
          items: [
            { label: 'Getting Started', to: '/getting-started/installation' },
            { label: 'CLI Reference', to: '/cli-reference/overview' },
            { label: 'Python API', to: '/python-api/overview' },
          ],
        },
        {
          title: 'Community',
          items: [
            { label: 'GitHub Issues', href: 'https://github.com/oddurs/astr0/issues' },
            { label: 'Contributing', href: 'https://github.com/oddurs/astr0/blob/master/CONTRIBUTING.md' },
          ],
        },
        {
          title: 'More',
          items: [
            { label: 'GitHub', href: 'https://github.com/oddurs/astr0' },
            { label: 'PyPI', href: 'https://pypi.org/project/astr0/' },
          ],
        },
      ],
      copyright: `Copyright ${new Date().getFullYear()} astr0 contributors. Built with Docusaurus.`,
    },

    // Sidebar behavior
    docs: {
      sidebar: {
        hideable: true,
        autoCollapseCategories: true,
      },
    },

    // Table of contents
    tableOfContents: {
      minHeadingLevel: 2,
      maxHeadingLevel: 4,
    },

    prism: {
      theme: prismThemes.github,
      darkTheme: prismThemes.dracula,
      additionalLanguages: ['bash', 'python', 'json', 'toml', 'diff'],
      magicComments: [
        {
          className: 'theme-code-block-highlighted-line',
          line: 'highlight-next-line',
          block: { start: 'highlight-start', end: 'highlight-end' },
        },
        {
          className: 'code-block-error-line',
          line: 'error-next-line',
        },
      ],
    },

    colorMode: {
      defaultMode: 'light',
      disableSwitch: false,
      respectPrefersColorScheme: true,
    },
  } satisfies Preset.ThemeConfig,

  themes: [
    [
      require.resolve('@easyops-cn/docusaurus-search-local'),
      {
        hashed: true,
        language: ['en'],
        indexBlog: false,
        docsRouteBasePath: '/',
        docsDir: '../docs',
      },
    ],
  ],
};

export default config;
