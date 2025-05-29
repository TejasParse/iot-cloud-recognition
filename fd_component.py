import json
import base64
import boto3
import io
import sys
sys.stdout = sys.stderr
import traceback
from PIL import Image

from facenet_pytorch import MTCNN  # You must copy the code folder into artifacts, not install via pip

QOS = '1'

# Update with your actual values
ASU_ID = "1232625370"
IOT_THING_NAME = f"{ASU_ID}-IoTThing"
TOPIC = f"clients/{IOT_THING_NAME}"
REQUEST_QUEUE_URL = f"https://sqs.us-east-1.amazonaws.com/182399699820/1232625370-req-queue"
RESPONSE_QUEUE_URL = f"https://sqs.us-east-1.amazonaws.com/182399699820/1232625370-resp-queue"

# Initialize MTCNN
mtcnn = MTCNN(image_size=240, margin=0, min_face_size=20)

IAM_ACCESSKEY = ""
IAM_SECRETKEY = ""

iam_session = boto3.Session(aws_access_key_id=IAM_ACCESSKEY, aws_secret_access_key=IAM_SECRETKEY)

# SQS client
sqs = iam_session.client("sqs", region_name="us-east-1")

# MQTT connection (managed by Greengrass pubsub internally)
def message_received(topic, payload, **kwargs):
    try:
        print(f"Message received on topic {topic}")
        msg = json.loads(payload.decode("utf-8"))
        base64_image = msg["encoded"]
        request_id = msg["request_id"]
        filename = msg["filename"]

        # Decode base64 image
        image_bytes = base64.b64decode(base64_image)
        img = Image.open(io.BytesIO(image_bytes)).convert("RGB")

        # Face detection
        face_output, prob = mtcnn(img, return_prob=True)

        if face_output is None:
            print(f"No face detected for request {request_id}")

            # Send directly to response queue for bonus
            sqs.send_message(
                QueueUrl=RESPONSE_QUEUE_URL,
                MessageBody=json.dumps({
                    "request_id": request_id,
                    "filename": filename,
                    "result": "No-Face"
                })
            )
            return

        # Normalize and encode detected face
        processed = face_output - face_output.min()
        processed = processed / processed.max()
        processed = (processed * 255).byte().permute(1, 2, 0).numpy()
        image_saved = Image.fromarray(processed, mode="RGB")

        buffer = io.BytesIO()
        image_saved.save(buffer, format="JPEG")
        face_base64 = base64.b64encode(buffer.getvalue()).decode("utf-8")

        # Send to SQS request queue for recognition
        message = {
            "request_id": request_id,
            "filename": filename,
            "content": face_base64
        }

        sqs.send_message(
            QueueUrl=REQUEST_QUEUE_URL,
            MessageBody=json.dumps(message)
        )

        print(f"Face for {request_id} sent to recognition queue.")

    except Exception as e:
        print("Error processing message:", e)
        traceback.print_exc()

# Main entry: subscribe to MQTT topic using local pubsub
def main():
    try:
        from awsiot.greengrasscoreipc.clientv2 import GreengrassCoreIPCClientV2

        print("Checkpoint: 1")

        ipc_client = GreengrassCoreIPCClientV2()

        print("Checkpoint: 2")

        def on_stream_event(event):
            print(event, "Please print hojana")
            payload = event.message.payload
            message_received(TOPIC, payload)

        print(f"Subscribing to topic: {TOPIC}")
        ipc_client.subscribe_to_iot_core(
            topic_name=TOPIC,
            qos=QOS,
            on_stream_event=on_stream_event
        )

        # Keep running
        while True:
            pass

    except Exception as e:
        print("Failed to subscribe to topic:", e)
        traceback.print_exc()


if __name__ == "__main__":
    print("Checkpoint: 0")
    main()
