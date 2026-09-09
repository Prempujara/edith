"""Provider-independent LLM abstraction and adapters.

The rest of the backend depends only on the :class:`~services.llm.base.LLMClient`
protocol. Concrete vendor SDKs are confined to individual adapter modules
(e.g. ``anthropic_client``) and are imported lazily so the application and its
tests run without the SDK installed.
"""
