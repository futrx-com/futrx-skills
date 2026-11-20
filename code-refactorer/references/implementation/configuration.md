# Configuration

Read when moving constants, catalogs, defaults, flags, environment values, or runtime settings.

- Give application constants and catalogs one canonical configuration owner, grouped by domain rather than collected in one giant file.
- Use `config/constants/` for constants and catalogs, and `config/runtime/` for environment loading, validation, defaults, and typed settings, or an established equivalent.
- Search for existing definitions before adding another. Reuse the canonical value instead of creating near-duplicates.
- Keep distinct meanings separate even when values match, such as `DEFAULT_PAGE_SIZE` and `MAX_PAGE_SIZE`.
- Keep business decisions, application workflows, mutable application state, and dependency construction outside configuration.
- Construct dependencies where the application is assembled, using the loaded settings.
- Keep backend secrets out of source code and frontend configuration. Client configuration must contain only public values.
- Give a constant used on both client and server one canonical owner, shared through an API contract or shared package.
- Preserve loading order, precedence, defaults, validation behavior, and when settings take effect. Do not introduce startup failures during a structural move.
