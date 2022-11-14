### lint-po

A simple gettext .po linter to check for mangled variable names in translations.


#### Features

* reads utf-8 encoded *.po files
* skips `msgid/msgstr` pairs where either value is unset
* compares original/translation pairs for common interpolation markers:
  * supports `{name}`, `{123}`, `<123>`, `</123>`, `<123/>`, `%(name)s`
  * ensures both messages use the same set of variables - no renames, no removals, no additions
* supports Github Actions error reporting syntax (when `env.GITHUB_ACTIONS` is set)
* supports lingui plural syntax - `msgstr "{count, plural, one {依存関係} other {依存関係}}"` is the one case when the thing in {} needs to change between msgid and msgstr


#### Example usage

```sh
$ lint-po locale/*.po

Difference between msgid="Hello {name}" and msgstr="Bonjour {nom}":
  Missing from msgstr: {name}
  Unexpected in msgstr: {nom}
  at problem.po:2
```


#### TODO

* catch nesting errors (<0><1></0></1>), reordering is fine but nesting still needs to make sense
* ensure positional counts (3x %s vs 4x %s, etc.)
* build: autoincrement version for releases
* check headers, Language: <code> should match the filename
