# ea2da6ff2169e6b9a2ee196a16f6c5b4
import tempfile
import io
from gtts import gTTS
import requests
from pydub import AudioSegment
from pydub.playback import play
from moviepy.editor import *
from moviepy.video.fx.resize import resize

import os

num_quotes = 2
# create_video usage:
audio_path = "audio/"
image_path = "images/image.png"
output_video_path = "videos/output_video.mp4"

def get_random_quote():
    url = "https://api.quotable.io/random"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        return data["content"], data["author"]
    else:
        return "Failed to fetch quote", None

def get_quotes(num_quotes):
    quotes = []
    for _ in range(num_quotes):
        quote, author = get_random_quote()
        quotes.append(quote)
    return quotes

def create_tts(quote, number):
    language = 'en'

    # Passing the text and language to the engine, 
    # here we have marked slow=False. Which tells 
    # the module that the converted audio should 
    # have a high speed
    myobj = gTTS(text=quote, lang=language, tld="us", slow=False)

    # Saving the converted audio in a mp3 file named
    # welcome 
    file_path = f"{audio_path}_{number}.mp3"
    myobj.save(file_path)

def create_voiceover_online(quote, number):
    url = "https://api.elevenlabs.io/v1/text-to-speech/JBFqnCBsd6RMkjVDRZzb"

    querystring = {"output_format":"mp3_44100_128"}

    payload = {
        "text": quote,
        "voice_settings": {
            "similarity_boost": 1,
            "stability" : 1,
            "style": 1,
            "use_speaker_boost": True,
        }
    }
    headers = {
        "xi-api-key": "ea2da6ff2169e6b9a2ee196a16f6c5b4",
        "Content-Type": "application/json"
    }

    response = requests.request("POST", url, json=payload, headers=headers, params=querystring)

    CHUNK_SIZE = 1024
    # file_path =  + number + ".mp3"
    file_path = f"{audio_path}_{number}.mp3"
    # Check if request was successful
    if response.status_code == 200:

        with open(file_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=CHUNK_SIZE):
                if chunk:
                    f.write(chunk)
    else:
        print("Failed to retrieve voiceover:", response.text)


def create_video_with_voiceover_and_text(quote_text, audio_path, image_path):
   
    # Load the image
    image_clip = ImageClip(image_path)
    

    # screen size
    screensize = (image_clip.size[0], 0)
    quote = wrap(quote_text, image_clip.size[0])

     # Generate text
    text_clip = TextClip(txt=quote.upper(), font="Lane", fontsize=48, color="white", size=screensize, align='center', method="caption", kerning=-2, interline=-1)
    
    
    # Load the audio file
    audio_clip = AudioFileClip(audio_path)
    duration = audio_clip.duration

    text_clip = text_clip.set_duration(duration)
    image_clip = image_clip.set_duration(duration).set_position("center")

    image_width, image_height = text_clip.size

    padding_width = 20     # 10 pixels on each side
    padding_height = 20    # 10 pixels on each side# We create the ColorClip object after creating the TextClip object
    #
    color_clip = ColorClip(size=(image_width + padding_width, 
                                image_height + padding_height),
                        color=(0, 255, 255))# Let's make the background a little transparent     
    #
    color_clip = color_clip.set_opacity(.5)# Now we need to set the position of 'text_clip' to 'center'
    #
    text_clip = text_clip.set_position('center')


    # Overlay text with background on the image
    clip_to_overlay  = CompositeVideoClip([color_clip, text_clip])
    clip_to_overlay  = clip_to_overlay.set_duration(duration).set_start(0).crossfadein(1)
    clip_to_overlay = clip_to_overlay.set_position('center')

    final_clip = CompositeVideoClip([image_clip, clip_to_overlay], size=(720, 1280))

    # Combine with audio clip
    final_clip = final_clip.set_audio(audio_clip)

    
    return final_clip

    # Write the video file
    # final_clip.write_videofile(output_video_path, codec="libx264", fps=24)


def wrap(string, max_width):
    s=''
    for i in range(0,len(string),max_width):
        s+=string[i:i+max_width]
        s+='\n'
    return s


def create_quoted_video():

    # get_random_quote usage:
    # quote, author = get_random_quote()

    
    quotes = get_quotes(num_quotes)

    # List to hold video segments
    video_segments = []

    for i, quote in enumerate(quotes):
        # create_voiceover(quote, i)
        create_tts(quote, i)
        
        # Create video segment
        segment = create_video_with_voiceover_and_text(quote, f"{audio_path}_{i}.mp3", image_path)

        # Add segment to list
        video_segments.append(segment)
    
    # Concatenate video segments
    final_video = concatenate_videoclips(video_segments)

    # Write the final video file
    final_video.write_videofile(output_video_path, codec="libx264", fps=24)
    
    # if author:
    #     # print(f"\"{quote}\" - {author}")
    #     create_voiceover(quote)

    #     # create_video usage:
    #     audio_path = "audio/output.mp3"
    #     image_path = "images/image.png"
    #     output_video_path = "output_video.mp4"

    #     create_video_with_voiceover_and_text(quote, audio_path, image_path, output_video_path)

    # else:
    #     print(quote)

create_quoted_video()