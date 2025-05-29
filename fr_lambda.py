import json
import boto3
import base64
from PIL import Image
import io
import torch
import numpy as np
from facenet_pytorch import InceptionResnetV1

sqs = boto3.client('sqs', region_name='us-east-1')

QUEUE_URL = "https://sqs.us-east-1.amazonaws.com/182399699820/1232625370-resp-queue"

resnet_model = InceptionResnetV1(pretrained='vggface2').eval()
saved_data = torch.load("resnetV1_video_weights.pt")
embedding_list = saved_data[0]
name_list = saved_data[1]

def recognize_from_base64(base64_str):
    try:
        img_data = base64.b64decode(base64_str)
        input = Image.open(io.BytesIO(img_data)).convert("RGB")
        # input = input.resize((160, 160))

        processed = np.array(input, dtype=np.float32) / 255.0
        processed = np.transpose(processed, (2, 0, 1))
        img_tensor = torch.tensor(processed, dtype=torch.float32).unsqueeze(0)

        with torch.no_grad():
            output = resnet_model(img_tensor)

        distances = [torch.dist(output, db).item() for db in embedding_list]
        min_idx = distances.index(min(distances))
        return name_list[min_idx]

    except Exception as e:
        print("Failed:", str(e))
        return "Unknown"

def handler(event, context):
    print("Received event:", json.dumps(event))

    for record in event['Records']:
        try:
            message = json.loads(record['body'])
            request_id = message['request_id']
            filename = message['filename']
            base64_face = message['content']

            identity = recognize_from_base64(base64_face)

            result = {
                "request_id": request_id,
                "result": identity
            }

            sqs.send_message(
                QueueUrl=QUEUE_URL,
                MessageBody=json.dumps(result)
            )

            print(f"Recognition sent for {filename}: {identity}")

        except Exception as e:
            print("Error:", e)

    return {
        "statusCode": 200,
        "body": json.dumps("Face recognition completed.")
    }
