# Edge and Cloud Based ML Pipeline

This project implements a scalable, distributed face recognition system that leverages **IoT edge computing** and **AWS cloud services** to deliver low-latency inference.

Video frames are captured on a simulated IoT client device, processed locally for face detection using **AWS IoT Greengrass**, and then passed to the cloud for face recognition using **AWS Lambda** and **FaceNet**. The entire pipeline is built with **event-driven communication** using **MQTT** and **Amazon SQS**.

---

## 📌 Architecture

![image](https://github.com/user-attachments/assets/bafe0368-a054-4a5d-b595-1d8fc3521e50)

- **Client Device** (EC2 instance) captures video frames and publishes them via MQTT.
- **Core Device** (also EC2) runs AWS Greengrass and hosts the face detection component using MTCNN.
- Detected faces are sent to an **SQS Request Queue**.
- **AWS Lambda** processes these using FaceNet and publishes results to an **SQS Response Queue**.
- The client device retrieves recognition results and presents identified names.

---

## 📄 Files

- **`fd_component.py`**  
  Contains the edge-based face detection logic using the MTCNN model, deployed as an AWS Greengrass component that subscribes to an MQTT topic, processes incoming video frames, and pushes results to the request queue.

- **`fr_lambda.py`**  
  Implements the AWS Lambda function that performs face recognition using the FaceNet model by reading messages from the request queue and writing the identification results to the response queue.

> 🔧 **Simulation Note**  
The IoT client and core devices were simulated using Amazon EC2 instances (Ubuntu and Amazon Linux), requiring minimal custom code and relying heavily on AWS IoT Greengrass configurations, IAM policies, MQTT setup, and secure provisioning.

---

## 🔧 Technologies Used

- **AWS EC2** – to simulate both IoT client and core devices  
- **AWS IoT Greengrass v2** – to deploy edge components (face detection)  
- **AWS Lambda** – to perform face recognition in the cloud  
- **Amazon SQS** – for request/response messaging  
- **MQTT** – for lightweight publish/subscribe communication  
- **MTCNN** – for face detection  
- **FaceNet** – for face recognition  
- **Python** – for all component logic and message handling  
- **facenet-pytorch** – imported as code into the artifacts directory

---

## 🚀 Key Features

- Real-time face detection and recognition via edge-to-cloud integration  
- Decoupled, event-driven pipeline using AWS-native services  
- Edge processing conserves cloud bandwidth and enhances privacy  
- Fully functional simulation without physical IoT hardware

---




