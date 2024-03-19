from kubernetes import client, config
from kubernetes.stream import stream

config.load_kube_config()
api_client = client.CoreV1Api()