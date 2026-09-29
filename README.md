# RidePilot

RidePilot is a smart cab booking aggregator system that connects with multiple ride-hailing providers to find the most preferred, cost-effective, or efficient travel options for users.

---

## 💻 ridepilot-ui

The frontend application provides a modern user interface built using **Next.js**.

*   **Technology Stack:** Next.js (React)
*   **Deployment:** For step-by-step setup and deployment instructions, please refer to the [UI README](ridepilot-ui/README.md).

---

## ⚙️ ridepilot

The backend application serves as the core engine, exposing robust REST APIs for seamless communication.

### Key Features
*   **Multi-Provider Integration:** Connects with major cab service providers such as Uber, Ola, and others to aggregate real-time options.
*   **Flexible LLM Support:** Powered by **Ollama** for local AI processing, with built-in configuration options to easily switch to **OpenAI**.
*   **Environment Configuration:** Features toggleable components manageable via a `.env` file, allowing you to use live integrations or switch to a **mock connection layer** for testing without querying actual Uber/Ola live endpoints.

### Technical Stack
*   **Language:** Python
*   **Database:** PostgreSQL
*   **AI/LLM:** Ollama / OpenAI (Configurable)

### Getting Started
For detailed installation, configuration, and API documentation, please refer to the [Backend README](ridepilot/README.md).
