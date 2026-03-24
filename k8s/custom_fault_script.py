#!/usr/bin/env python3
import time, json, os
import subprocess
from antithesis.random import random_choice

REPLICA_SCALING_SOURCE = "replica_scaling"

# ──────────────────────────────────────────────
# USER-DEFINED CONFIGURATION
# ──────────────────────────────────────────────
NAMESPACE = "default"
REPLICA_CHOICES = [3, 5, 7]

# Each entry defines a possible scaling action.
# On each run, one is randomly selected.
SCALE_ACTIONS = [
    {
        "scale_target": "deployment",
        "resource_name": "test-deployment",
    },
    {
        "scale_target": "statefulset",
        "resource_name": "test-statefulset",
    },
    {
        "scale_target": "pod",
        "resource_name": "test-pod",
        "label_selector": "app=test-pod",
    },
]
# ──────────────────────────────────────────────

# This script randomly performs one of several scaling actions on each run.
# It selects an action from SCALE_ACTIONS, then applies the appropriate strategy:
#   - deployment:   patches the Deployment's spec.replicas to a random count from REPLICA_CHOICES
#   - statefulset:  patches the StatefulSet's spec.replicas to a random count from REPLICA_CHOICES
#   - pod:          randomly adds or removes a single pod


# Executes a kubectl command and returns the result.
# Raises RuntimeError if the command exits with a non-zero status.
def __run_kubectl(cmd):
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"kubectl command failed: {' '.join(cmd)}\n{result.stderr.strip()}")
    return result


# Queries the cluster for all pods matching the given label selector
# in the specified namespace. Returns a list of pod names.
def __get_current_pods(namespace, label_selector):
    cmd = [
        "kubectl", "get", "pods",
        "-n", namespace,
        "-l", label_selector,
        "-o", "json"
    ]
    result = __run_kubectl(cmd)
    pods = json.loads(result.stdout)
    return [p["metadata"]["name"] for p in pods.get("items", [])]


# Patches a Deployment or StatefulSet's spec.replicas to the given count
# using a strategic merge patch.
def __scale_resource(namespace, resource_type, resource_name, replica_count):
    patch_payload = json.dumps({"spec": {"replicas": replica_count}})
    cmd = [
        "kubectl", "patch", resource_type, resource_name,
        "-n", namespace,
        "-p", patch_payload,
        "--type", "merge"
    ]
    result = __run_kubectl(cmd)
    return {"command": " ".join(cmd), "stdout": result.stdout.strip()}


# Creates a single new pod with the given resource name as the image
# and a unique timestamped name. The pod is labeled with the provided
# label selector so it can be discovered later.
def __add_pod(namespace, resource_name, label_selector):
    pod_name = f"{resource_name}-manual-{int(time.time())}"
    cmd = [
        "kubectl", "run", pod_name,
        "-n", namespace,
        "--image", f"{resource_name}:latest",
        "-l", label_selector,
        "--restart", "Never"
    ]
    result = __run_kubectl(cmd)
    return {"action": "create", "pod": pod_name, "stdout": result.stdout.strip()}


# Deletes a single randomly chosen pod matching the label selector.
# If no pods exist, returns gracefully without error.
def __remove_pod(namespace, label_selector):
    current_pods = __get_current_pods(namespace, label_selector)
    if not current_pods:
        return {"action": "delete", "pod": None, "detail": "no pods to remove"}

    pod_name = random_choice(current_pods)
    cmd = [
        "kubectl", "delete", "pod", pod_name,
        "-n", namespace
    ]
    result = __run_kubectl(cmd)
    return {"action": "delete", "pod": pod_name, "stdout": result.stdout.strip()}


# Randomly decides whether to add or remove a single pod.
# Uses Antithesis random_choice so the platform can explore both branches.
def __scale_pod(namespace, resource_name, label_selector):
    action = random_choice(["add", "remove"])
    if action == "add":
        return __add_pod(namespace, resource_name, label_selector)
    else:
        return __remove_pod(namespace, label_selector)


# Main entry point for a scaling event. Selects the appropriate strategy
# based on the action's scale_target:
#   - deployment/statefulset: patches spec.replicas to a random count
#   - pod: randomly adds or removes a single pod
# Logs fault info via FuzzPipeLogger and reports results via inst.fuzz_msg.
def __replica_scale_event(namespace, action, replica_choices):
    scale_target = action["scale_target"]
    resource_name = action["resource_name"]

    if scale_target in ("deployment", "statefulset"):
        replica_count = random_choice(replica_choices)

        fault_info = {
            "type": "replica_scaling",
            "name": "scale",
            "affected_nodes": ["ALL"],
            "details": {
                "scale_target": scale_target,
                "resource_name": resource_name,
                "namespace": namespace,
                "new_replicas": replica_count
            }
        }

        print(f"[fault] {json.dumps(fault_info)}")

        result = __scale_resource(namespace, scale_target, resource_name, replica_count)

    elif scale_target == "pod":
        label_selector = action.get("label_selector", f"app={resource_name}")
        result = __scale_pod(namespace, resource_name, label_selector)

        fault_info = {
            "type": "replica_scaling",
            "name": "scale_pod",
            "affected_nodes": ["ALL"],
            "details": {
                "scale_target": scale_target,
                "resource_name": resource_name,
                "namespace": namespace,
                "result": result
            }
        }

        print(f"[fault] {json.dumps(fault_info)}")

    scale_data_json = {
        "scale_target": scale_target,
        "resource_name": resource_name,
        "namespace": namespace,
        "result": result
    }

    print(f"[result] {json.dumps(scale_data_json)}")

    return


if __name__ == "__main__":
    action = random_choice(SCALE_ACTIONS)
    __replica_scale_event(NAMESPACE, action, REPLICA_CHOICES)