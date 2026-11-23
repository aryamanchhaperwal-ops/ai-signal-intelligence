"""Seed Database of 50 Prominent AI Startups with Aliases and Canonical Metadata."""

from typing import Dict, List, TypedDict


class StartupSeed(TypedDict):
    canonical_name: str
    aliases: List[str]
    website: str
    description: str


AI_STARTUP_SEEDS: List[StartupSeed] = [
    {
        "canonical_name": "OpenAI",
        "aliases": ["OpenAI Inc", "OpenAI, Inc.", "openai.com", "ChatGPT", "Open AI"],
        "website": "https://openai.com",
        "description": "Frontier AI research and deployment company behind GPT-4 and ChatGPT.",
    },
    {
        "canonical_name": "Anthropic",
        "aliases": ["Anthropic PBC", "Anthropic AI", "Claude AI", "anthropic.com"],
        "website": "https://anthropic.com",
        "description": "AI safety and research company behind the Claude model family.",
    },
    {
        "canonical_name": "Mistral AI",
        "aliases": ["Mistral", "Mistral.ai", "Mistral AI SAS", "mistral.ai"],
        "website": "https://mistral.ai",
        "description": "European frontier AI company providing open-weights and commercial models.",
    },
    {
        "canonical_name": "Cohere",
        "aliases": ["Cohere Inc", "Cohere AI", "cohere.com"],
        "website": "https://cohere.com",
        "description": "Enterprise LLM and retrieval platform.",
    },
    {
        "canonical_name": "Perplexity AI",
        "aliases": ["Perplexity", "Perplexity.ai", "Perplexity Inc", "perplexity.ai"],
        "website": "https://perplexity.ai",
        "description": "Conversational AI search engine delivering sourced answers.",
    },
    {
        "canonical_name": "Hugging Face",
        "aliases": ["Hugging Face Inc", "HuggingFace", "huggingface.co", "HF"],
        "website": "https://huggingface.co",
        "description": "Open-source AI platform and repository for machine learning models and datasets.",
    },
    {
        "canonical_name": "Scale AI",
        "aliases": ["Scale", "Scale AI Inc", "scale.com"],
        "website": "https://scale.com",
        "description": "Data infrastructure platform providing RLHF, fine-tuning, and annotations.",
    },
    {
        "canonical_name": "Runway",
        "aliases": ["RunwayML", "Runway AI", "Runway AI, Inc.", "runwayml.com"],
        "website": "https://runwayml.com",
        "description": "Generative media and video research tools (Gen-2, Gen-3).",
    },
    {
        "canonical_name": "Midjourney",
        "aliases": ["Midjourney Inc", "Midjourney AI", "midjourney.com"],
        "website": "https://midjourney.com",
        "description": "Independent research lab creating generative text-to-image AI tools.",
    },
    {
        "canonical_name": "Databricks",
        "aliases": ["Databricks Inc", "databricks.com", "MosaicML"],
        "website": "https://databricks.com",
        "description": "Data and AI platform for lakehouse analytics and open LLM training.",
    },
    {
        "canonical_name": "xAI",
        "aliases": ["xAI Corp", "x.ai", "Grok"],
        "website": "https://x.ai",
        "description": "AI company focused on understanding the universe and building Grok.",
    },
    {
        "canonical_name": "Synthesia",
        "aliases": ["Synthesia Ltd", "synthesia.io"],
        "website": "https://synthesia.io",
        "description": "AI video generation platform transforming text to avatar video.",
    },
    {
        "canonical_name": "ElevenLabs",
        "aliases": ["Eleven Labs", "ElevenLabs Inc", "elevenlabs.io"],
        "website": "https://elevenlabs.io",
        "description": "Voice AI and realistic speech synthesis platform.",
    },
    {
        "canonical_name": "Together AI",
        "aliases": ["Together", "Together.ai", "Together Computer Inc", "together.ai"],
        "website": "https://together.ai",
        "description": "Decentralized cloud platform for training and fine-tuning open source AI models.",
    },
    {
        "canonical_name": "Character.AI",
        "aliases": ["Character AI", "Character.ai Inc", "c.ai"],
        "website": "https://character.ai",
        "description": "Conversational neural agents providing personalized dialogue experiences.",
    },
    {
        "canonical_name": "Groq",
        "aliases": ["Groq Inc", "groq.com"],
        "website": "https://groq.com",
        "description": "LPU Inference Engine manufacturer accelerating deterministic LLM processing.",
    },
    {
        "canonical_name": "Anyscale",
        "aliases": ["Anyscale Inc", "anyscale.com", "Ray AI"],
        "website": "https://anyscale.com",
        "description": "Distributed computing platform powered by Ray for AI workloads.",
    },
    {
        "canonical_name": "Stability AI",
        "aliases": ["Stability", "Stability.ai", "Stability AI Ltd"],
        "website": "https://stability.ai",
        "description": "Developer of open-source generative models including Stable Diffusion.",
    },
    {
        "canonical_name": "Inflection AI",
        "aliases": ["Inflection", "inflection.ai", "Pi AI"],
        "website": "https://inflection.ai",
        "description": "Personal AI enterprise company and creators of Pi.",
    },
    {
        "canonical_name": "Glean",
        "aliases": ["Glean Inc", "glean.com", "Glean Search"],
        "website": "https://glean.com",
        "description": "AI-powered enterprise work assistant and search platform.",
    },
    {
        "canonical_name": "Jasper",
        "aliases": ["Jasper AI", "Jasper.ai", "UseJasper"],
        "website": "https://jasper.ai",
        "description": "Enterprise AI marketing and copywriting copilot platform.",
    },
    {
        "canonical_name": "Writer",
        "aliases": ["Writer.com", "Writer AI", "Writer Inc"],
        "website": "https://writer.com",
        "description": "Full-stack generative AI platform built for enterprise content workflows.",
    },
    {
        "canonical_name": "Adept AI",
        "aliases": ["Adept", "Adept Labs", "Adept.ai"],
        "website": "https://adept.ai",
        "description": "Machine learning research lab building useful general intelligence for software.",
    },
    {
        "canonical_name": "Cursor",
        "aliases": ["Anysphere", "Cursor AI", "Cursor Editor", "anysphere.co"],
        "website": "https://cursor.com",
        "description": "AI-powered code editor and engineering intelligence environment.",
    },
    {
        "canonical_name": "Harvey",
        "aliases": ["Harvey AI", "Harvey.ai", "Counsel AI"],
        "website": "https://harvey.ai",
        "description": "Generative AI platform designed for professional legal and compliance teams.",
    },
    {
        "canonical_name": "Cognition",
        "aliases": ["Cognition AI", "Devin AI", "Cognition Labs"],
        "website": "https://cognition.ai",
        "description": "Applied AI lab building Devin, the autonomous AI software engineer.",
    },
    {
        "canonical_name": "Poolside",
        "aliases": ["Poolside AI", "Poolside.ai"],
        "website": "https://poolside.ai",
        "description": "AI lab creating foundational models for code generation and software development.",
    },
    {
        "canonical_name": "Decagon",
        "aliases": ["Decagon AI", "decagon.ai"],
        "website": "https://decagon.ai",
        "description": "Generative AI customer support automation engine.",
    },
    {
        "canonical_name": "Sakana AI",
        "aliases": ["Sakana", "sakana.ai"],
        "website": "https://sakana.ai",
        "description": "Tokyo-based R&D lab pioneering nature-inspired evolutionary model merging.",
    },
    {
        "canonical_name": "Shield AI",
        "aliases": ["Shield AI Inc", "shield.ai"],
        "website": "https://shield.ai",
        "description": "Defense technology startup building autonomous pilot AI for uncrewed systems.",
    },
    {
        "canonical_name": "Helsing",
        "aliases": ["Helsing AI", "helsing.ai"],
        "website": "https://helsing.ai",
        "description": "European defense AI firm processing live sensor telemetry in real time.",
    },
    {
        "canonical_name": "DeepL",
        "aliases": ["DeepL SE", "DeepL GmbH", "deepl.com"],
        "website": "https://deepl.com",
        "description": "Deep learning translation and linguistic communication platform.",
    },
    {
        "canonical_name": "Snorkel AI",
        "aliases": ["Snorkel", "snorkel.ai", "Snorkel Flow"],
        "website": "https://snorkel.ai",
        "description": "Programmatic data labeling and foundational model development platform.",
    },
    {
        "canonical_name": "Weights & Biases",
        "aliases": ["W&B", "wandb", "Weights and Biases", "wandb.ai"],
        "website": "https://wandb.ai",
        "description": "MLOps platform for experiment tracking, model evaluation, and dataset versioning.",
    },
    {
        "canonical_name": "Pinecone",
        "aliases": ["Pinecone Systems", "pinecone.io"],
        "website": "https://pinecone.io",
        "description": "Managed serverless vector database for production AI search applications.",
    },
    {
        "canonical_name": "Weaviate",
        "aliases": ["Weaviate B.V.", "weaviate.io", "Semi Technologies"],
        "website": "https://weaviate.io",
        "description": "Open-source vector search engine and database.",
    },
    {
        "canonical_name": "Qdrant",
        "aliases": ["Qdrant Solutions", "qdrant.tech"],
        "website": "https://qdrant.tech",
        "description": "High-performance vector similarity search engine written in Rust.",
    },
    {
        "canonical_name": "Chroma",
        "aliases": ["Chroma DB", "chromadb", "trychroma"],
        "website": "https://trychroma.com",
        "description": "Open-source AI-native embedding database for LLM applications.",
    },
    {
        "canonical_name": "LangChain",
        "aliases": ["LangChain Inc", "langchain.com", "LangSmith"],
        "website": "https://langchain.com",
        "description": "Framework and observability suite for building context-aware reasoning applications.",
    },
    {
        "canonical_name": "LlamaIndex",
        "aliases": ["Llama Index", "llamaindex.ai", "GPT Index"],
        "website": "https://llamaindex.ai",
        "description": "Data framework connecting enterprise data sources to LLMs.",
    },
    {
        "canonical_name": "Baseten",
        "aliases": ["Baseten Inc", "baseten.co"],
        "website": "https://baseten.co",
        "description": "Machine learning model serving infrastructure designed for low-latency inference.",
    },
    {
        "canonical_name": "Modal",
        "aliases": ["Modal Labs", "modal.com"],
        "website": "https://modal.com",
        "description": "Cloud compute platform for running generative AI models and serverless containers.",
    },
    {
        "canonical_name": "Replicate",
        "aliases": ["Replicate Inc", "replicate.com"],
        "website": "https://replicate.com",
        "description": "Cloud API platform allowing developers to run open-source models with minimal code.",
    },
    {
        "canonical_name": "Cerebras Systems",
        "aliases": ["Cerebras", "cerebras.net"],
        "website": "https://cerebras.net",
        "description": "Pioneers of wafer-scale engine processors for high-performance AI compute.",
    },
    {
        "canonical_name": "SambaNova Systems",
        "aliases": ["SambaNova", "sambanova.ai"],
        "website": "https://sambanova.ai",
        "description": "Enterprise-scale reconfigurable dataflow architecture for generative AI models.",
    },
    {
        "canonical_name": "Tenstorrent",
        "aliases": ["Tenstorrent Inc", "tenstorrent.com"],
        "website": "https://tenstorrent.com",
        "description": "RISC-V and AI hardware architecture development startup.",
    },
    {
        "canonical_name": "Lambda",
        "aliases": ["Lambda Labs", "lambdalabs.com"],
        "website": "https://lambdalabs.com",
        "description": "GPU cloud and workstation infrastructure purpose-built for deep learning engineers.",
    },
    {
        "canonical_name": "CoreWeave",
        "aliases": ["CoreWeave Inc", "coreweave.com"],
        "website": "https://coreweave.com",
        "description": "Specialized cloud provider delivering massive GPU clusters for modern AI workloads.",
    },
    {
        "canonical_name": "Physical Intelligence",
        "aliases": ["Physical Intelligence Inc", "pi.company", "pi-company"],
        "website": "https://physicalintelligence.company",
        "description": "Robotics foundation model lab developing universal intelligence for physical robots.",
    },
    {
        "canonical_name": "Covariant",
        "aliases": ["Covariant.ai", "covariant"],
        "website": "https://covariant.ai",
        "description": "Universal AI robotic manipulation platform for warehouse automation.",
    },
]
