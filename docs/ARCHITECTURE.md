# Architecture · a research problem to a checked result

![Architecture](../assets/architecture.svg)

## End-to-end design — PLANNED / IN DEVELOPMENT

1. **Researcher** defines the problem, data rights, expected outputs and scientific constraints.
2. **Scientist AI** proposes a decomposition and scientific workflow. Reasoning is not a substitute for an executable mathematical contract.
3. **MainNode / control plane** manages dependencies, routing, data distribution, validation assignments, receipts and collection.
4. **Math / workflow DAG** binds precise inputs, operations, precision, partitioning and output contracts.
5. **Capability router** matches a legal workload to measured device capabilities and validated local profiles.
6. **MinerNodes** commission hardware, generate and check candidates, execute work and retain results until verified receipt.
7. **Execution resources** may include CPUs, GPUs, APUs, RT hardware, AI accelerators and eventually mobile/edge devices. Support is established per backend and path.
8. **Independent validation** checks the assigned mathematical contract, result completeness and provenance. Shared ownership/network domains do not automatically establish independence.
9. **Result merge** reconstructs the requested output, validates partition boundaries and presents it to the researcher.

No step in this diagram implies that the complete network is deployed. Identity, accounting, payment and ledger mechanisms are planned supporting services, not a replacement for useful compute.

## Local implementation boundary — EXPERIMENTAL

The development MinerNode contains hardware inspection, capability-conditioned candidate generation, source generation/compilation, GPU execution, oracle checks and local profile selection. Bounded Runtime Fusion paths share job data and scheduling mechanisms. The composition objective is correctly completed useful work per second.

The public source preview exports the CPU reference/contract layer. It intentionally excludes state-bound runtime installers, local winner seeds, raw measurements, research data and credentials. Public portable GPU execution is a separate release gate, not silently implied by an architecture diagram.

## Trust boundaries

- A documented numeric format does not establish a working backend.
- A compiler accepting a shader does not establish use of the intended hardware unit.
- A correctness pass does not prove sustained utilization.
- A local winner does not become a global science winner.
- A loopback transport test does not establish multi-owner validation.
- A simulated upload does not authorize deletion of research results.
- A future dashboard must show actual live data refreshed within approximately five seconds, or **OFFLINE / UNAVAILABLE**. No simulated number may impersonate network telemetry.
