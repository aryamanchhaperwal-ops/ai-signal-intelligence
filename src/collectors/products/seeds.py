"""Foundational AI Startup Products Registry.

Curated verified registry of flagship AI products from leading frontier AI startups.
Every record provides traceable official product URLs, verified company attribution,
and authentic pricing models.
"""

from typing import Any, Dict, List
from src.validation.schemas import PricingModel

FOUNDATIONAL_AI_PRODUCTS: List[Dict[str, Any]] = [
    # OpenAI
    {
        "product_name": "ChatGPT",
        "startup_name": "OpenAI",
        "pricing_model": PricingModel.FREEMIUM,
        "description": "Conversational generative AI assistant powered by GPT-4o and reasoning models.",
        "product_url": "https://chatgpt.com",
    },
    {
        "product_name": "GPT-4o API",
        "startup_name": "OpenAI",
        "pricing_model": PricingModel.PAID,
        "description": "Multimodal flagship API supporting text, vision, and real-time audio inference.",
        "product_url": "https://platform.openai.com/docs/models/gpt-4o",
    },
    {
        "product_name": "DALL-E 3",
        "startup_name": "OpenAI",
        "pricing_model": PricingModel.PAID,
        "description": "High-fidelity text-to-image synthesis model integrated with ChatGPT and REST API.",
        "product_url": "https://openai.com/index/dall-e-3",
    },
    {
        "product_name": "Sora",
        "startup_name": "OpenAI",
        "pricing_model": PricingModel.ENTERPRISE,
        "description": "Diffusion-transformer video generation model generating complex scenes up to 60 seconds.",
        "product_url": "https://openai.com/sora",
    },
    {
        "product_name": "Whisper",
        "startup_name": "OpenAI",
        "pricing_model": PricingModel.FREE,
        "description": "Open-source automatic speech recognition and translation neural network.",
        "product_url": "https://github.com/openai/whisper",
    },
    # Anthropic
    {
        "product_name": "Claude 3.5 Sonnet",
        "startup_name": "Anthropic",
        "pricing_model": PricingModel.FREEMIUM,
        "description": "State-of-the-art reasoning, coding, and vision foundation model.",
        "product_url": "https://www.anthropic.com/claude/sonnet",
    },
    {
        "product_name": "Claude Code",
        "startup_name": "Anthropic",
        "pricing_model": PricingModel.PAID,
        "description": "Agentic command-line interface for deep codebase exploration, editing, and execution.",
        "product_url": "https://docs.anthropic.com/claude/docs/claude-code",
    },
    {
        "product_name": "Claude Artifacts",
        "startup_name": "Anthropic",
        "pricing_model": PricingModel.FREEMIUM,
        "description": "Interactive dynamic workspace for executing web apps, diagrams, and frontend code in Claude.",
        "product_url": "https://claude.ai",
    },
    # Mistral AI
    {
        "product_name": "Le Chat",
        "startup_name": "Mistral AI",
        "pricing_model": PricingModel.FREE,
        "description": "Conversational assistant platform powered by Mistral frontier models with web search.",
        "product_url": "https://chat.mistral.ai",
    },
    {
        "product_name": "Mistral Large 2",
        "startup_name": "Mistral AI",
        "pricing_model": PricingModel.PAID,
        "description": "Enterprise-grade 123B parameter language model specialized in code, multilingual, and reasoning.",
        "product_url": "https://mistral.ai/technology/#models",
    },
    {
        "product_name": "Codestral",
        "startup_name": "Mistral AI",
        "pricing_model": PricingModel.FREEMIUM,
        "description": "Open-weight generative code model explicitly designed for code completion and synthesis.",
        "product_url": "https://mistral.ai/news/codestral",
    },
    # Perplexity AI
    {
        "product_name": "Perplexity Pro",
        "startup_name": "Perplexity AI",
        "pricing_model": PricingModel.FREEMIUM,
        "description": "Conversational search engine providing real-time sourced citations and multi-model switching.",
        "product_url": "https://www.perplexity.ai/pro",
    },
    {
        "product_name": "Sonar API",
        "startup_name": "Perplexity AI",
        "pricing_model": PricingModel.PAID,
        "description": "Search-augmented LLM API with live web grounding and citation extraction.",
        "product_url": "https://docs.perplexity.ai",
    },
    # Cursor (Anysphere)
    {
        "product_name": "Cursor Editor",
        "startup_name": "Cursor",
        "pricing_model": PricingModel.FREEMIUM,
        "description": "AI-native code editor fork of VS Code featuring Composer and predictive multi-line editing.",
        "product_url": "https://www.cursor.com",
    },
    # Cognition
    {
        "product_name": "Devin",
        "startup_name": "Cognition",
        "pricing_model": PricingModel.ENTERPRISE,
        "description": "Autonomous AI software engineer capable of planning, executing, debugging, and building repos.",
        "product_url": "https://devin.ai",
    },
    # Black Forest Labs
    {
        "product_name": "FLUX.1 [dev]",
        "startup_name": "Black Forest Labs",
        "pricing_model": PricingModel.FREE,
        "description": "12-billion parameter rectified flow transformer for high-quality image generation.",
        "product_url": "https://blackforestlabs.ai",
    },
    {
        "product_name": "FLUX.1 [pro]",
        "startup_name": "Black Forest Labs",
        "pricing_model": PricingModel.PAID,
        "description": "Commercial state-of-the-art text-to-image API delivering top prompt adherence and resolution.",
        "product_url": "https://blackforestlabs.ai/#get-flux",
    },
    # Midjourney
    {
        "product_name": "Midjourney v6.1",
        "startup_name": "Midjourney",
        "pricing_model": PricingModel.PAID,
        "description": "Photorealistic generative image synthesis engine accessible via Discord and web platform.",
        "product_url": "https://www.midjourney.com",
    },
    # ElevenLabs
    {
        "product_name": "ElevenLabs Voice Studio",
        "startup_name": "ElevenLabs",
        "pricing_model": PricingModel.FREEMIUM,
        "description": "AI voice synthesis, realistic voice cloning, dubbing studio, and speech-to-speech engine.",
        "product_url": "https://elevenlabs.io",
    },
    {
        "product_name": "ElevenLabs Conversational AI",
        "startup_name": "ElevenLabs",
        "pricing_model": PricingModel.PAID,
        "description": "Low-latency voice agent platform for real-time customer support and interactive assistants.",
        "product_url": "https://elevenlabs.io/conversational-ai",
    },
    # Runway
    {
        "product_name": "Gen-3 Alpha",
        "startup_name": "Runway",
        "pricing_model": PricingModel.FREEMIUM,
        "description": "Frontier video generation model capable of expressive camera movements and photorealistic motion.",
        "product_url": "https://runwayml.com/research/gen-3-alpha",
    },
    # Stability AI
    {
        "product_name": "Stable Diffusion 3.5",
        "startup_name": "Stability AI",
        "pricing_model": PricingModel.FREEMIUM,
        "description": "Multimodal diffusion model family with Large, Large Turbo, and Medium image generators.",
        "product_url": "https://stability.ai/stable-diffusion-3-5",
    },
    # Cohere
    {
        "product_name": "Command R+",
        "startup_name": "Cohere",
        "pricing_model": PricingModel.FREEMIUM,
        "description": "Highly scalable enterprise language model optimized for conversational interaction and RAG.",
        "product_url": "https://cohere.com/models/command-r-plus",
    },
    {
        "product_name": "Cohere Rerank 3",
        "startup_name": "Cohere",
        "pricing_model": PricingModel.PAID,
        "description": "Zero-shot document reranker boosting retrieval precision for enterprise search systems.",
        "product_url": "https://cohere.com/rerank",
    },
    # Scale AI
    {
        "product_name": "Scale Data Engine",
        "startup_name": "Scale AI",
        "pricing_model": PricingModel.ENTERPRISE,
        "description": "RLHF, red teaming, annotation, and synthetic data infrastructure for foundation model builders.",
        "product_url": "https://scale.com/data-engine",
    },
    {
        "product_name": "Scale GenAI Platform",
        "startup_name": "Scale AI",
        "pricing_model": PricingModel.ENTERPRISE,
        "description": "Full-stack enterprise application framework for fine-tuning, RAG, and evaluating generative AI.",
        "product_url": "https://scale.com/genai-platform",
    },
    # LangChain
    {
        "product_name": "LangChain Framework",
        "startup_name": "LangChain",
        "pricing_model": PricingModel.FREE,
        "description": "Open-source standard library for composing LLM pipelines, chains, and memory tools.",
        "product_url": "https://www.langchain.com",
    },
    {
        "product_name": "LangSmith",
        "startup_name": "LangChain",
        "pricing_model": PricingModel.FREEMIUM,
        "description": "DevOps observability, evaluation, and prompt debugging platform for production LLM apps.",
        "product_url": "https://smith.langchain.com",
    },
    {
        "product_name": "LangGraph",
        "startup_name": "LangChain",
        "pricing_model": PricingModel.FREEMIUM,
        "description": "Multi-agent cyclical coordination framework for stateful, durable agent architectures.",
        "product_url": "https://www.langchain.com/langgraph",
    },
    # LlamaIndex
    {
        "product_name": "LlamaIndex Core",
        "startup_name": "LlamaIndex",
        "pricing_model": PricingModel.FREE,
        "description": "Data framework for connecting custom private data sources to large language models.",
        "product_url": "https://www.llamaindex.ai",
    },
    {
        "product_name": "LlamaCloud & LlamaParse",
        "startup_name": "LlamaIndex",
        "pricing_model": PricingModel.FREEMIUM,
        "description": "Managed parsing, chunking, and ingestion engine for complex PDFs, tables, and docs.",
        "product_url": "https://cloud.llamaindex.ai",
    },
    # Pinecone
    {
        "product_name": "Pinecone Serverless",
        "startup_name": "Pinecone",
        "pricing_model": PricingModel.FREEMIUM,
        "description": "High-throughput serverless vector database with decoupled compute and storage for RAG.",
        "product_url": "https://www.pinecone.io",
    },
    # Weaviate
    {
        "product_name": "Weaviate Cloud",
        "startup_name": "Weaviate",
        "pricing_model": PricingModel.FREEMIUM,
        "description": "Open-source AI-native vector search engine with integrated hybrid search and vectorizers.",
        "product_url": "https://weaviate.io",
    },
    # Qdrant
    {
        "product_name": "Qdrant Cloud",
        "startup_name": "Qdrant",
        "pricing_model": PricingModel.FREEMIUM,
        "description": "Rust-powered vector similarity search engine and managed cloud database for embeddings.",
        "product_url": "https://qdrant.tech",
    },
    # Chroma
    {
        "product_name": "Chroma DB",
        "startup_name": "Chroma",
        "pricing_model": PricingModel.FREE,
        "description": "Open-source embedding database focused on developer ergonomics and lightweight local setup.",
        "product_url": "https://www.trychroma.com",
    },
    # Weights & Biases
    {
        "product_name": "W&B Models",
        "startup_name": "Weights & Biases",
        "pricing_model": PricingModel.FREEMIUM,
        "description": "Experiment tracking, model registry, and hyperparameter tuning platform for ML teams.",
        "product_url": "https://wandb.ai/site",
    },
    {
        "product_name": "W&B Weave",
        "startup_name": "Weights & Biases",
        "pricing_model": PricingModel.FREEMIUM,
        "description": "Lightweight toolkit for tracking, evaluating, and iterating on LLM applications.",
        "product_url": "https://wandb.ai/site/weave",
    },
    # Together AI
    {
        "product_name": "Together Inference Engine",
        "startup_name": "Together AI",
        "pricing_model": PricingModel.PAID,
        "description": "Ultra-fast open-source LLM inference cloud platform powering low-latency generative models.",
        "product_url": "https://www.together.ai",
    },
    # Groq
    {
        "product_name": "GroqCloud LPU",
        "startup_name": "Groq",
        "pricing_model": PricingModel.FREEMIUM,
        "description": "Language Processing Unit (LPU) cloud inference delivering 500+ tokens per second on open models.",
        "product_url": "https://groq.com",
    },
    # Cerebras
    {
        "product_name": "Cerebras Inference",
        "startup_name": "Cerebras Systems",
        "pricing_model": PricingModel.FREEMIUM,
        "description": "Wafer-scale AI accelerator inference cloud offering blazing fast LLM token throughput.",
        "product_url": "https://cerebras.ai/inference",
    },
    # DeepSeek
    {
        "product_name": "DeepSeek Chat",
        "startup_name": "DeepSeek",
        "pricing_model": PricingModel.FREE,
        "description": "Frontier open-weight conversational assistant powered by DeepSeek-V3 and DeepSeek-R1.",
        "product_url": "https://chat.deepseek.com",
    },
    {
        "product_name": "DeepSeek API",
        "startup_name": "DeepSeek",
        "pricing_model": PricingModel.PAID,
        "description": "Cost-disruptive inference API with OpenAI-compatible endpoint schema.",
        "product_url": "https://platform.deepseek.com",
    },
    # Replit
    {
        "product_name": "Replit Agent",
        "startup_name": "Replit",
        "pricing_model": PricingModel.FREEMIUM,
        "description": "Autonomous full-stack application builder that provisions, codes, and deploys cloud apps.",
        "product_url": "https://replit.com/agent",
    },
    # Phind
    {
        "product_name": "Phind Pro",
        "startup_name": "Phind",
        "pricing_model": PricingModel.FREEMIUM,
        "description": "Intelligent search engine and pair programmer optimized specifically for developers.",
        "product_url": "https://www.phind.com",
    },
    # Jasper AI
    {
        "product_name": "Jasper Marketing Platform",
        "startup_name": "Jasper",
        "pricing_model": PricingModel.PAID,
        "description": "AI copilot for enterprise marketing teams with brand voice customization and multi-channel campaigns.",
        "product_url": "https://www.jasper.ai",
    },
    # Copy.ai
    {
        "product_name": "Copy.ai GTM AI Platform",
        "startup_name": "Copy.ai",
        "pricing_model": PricingModel.FREEMIUM,
        "description": "Go-to-market automation platform connecting AI workflows to CRM, email, and pipeline operations.",
        "product_url": "https://www.copy.ai",
    },
    # Descript
    {
        "product_name": "Descript Underlord",
        "startup_name": "Descript",
        "pricing_model": PricingModel.FREEMIUM,
        "description": "All-in-one AI video and podcast editing platform with text-based editing and voice cloning.",
        "product_url": "https://www.descript.com",
    },
    # Modal
    {
        "product_name": "Modal Cloud",
        "startup_name": "Modal",
        "pricing_model": PricingModel.FREEMIUM,
        "description": "Serverless cloud compute for running AI models, batch jobs, and GPU workloads with fast cold starts.",
        "product_url": "https://modal.com",
    },
    # Baseten
    {
        "product_name": "Baseten Model Deployment",
        "startup_name": "Baseten",
        "pricing_model": PricingModel.FREEMIUM,
        "description": "Model serving infrastructure delivering autoscaling, custom runtimes, and low-latency inference.",
        "product_url": "https://www.baseten.co",
    },
    # Glean
    {
        "product_name": "Glean Work AI",
        "startup_name": "Glean",
        "pricing_model": PricingModel.ENTERPRISE,
        "description": "Enterprise generative AI search and assistant indexing all company knowledge and SaaS apps.",
        "product_url": "https://www.glean.com",
    },
    # Harvey AI
    {
        "product_name": "Harvey Legal AI",
        "startup_name": "Harvey",
        "pricing_model": PricingModel.ENTERPRISE,
        "description": "Generative AI platform designed for legal professionals, contract analysis, and regulatory diligence.",
        "product_url": "https://www.harvey.ai",
    },
    # Hebbia
    {
        "product_name": "Hebbia Matrix",
        "startup_name": "Hebbia",
        "pricing_model": PricingModel.ENTERPRISE,
        "description": "AI analysis tool structuring unstructured financial documents, filings, and diligence data.",
        "product_url": "https://www.hebbia.ai",
    },
    # Character.ai
    {
        "product_name": "Character Chat",
        "startup_name": "Character.ai",
        "pricing_model": PricingModel.FREEMIUM,
        "description": "Neural language model chatbot platform enabling conversational interaction with custom AI personas.",
        "product_url": "https://character.ai",
    },
    # Synthesia
    {
        "product_name": "Synthesia Video Studio",
        "startup_name": "Synthesia",
        "pricing_model": PricingModel.PAID,
        "description": "AI video generation platform transforming text scripts into studio-quality videos with realistic avatars.",
        "product_url": "https://www.synthesia.io",
    },
    # Hugging Face Flagships
    {
        "product_name": "Hugging Face Spaces",
        "startup_name": "Hugging Face",
        "pricing_model": PricingModel.FREEMIUM,
        "description": "Cloud hosting platform for deploying interactive machine learning demos and Gradio/Streamlit apps.",
        "product_url": "https://huggingface.co/spaces",
    },
    {
        "product_name": "Hugging Face Inference Endpoints",
        "startup_name": "Hugging Face",
        "pricing_model": PricingModel.PAID,
        "description": "Dedicated, secure model deployment infrastructure on managed AWS, GCP, and Azure instances.",
        "product_url": "https://huggingface.co/inference-endpoints",
    },
    {
        "product_name": "HuggingChat",
        "startup_name": "Hugging Face",
        "pricing_model": PricingModel.FREE,
        "description": "Open-source chat interface powered by top open-access models with web search and tools.",
        "product_url": "https://huggingface.co/chat",
    },
]
