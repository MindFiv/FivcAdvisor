# Models Migration Tests - Quick Reference

## Test Files

### 1. `tests/test_models_module.py` (22 tests)
**Purpose**: Unit tests for models module structure and functionality

**Test Coverage**:
- Module exports and structure
- Provider registry pattern
- OpenAI provider implementation
- Ollama provider implementation
- Factory functions (create_default_model, create_chat_model, create_reasoning_model, create_coding_model)

**Key Tests**:
```python
# Module structure
test_module_exports()              # Verify all functions exported
test_all_exports()                 # Verify __all__ is correct
test_providers_module_exists()     # Verify providers module accessible

# Provider registry
test_default_providers_structure() # Verify dict structure
test_default_providers_values_are_callable()  # Verify callability

# OpenAI provider
test_openai_model_creates_chat_openai()       # Verify ChatOpenAI creation
test_openai_model_default_parameters()        # Verify default params
test_openai_model_api_key_is_lambda()         # Verify api_key wrapping

# Ollama provider
test_ollama_model_creates_chat_ollama()       # Verify ChatOllama creation
test_ollama_model_default_parameters()        # Verify default params
test_ollama_model_with_reasoning()            # Verify reasoning param

# Factory functions
test_create_default_model_with_openai()       # Verify model creation
test_create_default_model_unsupported_provider()  # Verify error handling
test_create_default_model_merges_settings()   # Verify settings merge
test_create_chat_model_calls_create_default_model()
test_create_chat_model_uses_chat_config()
test_create_reasoning_model_calls_create_default_model()
test_create_reasoning_model_uses_reasoning_config()
test_create_coding_model_calls_create_default_model()
test_create_coding_model_uses_coding_config()
```

### 2. `tests/test_models_agents_integration.py` (16 tests)
**Purpose**: Integration tests verifying models work with agents module

**Test Coverage**:
- Agent module imports
- Model usage in agent creation
- Model passing through agent hierarchy
- Backward compatibility

**Key Tests**:
```python
# Agent imports
test_agents_imports_model_factories()         # Verify imports available
test_agents_init_imports_from_models()        # Verify namespace

# Default agent
test_default_agent_creates_default_model()    # Verify model creation
test_default_agent_passes_model_to_langchain_agent()  # Verify passing
test_default_agent_respects_provided_model()  # Verify override

# Companion agent
test_companion_agent_creates_chat_model()     # Verify chat model
test_companion_agent_passes_chat_model()      # Verify passing
test_companion_agent_respects_provided_model()  # Verify override

# Tooling agent
test_tooling_agent_creates_reasoning_model()  # Verify reasoning model
test_tooling_agent_passes_reasoning_model()   # Verify passing

# Consultant agent
test_consultant_agent_creates_reasoning_model()  # Verify reasoning model
test_consultant_agent_passes_reasoning_model()   # Verify passing

# Backward compatibility
test_models_module_is_package()                # Verify package structure
test_direct_imports_work()                     # Verify direct imports
test_providers_accessible()                    # Verify providers access
test_no_old_models_py_file()                   # Verify old file removed
```

## Running Tests

### Run all migration tests
```bash
uv run pytest tests/test_models_module.py tests/test_models_agents_integration.py -v
```

### Run specific test class
```bash
uv run pytest tests/test_models_module.py::TestOpenAIProvider -v
```

### Run specific test
```bash
uv run pytest tests/test_models_module.py::TestOpenAIProvider::test_openai_model_creates_chat_openai -v
```

### Run with coverage
```bash
uv run pytest tests/test_models_module.py tests/test_models_agents_integration.py --cov=fivcadvisor.models
```

### Run full test suite
```bash
uv run pytest tests/ -v
```

## Test Statistics

| Metric | Value |
|--------|-------|
| Total Tests | 38 |
| Unit Tests | 22 |
| Integration Tests | 16 |
| Pass Rate | 100% |
| Execution Time | ~1.7s |

## Test Organization

### By Feature
- **Module Structure**: 3 tests
- **Provider Registry**: 4 tests
- **OpenAI Provider**: 3 tests
- **Ollama Provider**: 3 tests
- **Factory Functions**: 9 tests
- **Agent Integration**: 8 tests
- **Backward Compatibility**: 4 tests

### By Type
- **Unit Tests**: 22 (module internals)
- **Integration Tests**: 16 (module + agents)

## Mocking Strategy

Tests use `@patch` decorators to mock:
- LangChain classes (ChatOpenAI, ChatOllama)
- Settings module functions
- Utils module functions
- Tools module components

This ensures tests are isolated and don't require external dependencies.

## Key Testing Patterns

1. **Provider Testing**: Mock LangChain classes, verify parameters
2. **Factory Testing**: Mock providers, verify delegation and settings merge
3. **Agent Testing**: Mock agent creation, verify model usage
4. **Integration Testing**: Verify module structure and backward compatibility

## Troubleshooting

### Test Fails with "AttributeError: module has no attribute"
- Ensure patch path matches where the class is imported
- Use `@patch('langchain_openai.ChatOpenAI')` not `@patch('fivcadvisor.models.providers.ChatOpenAI')`

### Test Fails with "CHROMA_OPENAI_API_KEY not set"
- Mock the tools module to avoid initialization
- Use `@patch('fivcadvisor.agents.tools')`

### Test Fails with Import Error
- Verify models module is properly installed
- Run `uv run pytest` to use virtual environment

## Next Steps

To add more tests:
1. Create test class in appropriate file
2. Use existing test patterns as reference
3. Mock external dependencies
4. Run tests to verify
5. Update this reference guide

## Related Documentation

- `MODELS_MIGRATION_COMPLETE.md` - Full migration summary
- `MIGRATION_TESTS_SUMMARY.md` - Detailed test documentation
- `README.md` - Project structure
- `docs/DESIGN.md` - Architecture documentation

