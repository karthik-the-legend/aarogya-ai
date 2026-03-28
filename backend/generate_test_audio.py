import sys
sys.path.insert(0, 'backend')

# Use gTTS to generate real Hindi audio
from gtts import gTTS
import os

print("Generating Hindi audio using gTTS...")
tts = gTTS(text="मुझे बुखार है और सिरदर्द है", lang='hi')
tts.save("test_hindi.mp3")
print("Saved: test_hindi.mp3")

print("Generating Telugu audio...")
tts2 = gTTS(text="నాకు జ్వరం వచ్చింది", lang='te')
tts2.save("test_telugu.mp3")
print("Saved: test_telugu.mp3")

print("Generating Tamil audio...")
tts3 = gTTS(text="எனக்கு காய்ச்சல் இருக்கிறது", lang='ta')
tts3.save("test_tamil.mp3")
print("Saved: test_tamil.mp3")

print("All audio files generated!")