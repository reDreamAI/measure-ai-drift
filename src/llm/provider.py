"""Config-driven LLM provider supporting OpenAI-compatible and Google APIs.

This module provides a unified interface for all LLM backends used in the
therapy simulation system. Provider-specific details are loaded from YAML config.

Usage:
    # Create provider for a specific role
    therapist_llm = create_provider("therapist")
    patient_llm = create_provider("patient")
    router_llm = create_provider("router")
    
    # Or create from explicit config
    config = LLMConfig(
        provider="groq",
        model="llama-3.3-70b-versatile",
        temperature=0.0,
        max_tokens=1024,
        api_key="...",
        base_url="https://api.groq.com/openai/v1",
        provider_type="openai_compatible"
    )
    llm = LLMProvider(config)
    
    # Generate completion
    content, usage = await llm.generate(messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Hello!"}
    ])
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, AsyncGenerator
import logging
import os

import yaml

logger = logging.getLogger(__name__)

# Default config path relative to this file
DEFAULT_CONFIG_PATH = Path(__file__).parent.parent / "config" / "models.yaml"


@dataclass
class LLMConfig:
    """Configuration for an LLM provider instance.
    
    Attributes:
        provider: Provider identifier (e.g., "groq", "scaleway", "openai", "gemini")
        model: Model identifier (provider-specific)
        temperature: Sampling temperature (0.0 = deterministic)
        max_tokens: Maximum tokens in response
        api_key: API key (resolved from environment)
        base_url: API base URL (for OpenAI-compatible providers)
        provider_type: Type of API ("openai_compatible" or "google")
    """
    provider: str
    model: str
    temperature: float = 0.0
    max_tokens: int = 1024
    api_key: str = ""
    base_url: str = ""
    provider_type: str = "openai_compatible"
    
    def __post_init__(self) -> None:
        """Validate configuration after initialization."""
        if not self.provider:
            raise ValueError("Provider name is required")
        if not self.model:
            raise ValueError("Model name is required")
        if self.temperature < 0.0 or self.temperature > 2.0:
            raise ValueError(f"Temperature must be between 0.0 and 2.0, got {self.temperature}")
        if self.max_tokens < 1:
            raise ValueError(f"max_tokens must be positive, got {self.max_tokens}")


class LLMProvider:
    """Unified provider for all LLM backends.
    
    Supports OpenAI-compatible APIs (OpenAI, Groq, Scaleway, etc.) and
    Google's Generative AI API for Gemini models.
    
    Example:
        >>> config = LLMConfig(
        ...     provider="groq",
        ...     model="llama-3.3-70b-versatile",
        ...     api_key="...",
        ...     base_url="https://api.groq.com/openai/v1"
        ... )
        >>> llm = LLMProvider(config)
        >>> content, usage = await llm.generate([{"role": "user", "content": "Hi"}])
    """
    
    def __init__(self, config: LLMConfig) -> None:
        """Initialize the provider with configuration.
        
        Args:
            config: LLMConfig instance with provider settings
        """
        self.config = config
        self._client: Any = None
        self._client = self._create_client()
    
    def _create_client(self) -> Any:
        """Create the appropriate client based on provider type.
        
        Returns:
            Configured API client (AsyncOpenAI or Google GenAI module)
            
        Raises:
            ValueError: If provider_type is unknown
            ImportError: If required package is not installed
        """
        if self.config.provider_type == "openai_compatible":
            try:
                from openai import AsyncOpenAI
            except ImportError as e:
                raise ImportError(
                    "OpenAI package required for OpenAI-compatible providers. "
                    "Install with: pip install openai"
                ) from e
            
            if not self.config.api_key:
                raise ValueError(
                    f"API key required for provider '{self.config.provider}'. "
                    f"Set the appropriate environment variable."
                )
            
            return AsyncOpenAI(
                api_key=self.config.api_key,
                base_url=self.config.base_url or None
            )
        
        elif self.config.provider_type == "google":
            try:
                import google.generativeai as genai
            except ImportError as e:
                raise ImportError(
                    "Google Generative AI package required for Gemini. "
                    "Install with: pip install google-generativeai"
                ) from e
            
            if not self.config.api_key:
                raise ValueError(
                    "API key required for Gemini. "
                    "Set GEMINI_API_KEY or G_DEVELOPER_KEY environment variable."
                )
            
            genai.configure(api_key=self.config.api_key)
            return genai
        
        else:
            raise ValueError(
                f"Unknown provider type: '{self.config.provider_type}'. "
                f"Supported types: 'openai_compatible', 'google'"
            )
    
    async def generate(
        self,
        messages: list[dict[str, str]],
        **kwargs: Any
    ) -> tuple[str, dict[str, Any]]:
        """Generate a completion from the model.
        
        Args:
            messages: List of message dicts with 'role' and 'content' keys
            **kwargs: Additional parameters passed to the API
            
        Returns:
            Tuple of (generated_content, usage_dict)
            
        Raises:
            Exception: If API call fails
        """
        # Allow override of config values via kwargs
        temperature = kwargs.pop("temperature", self.config.temperature)
        max_tokens = kwargs.pop("max_tokens", self.config.max_tokens)
        
        if self.config.provider_type == "openai_compatible":
            return await self._generate_openai(messages, temperature, max_tokens, **kwargs)
        elif self.config.provider_type == "google":
            return await self._generate_google(messages, temperature, max_tokens, **kwargs)
        else:
            raise ValueError(f"Unknown provider type: {self.config.provider_type}")
    
    async def _generate_openai(
        self,
        messages: list[dict[str, str]],
        temperature: float,
        max_tokens: int,
        **kwargs: Any
    ) -> tuple[str, dict[str, Any]]:
        """Generate completion using OpenAI-compatible API.
        
        Args:
            messages: Chat messages
            temperature: Sampling temperature
            max_tokens: Maximum response tokens
            **kwargs: Additional API parameters
            
        Returns:
            Tuple of (content, usage)
        """
        response = await self._client.chat.completions.create(
            model=self.config.model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            **kwargs
        )
        
        content = response.choices[0].message.content or ""
        usage = {
            "prompt_tokens": response.usage.prompt_tokens if response.usage else 0,
            "completion_tokens": response.usage.completion_tokens if response.usage else 0,
            "total_tokens": response.usage.total_tokens if response.usage else 0,
            "model": response.model,
        }
        
        logger.debug(
            f"OpenAI-compatible response from {self.config.provider}/{self.config.model}: "
            f"{usage['total_tokens']} tokens"
        )
        
        return content, usage
    
    async def _generate_google(
        self,
        messages: list[dict[str, str]],
        temperature: float,
        max_tokens: int,
        **kwargs: Any
    ) -> tuple[str, dict[str, Any]]:
        """Generate completion using Google Generative AI API.
        
        Args:
            messages: Chat messages (converted to Gemini format)
            temperature: Sampling temperature
            max_tokens: Maximum response tokens
            **kwargs: Additional API parameters
            
        Returns:
            Tuple of (content, usage)
        """
        import asyncio
        
        # Convert messages to Gemini format
        gemini_messages = self._convert_to_gemini_format(messages)
        
        # Extract system instruction if present
        system_instruction = None
        if messages and messages[0].get("role") == "system":
            system_instruction = messages[0]["content"]
        
        # Create model with configuration
        generation_config = {
            "temperature": temperature,
            "max_output_tokens": max_tokens,
        }
        
        model = self._client.GenerativeModel(
            model_name=self.config.model,
            generation_config=generation_config,
            system_instruction=system_instruction,
        )
        
        # Gemini API is synchronous, so run in executor
        chat = model.start_chat(history=gemini_messages[:-1] if len(gemini_messages) > 1 else [])
        
        # Get the last user message
        last_message = gemini_messages[-1] if gemini_messages else {"parts": [""]}
        last_content = last_message.get("parts", [""])[0] if isinstance(last_message.get("parts", [""]), list) else ""
        
        # Run sync API in thread pool
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(
            None,
            lambda: chat.send_message(last_content)
        )
        
        content = response.text if hasattr(response, "text") else ""
        
        # Gemini usage metadata
        usage = {
            "prompt_tokens": getattr(response.usage_metadata, "prompt_token_count", 0) if hasattr(response, "usage_metadata") else 0,
            "completion_tokens": getattr(response.usage_metadata, "candidates_token_count", 0) if hasattr(response, "usage_metadata") else 0,
            "total_tokens": getattr(response.usage_metadata, "total_token_count", 0) if hasattr(response, "usage_metadata") else 0,
            "model": self.config.model,
        }
        
        logger.debug(
            f"Gemini response from {self.config.model}: "
            f"{usage['total_tokens']} tokens"
        )
        
        return content, usage
    
    def _convert_to_gemini_format(
        self,
        messages: list[dict[str, str]]
    ) -> list[dict[str, Any]]:
        """Convert OpenAI-format messages to Gemini format.
        
        Args:
            messages: OpenAI-format messages
            
        Returns:
            Gemini-format messages (excluding system messages which are handled separately)
        """
        gemini_messages = []
        
        for msg in messages:
            role = msg.get("role", "user")
            content = msg.get("content", "")
            
            # Skip system messages (handled via system_instruction)
            if role == "system":
                continue
            
            # Map roles: OpenAI uses "assistant", Gemini uses "model"
            gemini_role = "model" if role == "assistant" else "user"
            
            gemini_messages.append({
                "role": gemini_role,
                "parts": [content]
            })
        
        return gemini_messages
    
    async def generate_stream(
        self,
        messages: list[dict[str, str]],
        **kwargs: Any
    ) -> AsyncGenerator[str, None]:
        """Stream completion tokens from the model.
        
        Args:
            messages: List of message dicts with 'role' and 'content' keys
            **kwargs: Additional parameters passed to the API
            
        Yields:
            Generated content chunks as strings
            
        Raises:
            Exception: If API call fails
        """
        temperature = kwargs.pop("temperature", self.config.temperature)
        max_tokens = kwargs.pop("max_tokens", self.config.max_tokens)
        
        if self.config.provider_type == "openai_compatible":
            async for chunk in self._stream_openai(messages, temperature, max_tokens, **kwargs):
                yield chunk
        elif self.config.provider_type == "google":
            async for chunk in self._stream_google(messages, temperature, max_tokens, **kwargs):
                yield chunk
        else:
            raise ValueError(f"Unknown provider type: {self.config.provider_type}")
    
    async def _stream_openai(
        self,
        messages: list[dict[str, str]],
        temperature: float,
        max_tokens: int,
        **kwargs: Any
    ) -> AsyncGenerator[str, None]:
        """Stream completion using OpenAI-compatible API.
        
        Args:
            messages: Chat messages
            temperature: Sampling temperature
            max_tokens: Maximum response tokens
            **kwargs: Additional API parameters
            
        Yields:
            Content chunks
        """
        stream = await self._client.chat.completions.create(
            model=self.config.model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            stream=True,
            **kwargs
        )
        
        async for chunk in stream:
            if chunk.choices and chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content
    
    async def _stream_google(
        self,
        messages: list[dict[str, str]],
        temperature: float,
        max_tokens: int,
        **kwargs: Any
    ) -> AsyncGenerator[str, None]:
        """Stream completion using Google Generative AI API.
        
        Note: Gemini's streaming is synchronous, so this wraps it
        to provide an async interface.
        
        Args:
            messages: Chat messages
            temperature: Sampling temperature
            max_tokens: Maximum response tokens
            **kwargs: Additional API parameters
            
        Yields:
            Content chunks
        """
        import asyncio
        
        gemini_messages = self._convert_to_gemini_format(messages)
        
        system_instruction = None
        if messages and messages[0].get("role") == "system":
            system_instruction = messages[0]["content"]
        
        generation_config = {
            "temperature": temperature,
            "max_output_tokens": max_tokens,
        }
        
        model = self._client.GenerativeModel(
            model_name=self.config.model,
            generation_config=generation_config,
            system_instruction=system_instruction,
        )
        
        chat = model.start_chat(history=gemini_messages[:-1] if len(gemini_messages) > 1 else [])
        last_content = ""
        if gemini_messages:
            last_message = gemini_messages[-1]
            parts = last_message.get("parts", [""])
            last_content = parts[0] if isinstance(parts, list) and parts else ""
        
        # Run sync streaming in thread pool
        loop = asyncio.get_event_loop()
        
        def sync_stream():
            return chat.send_message(last_content, stream=True)
        
        response_stream = await loop.run_in_executor(None, sync_stream)
        
        for chunk in response_stream:
            if hasattr(chunk, "text") and chunk.text:
                yield chunk.text
                # Small yield to allow event loop to process
                await asyncio.sleep(0)
    
    def __repr__(self) -> str:
        """String representation of the provider."""
        return (
            f"LLMProvider(provider={self.config.provider!r}, "
            f"model={self.config.model!r}, "
            f"type={self.config.provider_type!r})"
        )


def load_config(config_path: str | Path | None = None) -> dict[str, Any]:
    """Load and validate the models.yaml configuration.
    
    Args:
        config_path: Path to config file (default: src/config/models.yaml)
        
    Returns:
        Parsed configuration dictionary
        
    Raises:
        FileNotFoundError: If config file doesn't exist
        yaml.YAMLError: If config file is invalid YAML
    """
    path = Path(config_path) if config_path else DEFAULT_CONFIG_PATH
    
    if not path.exists():
        raise FileNotFoundError(
            f"Config file not found: {path}. "
            f"Create it from the template or specify a valid path."
        )
    
    with open(path, "r") as f:
        config = yaml.safe_load(f)
    
    # Validate required sections
    required_sections = ["providers", "model_options", "roles"]
    for section in required_sections:
        if section not in config:
            raise ValueError(f"Config missing required section: '{section}'")
    
    return config


def create_provider(
    role: str,
    config_path: str | Path | None = None
) -> LLMProvider:
    """Factory: create provider for a role (therapist/patient/router/judge).
    
    This function reads the models.yaml configuration and creates an
    LLMProvider configured for the specified role. Roles reference model
    options via the 'use' key, which is resolved from the model_options section.
    
    Args:
        role: Role identifier ("therapist", "patient", "router", "judge", 
              or model name from evaluation_models)
        config_path: Optional path to config file (default: src/config/models.yaml)
        
    Returns:
        Configured LLMProvider instance
        
    Raises:
        ValueError: If role is not found in config
        FileNotFoundError: If config file doesn't exist
        
    Example:
        >>> therapist = create_provider("therapist")
        >>> content, usage = await therapist.generate([...])
    """
    config = load_config(config_path)
    model_options = config.get("model_options", {})
    
    # Check if role exists in roles section
    if role in config.get("roles", {}):
        role_config = config["roles"][role]
        
        # Resolve 'use' key to get model details from model_options
        use_key = role_config.get("use")
        if use_key and role in model_options:
            model_def = model_options[role].get(use_key)
            if not model_def:
                available = list(model_options[role].keys())
                raise ValueError(
                    f"Model option '{use_key}' not found for role '{role}'. "
                    f"Available options: {available}"
                )
            provider_name = model_def["provider"]
            model_name = model_def["model"]
        else:
            # Fallback: direct provider/model in role config (legacy format)
            provider_name = role_config.get("provider", "")
            model_name = role_config.get("model", "")
            
    # Check if role is an evaluation model name
    elif "evaluation_models" in config:
        eval_model = next(
            (m for m in config["evaluation_models"] if m.get("name") == role),
            None
        )
        if eval_model:
            role_config = eval_model
            provider_name = eval_model["provider"]
            model_name = eval_model["model"]
        else:
            raise ValueError(
                f"Role '{role}' not found in config. "
                f"Available roles: {list(config.get('roles', {}).keys())}"
            )
    else:
        raise ValueError(
            f"Role '{role}' not found in config. "
            f"Available roles: {list(config.get('roles', {}).keys())}"
        )
    
    # Get provider details
    if provider_name not in config["providers"]:
        raise ValueError(
            f"Provider '{provider_name}' not found in config. "
            f"Available providers: {list(config['providers'].keys())}"
        )
    
    provider_config = config["providers"][provider_name]
    
    # Resolve API key from environment
    api_key_env = provider_config.get("api_key_env", "")
    api_key = os.environ.get(api_key_env, "")
    
    if not api_key:
        logger.warning(
            f"API key not found for provider '{provider_name}'. "
            f"Set environment variable: {api_key_env}"
        )
    
    # Build LLMConfig (role overrides take precedence)
    llm_config = LLMConfig(
        provider=provider_name,
        model=model_name,
        temperature=role_config.get("temperature", 0.0),
        max_tokens=role_config.get("max_tokens", 1024),
        api_key=api_key,
        base_url=provider_config.get("base_url", ""),
        provider_type=provider_config.get("type", "openai_compatible"),
    )
    
    logger.info(
        f"Created LLMProvider for role '{role}': "
        f"{provider_name}/{llm_config.model}"
    )
    
    return LLMProvider(llm_config)


def list_model_options(
    config_path: str | Path | None = None
) -> dict[str, Any]:
    """Return a structured overview of all available model options.
    
    Useful for debugging, logging, or displaying available configurations.
    
    Args:
        config_path: Optional path to config file
        
    Returns:
        Dictionary with model_options, active roles, and evaluation_models
        
    Example:
        >>> options = list_model_options()
        >>> print(options["model_options"]["therapist"])
        {'groq_oss': {'provider': 'groq', 'model': 'openai/gpt-oss-120', ...}, ...}
    """
    config = load_config(config_path)
    
    # Build active selections
    active = {}
    for role, role_config in config.get("roles", {}).items():
        use_key = role_config.get("use", "direct")
        active[role] = {
            "using": use_key,
            "temperature": role_config.get("temperature", 0.0),
            "max_tokens": role_config.get("max_tokens", 1024),
        }
    
    return {
        "providers": list(config.get("providers", {}).keys()),
        "model_options": config.get("model_options", {}),
        "active_roles": active,
        "evaluation_models": [m.get("name") for m in config.get("evaluation_models", [])],
    }


def create_provider_from_config(
    provider_name: str,
    model: str,
    config_path: str | Path | None = None,
    **overrides: Any
) -> LLMProvider:
    """Create a provider with explicit provider and model specification.
    
    Unlike create_provider() which uses role-based lookup, this function
    allows direct specification of provider and model.
    
    Args:
        provider_name: Provider identifier (e.g., "groq", "openai", "gemini")
        model: Model identifier
        config_path: Optional path to config file
        **overrides: Override config values (temperature, max_tokens)
        
    Returns:
        Configured LLMProvider instance
        
    Example:
        >>> llm = create_provider_from_config(
        ...     "groq",
        ...     "llama-3.3-70b-versatile",
        ...     temperature=0.5
        ... )
    """
    config = load_config(config_path)
    
    if provider_name not in config["providers"]:
        raise ValueError(
            f"Provider '{provider_name}' not found in config. "
            f"Available providers: {list(config['providers'].keys())}"
        )
    
    provider_config = config["providers"][provider_name]
    
    # Resolve API key from environment
    api_key_env = provider_config.get("api_key_env", "")
    api_key = os.environ.get(api_key_env, "")
    
    llm_config = LLMConfig(
        provider=provider_name,
        model=model,
        temperature=overrides.get("temperature", 0.0),
        max_tokens=overrides.get("max_tokens", 1024),
        api_key=api_key,
        base_url=provider_config.get("base_url", ""),
        provider_type=provider_config.get("type", "openai_compatible"),
    )
    
    return LLMProvider(llm_config)
