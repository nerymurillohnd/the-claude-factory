# Check browser support

Read https://tailwindcss.com/docs/compatibility#browser-support. Follow it over this file.

- Read the browser floor on the page; never quote it from memory.
- Compare it with the project's targets: Browserslist, analytics or the user's requirement.
- Tell the user which targets fall below the floor before adopting v4.
- Check the installed version's release notes: newer releases degrade better on old browsers.
- Check each bleeding-edge utility on https://caniuse.com before using it.
- Skip a utility or variant the target browsers do not support.
