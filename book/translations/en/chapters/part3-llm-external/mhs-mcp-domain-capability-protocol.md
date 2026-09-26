# From MHS and MCP to Domain Capability Protocols

In August 2026, Anthropic introduced a research preview of the **Model Hardware Standard (MHS)**: a shared specification for AI agents to operate programmable physical equipment safely, initially in scientific laboratories and advanced manufacturing. It is not yet a mature public standard. The engineering question behind it is older: when a domain has many heterogeneous implementations, how can objects, capabilities, state, constraints, and operations be expressed through a stable model?

JDBC, POSIX, USB device classes, Kubernetes resource abstractions, and OpenAPI solve related problems. Such standards reduce repeated integration work by moving vendor-specific knowledge into an adapter layer and giving applications a shared contract.

## What MHS Standardizes

MHS concerns devices such as microscopes, liquid-handling workstations, robot arms, sensors, and laser systems. A standard driver sits between a vendor SDK or device protocol and an application or agent. It translates vendor-specific interfaces and state into a representation that higher layers can discover and use consistently.

The important abstraction is not merely a common function name. A device also has measurable and controllable properties, current state, physical characteristics, units, safety limits, confirmation requirements, and recovery behavior. MHS drivers use simple primitives such as `read` and `write`, but their value depends on the structured device semantics behind those primitives. Device reference files and tags can capture information that otherwise lives in manuals, local files, or operator experience.

```text
agent or application → MHS representation → standard driver
                     → vendor SDK / protocol → physical device
```

This can reduce the need to repeat manuals, unit conventions, and safety rules in every tool description or prompt. It does not give an agent complete physical-world understanding or remove the need for expert operation and safety controls.

## MCP and MHS Sit at Different Layers

The **Model Context Protocol (MCP)** is an open protocol for connecting an AI client to external systems. It can expose prompts, resources, and tools with names, descriptions, input schemas, output schemas, text, images, links, and structured content. It solves the connection and discovery boundary.

MCP does not by itself define what a microscope's state means, which centrifuge limits are safe, or how a robot arm's workspace and payload should be represented. Those are domain semantics. MHS is a device-domain model and control layer; MCP can be one way an agent accesses it, alongside a CLI, code API, or a higher-level business API.

```text
agent → MCP tool, CLI, or business API → MHS capability model → driver → device
```

MHS is model-agnostic. It does not decide the names of business tools, their approval flow, prompt wording, or task orchestration. A laboratory might expose `capture_cell_image`; a quality system might expose `inspect_surface_defect`. Their business meanings differ even if both use the same underlying hardware capability.

## When MCP Alone Is Enough

A team can directly wrap a microscope or robot in an MCP server. For one device and one stable workflow, that may be the most practical choice. The issue is long-term reuse: every independently designed server must otherwise invent capability names, state formats, units, error classes, safety limits, confirmations, and multi-device coordination.

MCP answers “how can an agent reach this capability?” MHS tries to answer “can similar devices be understood and composed with shared semantics?” Standardization becomes worthwhile when implementations are numerous, objects and operations are sufficiently stable, replacement and composition are frequent, and the benefit of a common model exceeds migration cost.

## From Hardware to Domain Capability Models

MHS is officially a hardware standard, but it illustrates a wider domain-modeling pattern. A domain can expose stable objects, capabilities, states, constraints, and workflows while adapters hide heterogeneous implementations. Payments, smart homes, logistics, manufacturing, and games may each have such a need. The point is not to make every API name identical: the semantics must be shared. Two systems may both offer `set_mode` while one only turns off lights and another also locks doors, enables cameras, and changes alarms.

AI amplifies this requirement because agents may enter dynamic environments without a programmer having encoded every vendor manual in advance. They need discoverable capabilities and readable constraints, while executors still enforce authorization, safety, idempotency, and audit.

## Summary

MCP connects agents to tools, resources, and workflows. MHS standardizes the description and control of physical devices through drivers, state, capability, and safety semantics. MHS may be exposed through MCP, but neither protocol grants authority or replaces domain rules. The durable engineering lesson is to standardize meaningful objects and constraints, not only function names.

## References

- [Previewing the Model Hardware Standard](https://www.anthropic.com/news/model-hardware-standard-research-preview)
- [Introducing the Model Context Protocol](https://www.anthropic.com/news/model-context-protocol)
- [What is the Model Context Protocol?](https://modelcontextprotocol.io/docs/2026-07-28/getting-started/intro)
- [MCP Specification: Tools](https://modelcontextprotocol.io/specification/2025-06-18/server/tools)
