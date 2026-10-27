// The plugin options, which .mcp.json passes to this server as environment variables, and the
// file types the Tailwind CSS language server reads.

/** @typedef {{ title: string, languages: Readonly<Record<string, string>> }} FileTypeGroup */

/**
 * File-type groups, one userConfig boolean each: extension → language id, from the language ids
 * @tailwindcss/language-server 0.16.0 accepts.
 * @type {ReadonlyMap<string, FileTypeGroup>}
 */
export const FILE_TYPE_GROUPS = new Map([
  [
    'check_css',
    {
      title: 'CSS and preprocessors',
      languages: {
        '.css': 'css',
        '.scss': 'scss',
        '.sass': 'sass',
        '.less': 'less',
        '.pcss': 'postcss',
        '.postcss': 'postcss',
        '.styl': 'stylus',
        '.sss': 'sugarss',
      },
    },
  ],
  ['check_html', { title: 'HTML', languages: { '.html': 'html', '.htm': 'html' } }],
  [
    'check_js_ts',
    {
      title: 'JavaScript and TypeScript',
      languages: {
        '.js': 'javascript',
        '.mjs': 'javascript',
        '.cjs': 'javascript',
        '.jsx': 'javascriptreact',
        '.ts': 'typescript',
        '.mts': 'typescript',
        '.cts': 'typescript',
        '.tsx': 'typescriptreact',
      },
    },
  ],
  ['check_vue', { title: 'Vue', languages: { '.vue': 'vue' } }],
  ['check_svelte', { title: 'Svelte', languages: { '.svelte': 'svelte' } }],
  ['check_astro', { title: 'Astro', languages: { '.astro': 'astro' } }],
  [
    'check_markdown',
    { title: 'Markdown and MDX', languages: { '.md': 'markdown', '.mdx': 'mdx' } },
  ],
  [
    'check_templates',
    {
      title: 'Server templates',
      languages: {
        '.php': 'php',
        '.erb': 'erb',
        '.twig': 'twig',
        '.liquid': 'liquid',
        '.hbs': 'handlebars',
        '.handlebars': 'handlebars',
        '.njk': 'nunjucks',
        '.ejs': 'ejs',
        '.haml': 'haml',
        '.slim': 'slim',
        '.heex': 'phoenix-heex',
        '.razor': 'razor',
        '.cshtml': 'aspnetcorerazor',
        '.gohtml': 'gohtml',
        '.mustache': 'mustache',
        '.jade': 'jade',
        '.latte': 'latte',
        '.edge': 'edge',
        '.leaf': 'leaf',
      },
    },
  ],
])

export const DEFAULT_CLASS_FUNCTIONS = Object.freeze(['clsx', 'cn', 'cva', 'tw', 'twMerge'])
export const DEFAULT_CLASS_ATTRIBUTES = Object.freeze([
  'class',
  'className',
  'ngClass',
  'class:list',
])

/**
 * @typedef {object} Options
 * @property {ReadonlySet<string>} enabledGroups keys of FILE_TYPE_GROUPS the automatic check covers
 * @property {readonly string[]} classFunctions
 * @property {readonly string[]} classAttributes
 * @property {string | null} configFile path of the CSS entry point or config file, relative to the project
 */

/**
 * The environment variable that carries a userConfig key.
 * @param {string} key
 */
export function envName(key) {
  return `TAILWIND_${key.toUpperCase()}`
}

/**
 * Reads the options from the environment. A value it cannot read throws: the server then fails to
 * start, and /mcp shows why, instead of checking files the user turned off.
 * @param {Readonly<Record<string, string | undefined>>} env
 * @returns {Options}
 */
export function readOptions(env) {
  const enabledGroups = new Set(
    [...FILE_TYPE_GROUPS.keys()].filter((key) =>
      parseBoolean(envName(key), env[envName(key)], true),
    ),
  )
  const configFile = (env[envName('config_file')] ?? '').trim()
  return {
    enabledGroups,
    classFunctions: parseList(
      envName('class_functions'),
      env[envName('class_functions')],
      DEFAULT_CLASS_FUNCTIONS,
    ),
    classAttributes: parseList(
      envName('class_attributes'),
      env[envName('class_attributes')],
      DEFAULT_CLASS_ATTRIBUTES,
    ),
    configFile: configFile === '' ? null : configFile,
  }
}

/**
 * @param {string} name
 * @param {string | undefined} raw
 * @param {boolean} fallback used when the variable is unset or empty
 */
export function parseBoolean(name, raw, fallback) {
  const value = (raw ?? '').trim().toLowerCase()
  if (value === '') {
    return fallback
  }
  if (value === 'true' || value === '1') {
    return true
  }
  if (value === 'false' || value === '0') {
    return false
  }
  throw new Error(`${name} must be true or false, got ${JSON.stringify(raw)}`)
}

/** What separates the names of a list option written as plain text. */
const LIST_SEPARATOR = /[,\n]/u

/**
 * Reads a list option: a JSON array of strings, or names separated by commas or new lines.
 * @param {string} name
 * @param {string | undefined} raw
 * @param {readonly string[]} fallback used when the variable is unset or empty
 * @returns {readonly string[]}
 */
export function parseList(name, raw, fallback) {
  const value = (raw ?? '').trim()
  if (value === '') {
    return fallback
  }
  if (value.startsWith('[')) {
    /** @type {unknown} */
    let parsed
    try {
      parsed = JSON.parse(value)
    } catch {
      throw new Error(`${name} is not a valid JSON array: ${JSON.stringify(raw)}`)
    }
    if (!Array.isArray(parsed) || !parsed.every((item) => typeof item === 'string')) {
      throw new Error(`${name} must be a list of strings, got ${JSON.stringify(raw)}`)
    }
    return parsed.map((item) => item.trim()).filter((item) => item !== '')
  }
  return value
    .split(LIST_SEPARATOR)
    .map((item) => item.trim())
    .filter((item) => item !== '')
}

/**
 * The group and language id of a file extension, or null when the server reads no such files.
 * @param {string} extension lower-case, with its leading dot
 * @returns {{ group: string, languageId: string } | null}
 */
export function fileType(extension) {
  for (const [group, { languages }] of FILE_TYPE_GROUPS) {
    const languageId = languages[extension]
    if (languageId !== undefined) {
      return { group, languageId }
    }
  }
  return null
}

/**
 * The tailwindCSS settings the server answers workspace/configuration with (spec 3.8).
 * @param {Options} options
 */
export function tailwindSettings(options) {
  return {
    classFunctions: [...options.classFunctions],
    classAttributes: [...options.classAttributes],
    experimental: { configFile: options.configFile, classRegex: [] },
    validate: true,
    codeActions: true,
    hovers: true,
    suggestions: true,
    emmetCompletions: false,
    // The server answers textDocument/documentColor only with this on; class_css reads it.
    colorDecorators: true,
    showPixelEquivalents: true,
    rootFontSize: 16,
    inspectPort: null,
    includeLanguages: {},
    files: {
      exclude: ['**/.git/**', '**/node_modules/**', '**/.hg/**', '**/.svn/**'],
    },
    lint: {
      cssConflict: 'warning',
      invalidApply: 'error',
      invalidScreen: 'error',
      invalidVariant: 'error',
      invalidConfigPath: 'error',
      invalidTailwindDirective: 'error',
      recommendedVariantOrder: 'warning',
      usedBlocklistedClass: 'warning',
      deprecatedAtRule: 'warning',
      suggestCanonicalClasses: 'warning',
    },
  }
}
