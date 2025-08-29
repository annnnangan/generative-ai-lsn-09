# Streamlit AI Chat Application

This project is a simple yet powerful Streamlit-based chat application that enables users to interact with AI models through OpenRouter's API with real-time streaming responses. Built with Python as the core language, the application leverages Pydantic AI for robust data validation and model management, ensuring type-safe interactions between the user interface and AI services. The Streamlit framework provides an intuitive web interface where users can input system prompts, contextual information, and questions, which are then processed and sent to OpenRouter's diverse collection of AI models. Streaming responses are displayed in real-time, creating a responsive chat experience. Langfuse integration provides comprehensive observability and analytics, tracking conversation flows, token usage, and performance metrics to help monitor and optimize AI interactions. This architecture combines the simplicity of Streamlit's rapid prototyping capabilities with enterprise-grade AI model access through OpenRouter, while maintaining data integrity through Pydantic's validation system and gaining valuable insights through Langfuse's monitoring platform.

## Implementation Plan Checklist

### Phase 1: Core OpenRouter Integration (Simplified)

- [x] Create `.env` file for OpenRouter API key
- [x] Install essential dependencies: `pydantic-ai-slim[openai]`
- [x] Configure PydanticAI with OpenRouter base URL and API key
- [x] Test basic connection to OpenRouter API

### Phase 2: Replace Mock with Real AI (Minimal Changes)

- [x] Replace mock response function with actual PydanticAI call
- [x] Update Send Button logic to use real AI instead of mock
- [x] Implement basic streaming using PydanticAI's built-in capabilities
- [x] Test real AI responses in the existing UI

### Phase 3: Enhanced Features (Optional)

- [ ] Add conversation export functionality
- [ ] Implement model switching between different OpenRouter models
- [ ] Add basic error handling for API failures
- [ ] Optimize streaming performance

### Phase 4: Langfuse Integration (Deprioritized)

- [ ] Install Langfuse dependencies
- [ ] Configure basic conversation tracking
- [ ] Add performance metrics monitoring
- [ ] Implement analytics dashboard

## Key Implementation Principles

- ✅ Keep existing UI (it's well-designed)
- ✅ Use PydanticAI's built-in OpenRouter support
- ✅ Minimize code changes to existing structure
- ✅ Focus on core functionality first
- ❌ Avoid over-engineering
- ❌ Deprioritize complex features initially

## Dependencies Required

- `streamlit` (already installed)
- `pydantic-ai-slim[openai]` (to be installed)
- `python-dotenv` (for environment management)
