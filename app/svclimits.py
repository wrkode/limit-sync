from flask import Flask, request, jsonify
import json

app = Flask(__name__)

@app.route('/sync', methods=['POST'])
def sync():
    body = request.get_json()
    print("Received request:", json.dumps(body, indent=2))
    parent = body.get("parent")
    children = body.get("children")
    print("Received children:", json.dumps(children, indent=2))

    desired_cpu = parent.get("spec", {}).get("resources", {}).get("cpu", "500m")
    desired_memory = parent.get("spec", {}).get("resources", {}).get("memory", "128Mi")
    desired_ephemeralStorage = parent.get("spec", {}).get("resources", {}).get("ephemeral-storage", "500Mi")

    desired_deployments = {}
    for name, deployment in children.get("Deployment.apps/v1", {}).items():
        desired_deployment = deployment.copy()

        containers = desired_deployment["spec"]["template"]["spec"]["containers"]

        for container in containers:
            if "resources" not in container:
                container["resources"] = {
                    "limits": {
                        "cpu": desired_cpu,
                        "memory": desired_memory,
                        "ephemeral-storage": desired_ephemeralStorage,
                    }
                }
            else:
                if "limits" not in container["resources"]:
                    container["resources"]["limits"] = {
                        "cpu": desired_cpu,
                        "memory": desired_memory,
                        "ephemeral-storage": desired_ephemeralStorage,
                    }
                else:
                    if "cpu" not in container["resources"]["limits"]:
                        container["resources"]["limits"]["cpu"] = desired_cpu
                    if "memory" not in container["resources"]["limits"]:
                        container["resources"]["limits"]["memory"] = desired_memory
                    if "ephemeral-storage" not in container["resources"]["limits"]:
                        container["resources"]["limits"]["ephemeral-storage"] = desired_ephemeralStorage
                        
        desired_deployments[name] = desired_deployment

    response = {"children": list(desired_deployments.values())}
    print("Generated response:", json.dumps(response, indent=2))
    return jsonify(response)



@app.route('/finalize', methods=['POST'])
def finalize():
    return jsonify({"status": "Success"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
