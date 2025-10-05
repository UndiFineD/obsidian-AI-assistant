# Compatibility shim so tests can `import voice` and patch/reload cleanly
import importlib
import backend.voice as _backend_voice
_backend_voice = importlib.reload(_backend_voice)

# Expose key symbols and ensure reload affects this shim too
voice_transcribe = _backend_voice.voice_transcribe  # noqa: F401
router = _backend_voice.router  # noqa: F401
MODEL_PATH = _backend_voice.MODEL_PATH  # noqa: F401
get_vosk_model = _backend_voice.get_vosk_model  # noqa: F401
model = getattr(_backend_voice, 'model', None)  # noqa: F401

def __getattr__(name):
	# Delegate attribute access to backend.voice so patches remain consistent
	return getattr(_backend_voice, name)

def __reload__():
	# Helper so tests can importlib.reload(voice) and refresh backend.voice
	global _backend_voice, voice_transcribe, router, MODEL_PATH, get_vosk_model, model
	_backend_voice = importlib.reload(_backend_voice)
	voice_transcribe = _backend_voice.voice_transcribe
	router = _backend_voice.router
	MODEL_PATH = _backend_voice.MODEL_PATH
	get_vosk_model = _backend_voice.get_vosk_model
	model = getattr(_backend_voice, 'model', None)
