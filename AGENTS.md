# Active Capabilities & Agent Architecture: Bluestock Week 2

This workspace is configured with specialized multi-agent capabilities, skills, and tools imported from the desktop skills repository (`C:\Users\tanay\OneDrive\Desktop\skills`).

---

## 1. Capability Matrix & Loaded Modules

### 🌐 Web Research
| Capability | Type | File / Path | Key Focus |
| :--- | :--- | :--- | :--- |
| **`browser`** | Skill | `.agents/skills/browser/SKILL.md` | Automated headless/GUI browser interaction via `agent-browser` with 93% token reduction using interactive element refs (`@e1`, `@e2`). |
| **`browser-qa`** | Skill | `.agents/skills/browser-qa/SKILL.md` | Interactive web testing, QA verification, console and network error assertion. |
| **`playwright-cli`** | Skill | `.agents/skills/playwright-cli/SKILL.md` | Direct Playwright script generation and command-line execution for browser workflows. |
| **`xurl`** | Skill | `.agents/skills/xurl/SKILL.md` | Web fetching, external API interaction, search, and remote content retrieval. |
| **`browser-agent`** | Agent | `.agents/agents/browser-agent.yaml` | Dedicated web automation specialist for DOM inspection, navigation, and screenshots. |
| **`e2e-runner`** | Agent | `.agents/agents/e2e-runner.md` | End-to-end browser execution and UI validation. |
| **`docs-lookup`** | Agent | `.agents/agents/docs-lookup.md` | Fast online documentation search and reference lookups. |

---

### 📊 Financial Analysis
| Capability | Type | File / Path | Key Focus |
| :--- | :--- | :--- | :--- |
| **`financial-analysis`**| Skill | `.agents/skills/financial-analysis/SKILL.md` | Institutional equity valuation (DCF, WACC, exit multiples), 3-statement analysis (Balance Sheet, P&L, Cash Flow), ratios (ROE, ROCE, P/E, EV/EBITDA, D/E), IPO deconstruction (DRHP/RHP valuation, GMP, subscription metrics), and portfolio risk metrics (Sharpe, Sortino, Max Drawdown). |
| **`financial-analyst`** | Agent | `.agents/agents/financial-analyst.md` | Senior equity research and financial analyst for corporate valuation and financial modelling. |
| **`trading-predictor`** | Agent | `.agents/agents/trading-predictor.md` | Sublinear algorithm and ML specialist for market price trend forecasting, volatility, and momentum signals (from Claude Flow V3). |
| **`skill-stocktake`** | Skill | `.agents/skills/skill-stocktake/SKILL.md` | Quantitative portfolio health, metrics tracking, and analytics dashboards. |

---

### ✍️ Technical Writing
| Capability | Type | File / Path | Key Focus |
| :--- | :--- | :--- | :--- |
| **`architecture-decision-records`** | Skill | `.agents/skills/architecture-decision-records/SKILL.md` | Michael Nygard ADR format in `docs/adr/` with context, alternatives considered, consequences, and status tracking. |
| **`living-docs-governance`** | Skill | `.agents/skills/living-docs-governance/SKILL.md` | Long-lived documentation governance preventing documentation rot, establishing 4 canonical roles (constitution, map, status, history). |
| **`writing-plans`** | Skill | `.agents/skills/writing-plans/SKILL.md` | Rigorous step-by-step implementation planning, requirement mapping, and verification criteria. |
| **`writing-skills`** | Skill | `.agents/skills/writing-skills/SKILL.md` | Standards and best practices for creating and maintaining agent skills and YAML frontmatter. |
| **`code-tour`** | Skill | `.agents/skills/code-tour/SKILL.md` | Interactive step-by-step CodeTour walkthrough files (`.tour`) with concrete line anchors. |
| **`doc-updater`** | Agent | `.agents/agents/doc-updater.md` | Automated documentation and codemap generation keeping docs synchronized with code. |
| **`spec-miner`** | Agent | `.agents/agents/spec-miner.md` | Behavioral specification extractor generating flat OpenSpec requirement blocks. |
| **`specification`** | Agent | `.agents/agents/specification.md` | SPARC requirements engineering and formal software specifications. |
| **`impeccable-documenter`**| Agent | `.agents/agents/impeccable-documenter.md` | Design system documentation and UX specification. |

---

### 🎨 Diagramming & Visualization
| Capability | Type | File / Path | Key Focus |
| :--- | :--- | :--- | :--- |
| **`diagram-maker`** | Skill | `.agents/skills/diagram-maker/SKILL.md` | Generates standalone clean SVG/HTML architecture diagrams and editable Excalidraw whiteboards. |
| **`visualize`** | Skill | `.agents/skills/visualize/SKILL.md` | Inline visuals, Mermaid diagrams, charts, UI mockups, and dashboard widgets. |
| **`plan-canvas`** | Skill | `.agents/skills/plan-canvas/SKILL.md` | Interactive HTML canvas renderer for reviewing and annotating visual plans. |
| **`impeccable-asset-producer`**| Agent | `.agents/agents/impeccable-asset-producer.md` | Production of clean raster and vector assets, comps, and visual components. |

---

### 📥 Data Extraction
| Capability | Type | File / Path | Key Focus |
| :--- | :--- | :--- | :--- |
| **`nano-pdf`** | Skill | `.agents/skills/nano-pdf/SKILL.md` | High-speed PDF text, tabular data extraction, and programmatic document edits. |
| **`summarize`** | Skill | `.agents/skills/summarize/SKILL.md` | Context-efficient distillation of voluminous documents, reports, and unstructured data. |
| **`spec-miner`** | Agent | `.agents/agents/spec-miner.md` | Reverse-engineers and extracts business logic and requirements from codebases. |
| **`mle-reviewer`** | Agent | `.agents/agents/mle-reviewer.md` | Production review of data contracts, feature pipelines, training sets, and ETL pipelines. |
| **`database-reviewer`** | Agent | `.agents/agents/database-reviewer.md` | Schema analysis, index optimization, query performance, and data modeling. |

---

### 🛠️ Developer Experience & Pragmatic Engineering
| Capability | Type | File / Path | Key Focus |
| :--- | :--- | :--- | :--- |
| **`ponytail`** | Skill | `.agents/skills/ponytail/SKILL.md` | Lazy senior dev mode: the smallest change that fully solves the task, avoiding bloat, over-engineering, and unnecessary code churn. |

---

## 2. Execution Guidelines

1. **Progressive Disclosure**: Detailed skill content is loaded on-demand when the respective task is active.
2. **Coordination Pattern**: Complex cross-functional tasks can spawn specialist subagents (e.g. `financial-analyst` for valuation, `diagram-maker` for architecture SVGs, `nano-pdf` for filing extractions).
3. **Evidence-First Verification**: Every analytical finding or code output must be verified against source facts or reproducible unit tests.
