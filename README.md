# Agent Skills

A collection of AI agent skills designed for [Agent Zero](https://github.com/frdel/agent-zero) and compatible AI systems such as Claude Code. Each skill is a self-contained module with its own script(s) and documentation.

## Skills

| Skill | Description |
|-------|-------------|
| [browser-use-cloud](./browser-use-cloud/) | AI-powered browser automation via Browser Use Cloud API -- web scraping, data extraction, form filling, and authenticated workflows with stealth anti-detect browsers |
| [deep-research](./deep-research/) | Automated deep web research -- performs multiple searches, reviews sources, and synthesizes comprehensive expert-level reports |
| [search-google-places](./search-google-places/) | Google Places API search for businesses and places by category with ratings, reviews, photos, and AI-powered review synthesis |
| [seats-award-search-by-date](./seats-award-search-by-date/) | Day-by-day award flight availability search across all mileage programs with HTML dashboard, calendar heatmaps, and optional 4K infographic (**requires paid Seats.aero Pro subscription**) |
| [use-opencode](./use-opencode/) | OpenCode CLI integration for surgical file edits, refactoring, and code analysis in single-turn non-interactive mode |

## Structure

Each skill follows a consistent layout:

```
skill-name/
  SKILL.md          # Agent-facing documentation (frontmatter + usage)
  README.md         # Human-facing GitHub documentation
  scripts/          # Executable scripts
  config/           # Configuration files (if applicable)
```

- **`SKILL.md`** -- Contains frontmatter metadata (name, description, tags, trigger patterns) used by Agent Zero's skill system, plus detailed usage instructions for the agent.
- **`README.md`** -- Human-readable documentation for GitHub visitors.
- **`scripts/`** -- The actual executable code for the skill.

## Requirements

Skills have varying dependencies. Common requirements:

- **Python 3.10+**
- **API Keys** -- Each skill documents its required environment variables. Never hardcode API keys; always use environment variables.

| Skill | Required Env Vars |
|-------|-------------------|
| browser-use-cloud | `BROWSER_USE_API_KEY` |
| deep-research | *(none -- uses DuckDuckGo)* |
| search-google-places | `GOOGLE_PLACES_API_KEY`, `VENICE_API_KEY` (optional, for review synthesis) |
| seats-award-search-by-date | `SEATS_AERO_API_KEY`, `VENICE_API_KEY` (optional, for infographic) |
| use-opencode | `VENICE_API_KEY` |

## Disclaimer

**USE AT YOUR OWN RISK.** This software is provided "as is", without warranty of any kind, express or implied, including but not limited to the warranties of merchantability, fitness for a particular purpose, and noninfringement.

By using any skill in this repository, you acknowledge and agree to the following:

1. **No Warranty.** The authors and contributors make no representations or warranties regarding the accuracy, completeness, reliability, suitability, or availability of the software, scripts, documentation, or any related materials. Any reliance you place on such materials is strictly at your own risk.

2. **No Liability.** In no event shall the authors, contributors, or copyright holders be liable for any direct, indirect, incidental, special, exemplary, consequential, or punitive damages (including but not limited to procurement of substitute goods or services, loss of use, data, or profits, business interruption, or any other commercial damages or losses) arising out of or in connection with the use of or inability to use this software, however caused and on any theory of liability, whether in contract, strict liability, or tort (including negligence or otherwise), even if advised of the possibility of such damage.

3. **Third-Party APIs and Services.** These skills interact with third-party APIs and services (including but not limited to Google Places API, Browser Use Cloud, Seats.aero, Venice.ai, DuckDuckGo, and OpenCode). The authors are not responsible for any charges, fees, rate limiting, account suspension, terms of service violations, or other consequences arising from your use of these third-party services. You are solely responsible for complying with the terms of service of any third-party API or service you use through these skills.

4. **API Costs and Billing.** Several skills make calls to paid APIs that may incur costs on your accounts. You are solely responsible for monitoring and managing your API usage and any associated charges. The authors accept no responsibility for unexpected charges or costs incurred through the use of these skills.

5. **Data and Privacy.** These skills may process, transmit, or store data through third-party services. The authors make no guarantees regarding data privacy, security, or confidentiality. You are responsible for ensuring that your use of these skills complies with all applicable data protection laws and regulations.

6. **Security.** While efforts have been made to follow security best practices (e.g., using environment variables for API keys), the authors make no guarantees that the software is free of vulnerabilities. You are responsible for reviewing the code and securing your own environment before use.

7. **AI-Generated Output.** Some skills produce AI-generated content, research reports, or automated actions. The authors make no guarantees regarding the accuracy, completeness, or appropriateness of any AI-generated output. You are solely responsible for reviewing and validating all output before relying on it.

8. **Autonomous Agent Execution.** These skills are designed to be executed by autonomous AI agents that may take actions on your behalf, including but not limited to browsing the web, making API calls, reading/writing files, and executing code. The authors accept no responsibility for any actions taken by AI agents using these skills.

9. **No Professional Advice.** Nothing in this repository constitutes financial, legal, medical, travel, or any other form of professional advice. Award flight search results, business search results, research reports, and other outputs are for informational purposes only.

10. **Indemnification.** You agree to indemnify, defend, and hold harmless the authors and contributors from and against any and all claims, liabilities, damages, losses, costs, and expenses (including reasonable attorneys' fees) arising out of or in connection with your use of this software.

**If you do not agree to these terms, do not use this software.**

## License

See individual skill directories for license information.
