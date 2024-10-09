
import models
import soundfile as sf
import json
import AIModels
import utils
import os
import base64

SAMPLING_RATE = 16000

model_TTS_lambda = AIModels.NeuralTTS(
    models.get_model_TTS("de"),
    SAMPLING_RATE
)


def lambda_handler(event, context):
    print("[DEBUG] event", type(event))
    print("[DEBUG] context", type(context))
    
    body = json.loads(event["body"])
    text_string = body["value"]

    linear_factor = 0.2
    audio = model_TTS_lambda.getAudioFromSentence(
        text_string
    ).detach().numpy() * linear_factor
    
    random_file_name = utils.generateRandomString(20) + ".wav"
    sf.write("./" + random_file_name, audio, 16000)

    with open(random_file_name, "rb") as f:
        audio_byte_array = f.read()

    os.remove(random_file_name)
    return {
        "statusCode": 200,
        "headers": {
            "Access-Control-Allow-Headers": "*",
            "Access-Control-Allow-Origin":  "*",
            "Access-Control-Allow-Methods": "OPTIONS,POST,GET"
        },
        "body": json.dumps(
            {
                "wavBase64": str(
                    base64.b64encode(audio_byte_array)
                )[2:-1],
            },
        )
    }
