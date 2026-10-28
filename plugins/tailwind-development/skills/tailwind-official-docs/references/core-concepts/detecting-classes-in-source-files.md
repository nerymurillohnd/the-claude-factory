# [Detecting classes in source files](https://tailwindcss.com/docs/detecting-classes-in-source-files)

Understanding and customizing how Tailwind scans your source files.

- [Overview](https://tailwindcss.com/docs/detecting-classes-in-source-files#overview): Tailwind scans files and generates only the classes it finds
  - [How classes are detected](https://tailwindcss.com/docs/detecting-classes-in-source-files#how-classes-are-detected): Plain-text scan for class-like tokens
  - [Dynamic class names](https://tailwindcss.com/docs/detecting-classes-in-source-files#dynamic-class-names): Never build class names by interpolation
  - [Which files are scanned](https://tailwindcss.com/docs/detecting-classes-in-source-files#which-files-are-scanned): Skips `.gitignore`d files, `node_modules`, binaries and CSS
- [Explicitly registering sources](https://tailwindcss.com/docs/detecting-classes-in-source-files#explicitly-registering-sources): Add paths with `@source`
  - [Setting your base path](https://tailwindcss.com/docs/detecting-classes-in-source-files#setting-your-base-path): Set the scan root with `source()`
  - [Ignoring specific paths](https://tailwindcss.com/docs/detecting-classes-in-source-files#ignoring-specific-paths): Exclude paths with `@source not`
  - [Disabling automatic detection](https://tailwindcss.com/docs/detecting-classes-in-source-files#disabling-automatic-detection): Register every source by hand with `source(none)`
- [Safelisting specific utilities](https://tailwindcss.com/docs/detecting-classes-in-source-files#safelisting-specific-utilities): Force classes with `@source inline()`
  - [Safelisting variants](https://tailwindcss.com/docs/detecting-classes-in-source-files#safelisting-variants): Safelist with variants
  - [Safelisting with ranges](https://tailwindcss.com/docs/detecting-classes-in-source-files#safelisting-with-ranges): Brace ranges in `@source inline()`
  - [Explicitly excluding classes](https://tailwindcss.com/docs/detecting-classes-in-source-files#explicitly-excluding-classes): Block classes with `@source not inline()`
