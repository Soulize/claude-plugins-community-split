# Split marketplace mirror

This repository keeps the automation on `main` and generates four read-only branches:

- `upstream-mirror` — exact mirror of `anthropics/claude-plugins-community:main`
- `marketplace-1` — marketplace name `soulize-community-split-1`
- `marketplace-2` — marketplace name `soulize-community-split-2`
- `marketplace-3` — marketplace name `soulize-community-split-3`

The workflow runs every six hours, whenever the splitter/workflow itself changes on
`main`, and can also be started manually with
**Actions → Sync upstream and split marketplace → Run workflow**.

## How splitting works

Plugins are assigned to one of three shards using a deterministic SHA-256 hash of
the plugin name. This keeps assignments stable when new plugins are added, unlike
splitting by array position.

Each generated branch starts from the latest upstream `main` commit and changes
only `.claude-plugin/marketplace.json`. The rest of the repository remains
identical to upstream, so marketplace entries that use relative/local source paths
continue to resolve correctly.

The workflow refuses to publish if any shard exceeds 1900 plugins, leaving headroom
below Claude's 2000-plugin marketplace limit.

The generated marketplace names deliberately do not reuse the reserved Anthropic
marketplace name.

## Add all three marketplaces

```bash
claude plugin marketplace add Soulize/claude-plugins-community-split@marketplace-1
claude plugin marketplace add Soulize/claude-plugins-community-split@marketplace-2
claude plugin marketplace add Soulize/claude-plugins-community-split@marketplace-3
```

Then browse them with `/plugin` or install a plugin using its generated marketplace
name, for example:

```bash
claude plugin install PLUGIN_NAME@soulize-community-split-1
```

Generated branches are force-updated by design. Do not make manual changes on
`upstream-mirror` or `marketplace-1/2/3`; put automation changes on `main`.
