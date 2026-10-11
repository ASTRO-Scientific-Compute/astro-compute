# Canonical CPU references

This directory exports the original canonical catalog, CPU oracles, frozen arithmetic tables and analytic vectors from the v1.17.52 development tree. Mathematical implementations are unchanged. The 81 canonical primitives include 66 SPACE entries. The full 94-entry development inventory is summarized in [registry_inventory.json](../registry_inventory.json); the remaining historical/runtime entries are not extra CPU implementations in this preview.

Metadata can name GPU source, validation tools and adapters from the broader development project. Those references describe upstream execution contracts; they do not imply that those tools are included here. Only the files actually present in this preview are installable source. Contract documents retain their upstream mathematical text and historical validation context; current verification scope is [PUBLICATION.md](../docs/PUBLICATION.md).

Run the repository-level tests without a GPU. `specs/` contains contract metadata and `vectors/` contains small analytic examples, not benchmark or researcher data. Mathematical contract digests bind unchanged definitions; no benchmark hash inventory is included.
