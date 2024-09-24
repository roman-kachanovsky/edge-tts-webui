import argparse
import os

import edge_tts
import gradio as gr

# https://speech.platform.bing.com/consumer/speech/synthesize/readaloud/voices/list?trustedclienttoken=6A5AA1D4EAFF4E9FB37E23D68491D6F4
DEFAULT_VOICE = 'ru-RU-DmitryNeural'
SUPPORTED_VOICES = {
    'Dmitry RU': DEFAULT_VOICE,
    'Svetlana RU': 'ru-RU-SvetlanaNeural',
    'Andrew EN': 'en-US-AndrewMultilingualNeural',
    'Ava EN': 'en-US-AvaMultilingualNeural',
}


def change_voice(voices):
    example = SUPPORTED_VOICES[voices]
    example_file = os.path.join(os.path.dirname(__file__), 'example/' + example + '.mp3')
    return example_file


async def text_to_speech(text, voices, rate, volume):
    output_file = 'output.mp3'
    voices = SUPPORTED_VOICES[voices]

    if rate >= 0:
        rates = rate = '+' + str(rate) + '%'
    else:
        rates = str(rate) + '%'

    if volume >= 0:
        volumes = '+' + str(volume) + '%'
    else:
        volumes = str(volume) + '%'

    communicate = edge_tts.Communicate(text, voices, rate=rates, volume=volumes, proxy=None)
    await communicate.save(output_file)
    audio_file = os.path.join(os.path.dirname(__file__), 'output.mp3')
    if os.path.exists(audio_file):
        return audio_file
    else:
        raise gr.Error('Convertation failed!')
        return FileNotFoundError


def clear():
    output_file = os.path.join(os.path.dirname(__file__), 'output.mp3')
    if os.path.exists(output_file):
        os.remove(output_file)
    return None, None


with gr.Blocks(css='style.css', title='text-to-speech') as demo:
    gr.Markdown("""
    # Text to speech conversion using Microsoft Edge
    """)
    with gr.Row():
        with gr.Column():
            text = gr.TextArea(label='Text', elem_classes='text-area')
            btn = gr.Button('Generate', elem_id='submit-btn')
        with gr.Column():
            voices = gr.Dropdown(
                choices=[
                    'Dmitry RU',
                    'Svetlana RU',
                    'Andrew EN',
                    'Ava EN',
                ],
                value='Dmitry RU',
                label='Voice',
                info='Please, choose voice',
                interactive=True,
            )

            example = gr.Audio(
                label='Voice example', value=f'example/{DEFAULT_VOICE}.mp3', interactive=False, elem_classes='example'
            )

            voices.change(fn=change_voice, inputs=voices, outputs=example)
            rate = gr.Slider(
                -100, 100, step=1, value=0, label='Increase / decrease speed', info='Speech speed', interactive=True
            )

            volume = gr.Slider(
                -100, 100, step=1, value=0, label='Increase / decrease volume', info='Volume level', interactive=True
            )
            audio = gr.Audio(label='Result')
            btn.click(fn=text_to_speech, inputs=[text, voices, rate, volume], outputs=[audio])

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--server-name', default='127.0.0.1', help='Server name')
    args = parser.parse_args()
    demo.launch(server_name=args.server_name)
