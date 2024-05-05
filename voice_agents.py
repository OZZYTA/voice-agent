import os
import asyncio
from services.speech_to_text import SpeechToText
from services.text_to_speech import TextToSpeech
from services.llamager import LLamager
from eleven_labs_socket import ElevenLabsSocket
from groq import Groq

class ConversationManager:
    def __init__(self):
        self.transcription_response = ""
        self.llm = LLamager('elevenlabs')
        self.tts = TextToSpeech(os.getenv("ELEVENLABS_API_KEY"))
        self.tts_socket = ElevenLabsSocket('21m00Tcm4TlvDq8ikWAM')
        self.stt = SpeechToText(os.getenv("DEEPGRAM_API_KEY"))

    async def voice_agent_socket(self):
        def handle_full_sentence(full_sentence):
            self.transcription_response = full_sentence

        while True:
            await self.stt.transcript(handle_full_sentence, self.llm)

            if "adios" in self.transcription_response.lower():
                break

            await response_groq(self.transcription_response)

            self.transcription_response = ""

async def response_groq(transcription):
    client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
    completion = client.chat.completions.create(
        model="llama3-8b-8192",
        messages=[
            {"role": "user", "content": transcription}
        ],
        temperature=1,
        max_tokens=1024,
        top_p=1,
        stream=True,
        stop=None,
    )

    generated_text = ""
    for chunk in completion:
        generated_text += chunk.choices[0].delta.content or ""

    print(generated_text) 

if __name__ == "__main__":
    manager = ConversationManager()
    asyncio.run(manager.voice_agent_socket())
