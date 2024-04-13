import time
from kubernetes import client as kubernetes_client
from kubernetes import utils
from kubernetes import config
import yaml


# read yaml file as object
with open("../Config/K8sYaml/Deployment/cron.yaml") as f:
    nginx_deployment_yaml = yaml.safe_load(f)

# load default config
# assume that default setting is set in ~/.kube/config
config.load_kube_config('../Config/kube.yaml')

# load kubernetes client
k8s_client = kubernetes_client.api_client.ApiClient()

# create pods from yaml object
utils.create_from_yaml(k8s_client, yaml_objects=[
                       nginx_deployment_yaml], namespace="default")

# wait for pods
time.sleep(3)

# list pods
core_v1_api = kubernetes_client.CoreV1Api()
pods = core_v1_api.list_namespaced_pod("default")
for pod in pods.items:
    print(f"{pod.metadata.name} {pod.status.phase} {pod.status.pod_ip} {pod.metadata.namespace}")