"""Configuration for Consent Agent"""

import os
from pathlib import Path

# Project paths
PROJECT_ROOT = Path(__file__).parent.parent
MODELS_DIR = PROJECT_ROOT / "models"
DATA_DIR = PROJECT_ROOT / "data"
LOGS_DIR = DATA_DIR / "logs"

# Model paths
WHISPER_MODEL_PATH = MODELS_DIR / "whisper-large-v3"
QWEN_MODEL_PATH = MODELS_DIR / "qwen3-14b-awq"
NLLB_MODEL_PATH = MODELS_DIR / "nllb-200-distilled-600m"
PIPER_MODEL_DIR = MODELS_DIR / "piper-tts"

# Language configuration
SUPPORTED_LANGUAGES = {
    "en": {"name": "English", "piper_voice": "en_US-lessac-medium", "nllb_code": "eng_Latn"},
    "es": {"name": "Spanish", "piper_voice": "es_ES-davefx-medium", "nllb_code": "spa_Latn"},
    "it": {"name": "Italian", "piper_voice": "it_IT-riccardo-x_low", "nllb_code": "ita_Latn"}
}

# Performance targets (from tech spec)
LATENCY_TARGETS = {
    "whisper_ms": 500,
    "translation_ms": 800,
    "llm_ms": 1200,
    "tts_ms": 400,
    "total_ms": 2200
}

# vLLM configuration for Qwen3-14B-AWQ
# In config/config.py, update VLLM_CONFIG:
VLLM_CONFIG = {
    "model": str(QWEN_MODEL_PATH),
    "quantization": "awq_marlin",
    "dtype": "float16",
    "max_model_len": 1024,  # Reduced from 4096 - smaller context = faster generation
    "gpu_memory_utilization": 0.80,  # Increased from 0.85 - use more VRAM
    "tensor_parallel_size": 1,
    "trust_remote_code": True,
    "disable_log_stats": True,
    "enforce_eager": False,  # Keep CUDA graphs enabled
    "enable_thinking": False, #Disable reasoning because it increases latency
    "enable_prefix_caching": True,  # Try disabling - can cause slowdown
    "enable_chunked_prefill": True,
    "max_num_batched_tokens": 4096,  # Increase batch processing
    "max_num_seqs": 64  # Allow more sequences in flight
}

# Whisper configuration
WHISPER_CONFIG = {
    "compute_type": "float16",
    "beam_size": 5,
    "vad_filter": True,
    "vad_parameters": {
        "threshold": 0.5,
        "min_speech_duration_ms": 250,
        "min_silence_duration_ms": 500
    }
}

# System prompts
SYSTEM_PROMPTS = {
    "en": """/no_think
    
    You are a healthcare assistant helping patients understand their medical procedures. You are embodied as Reachy, a friendly desktop robot.

IMPORTANT: Respond directly without showing your reasoning process. Do not use <think> tags.

Key behaviors:
- Explain medical concepts in simple, clear language
- Ask comprehension questions to verify understanding
- Detect confusion from vague or uncertain responses
- Re-explain if the patient seems confused
- Be warm, patient, and reassuring
- Keep responses concise (2-3 sentences maximum)
- Never provide medical advice, only procedural information

Respond naturally as if having a face-to-face conversation.""",

    "es": """/no_think
    Eres un asistente de salud que ayuda a los pacientes a comprender sus procedimientos médicos. Estás incorporado como Reachy, un robot de escritorio amigable.

IMPORTANTE: Responde directamente sin mostrar tu proceso de razonamiento. No uses etiquetas <think>.

Comportamientos clave:
- Explica conceptos médicos en lenguaje simple y claro
- Haz preguntas de comprensión para verificar el entendimiento
- Detecta confusión en respuestas vagas o inciertas
- Vuelve a explicar si el paciente parece confundido
- Sé cálido, paciente y tranquilizador
- Mantén las respuestas concisas (máximo 2-3 oraciones)
- Nunca des consejos médicos, solo información de procedimientos

Responde naturalmente como si tuvieras una conversación cara a cara.""",

    "it": """/no_think
    Sei un assistente sanitario che aiuta i pazienti a comprendere le loro procedure mediche. Sei incarnato come Reachy, un robot da scrivania amichevole.

IMPORTANTE: Rispondi direttamente senza mostrare il tuo processo di ragionamento. Non usare tag <think>.

Comportamenti chiave:
- Spiega i concetti medici in un linguaggio semplice e chiaro
- Fai domande di comprensione per verificare la comprensione
- Rileva confusione da risposte vaghe o incerte
- Rispiega se il paziente sembra confuso
- Sii caloroso, paziente e rassicurante
- Mantieni le risposte concise (massimo 2-3 frasi)
- Non dare mai consigli medici, solo informazioni procedurali

Rispondi naturalmente come se avessi una conversazione faccia a faccia."""
}

# Procedure templates (colonoscopy example)
PROCEDURE_INFO = {
    "colonoscopy": {
        "en": {
            "overview": "A colonoscopy is a test where a doctor uses a thin, flexible tube with a camera to look inside your colon (large intestine). It helps detect problems like polyps or cancer early.",
            "preparation": "Before the test, you'll need to drink a special liquid that cleans out your colon. This is very important because the doctor needs to see clearly inside.",
            "procedure": "During the test, you'll be given medicine to make you sleepy and comfortable. The test takes about 30-45 minutes. You won't feel pain.",
            "after": "After the procedure, you'll rest for about an hour. You'll need someone to drive you home because of the medicine. You can usually eat normally the same day."
        },
        "es": {
            "overview": "Una colonoscopia es una prueba donde un médico usa un tubo delgado y flexible con una cámara para ver dentro de su colon (intestino grueso). Ayuda a detectar problemas como pólipos o cáncer temprano.",
            "preparation": "Antes de la prueba, necesitará beber un líquido especial que limpia su colon. Esto es muy importante porque el médico necesita ver claramente adentro.",
            "procedure": "Durante la prueba, le darán medicina para que esté dormido y cómodo. La prueba toma unos 30-45 minutos. No sentirá dolor.",
            "after": "Después del procedimiento, descansará por aproximadamente una hora. Necesitará que alguien lo lleve a casa debido a la medicina. Generalmente puede comer normalmente el mismo día."
        },
        "it": {
            "overview": "Una colonscopia è un test in cui un medico usa un tubo sottile e flessibile con una telecamera per guardare dentro il colon (intestino crasso). Aiuta a rilevare problemi come polipi o cancro precocemente.",
            "preparation": "Prima del test, dovrai bere un liquido speciale che pulisce il colon. Questo è molto importante perché il medico deve vedere chiaramente all'interno.",
            "procedure": "Durante il test, ti verrà somministrata una medicina per farti dormire e stare comodo. Il test dura circa 30-45 minuti. Non sentirai dolore.",
            "after": "Dopo la procedura, riposerai per circa un'ora. Avrai bisogno di qualcuno che ti accompagni a casa a causa della medicina. Di solito puoi mangiare normalmente lo stesso giorno."
        }
    }
}
