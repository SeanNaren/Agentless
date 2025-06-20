import json
import os
from pathlib import Path

import requests
from swebench.harness.constants import (
    KEY_MODEL,
    KEY_PREDICTION,
    RUN_EVALUATION_LOG_DIR,
)
from swebench.harness.grading import get_eval_report
from swebench.harness.test_spec import make_test_spec, TestSpec


DOCKER_PATCH = "/tmp/patch.diff"
DOCKER_USER = "root"
DOCKER_WORKDIR = "/testbed"
LOG_REPORT = "report.json"
LOG_INSTANCE = "run_instance.log"
LOG_TEST_OUTPUT = "test_output.txt"
UTF8 = "utf-8"

class SkillsExecutionClient:
    """
    A client to interact with the Git Patch Flask server.
    """

    def __init__(self, host=None, port=None):
        final_port = port or int(os.getenv('NEMO_SKILLS_SANDBOX_PORT') or 6005)
        final_host = host or 'http://127.0.0.1'
        self.base_url = f"{final_host.rstrip('/')}:{final_port}"
        self.session = requests.Session()

    def _make_request(self, endpoint, data):
        """
        Helper method to make a POST request and handle responses.
        """
        url = f"{self.base_url}/{endpoint}"
        headers = {"Content-Type": "application/json"}
        try:
            response = self.session.post(url, data=json.dumps(data), headers=headers)
            response.raise_for_status()  # Raise an exception for bad status codes (4xx or 5xx)
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"An error occurred while connecting to {url}: {e}")
            return None
        except json.JSONDecodeError:
            print(f"Failed to decode JSON response from {url}. Raw response: {response.text}")
            return None

    def apply_patch(self, workdir, patch_content):
        """
        Sends a request to the /apply-patch endpoint.
        """
        print(f"--- Attempting to apply patch in '{workdir}' ---")
        payload = {
            "workdir": workdir,
            "patch": patch_content
        }
        response = self._make_request("apply-patch", payload)
        if not response['patch_success']:
            print("warning, patch did not successfully apply.")
        return response['output']

    def execute_command(self, workdir, command):
        """
        Sends a request to the /execute-command endpoint.
        """
        print(f"\n--- Executing command in '{workdir}': '{command}' ---")
        payload = {
            "workdir": workdir,
            "command": command
        }
        response_dict = self._make_request("execute-command", payload)
        return response_dict['output']

    def revert_patch(self, workdir, patch_content):
        """
        Sends a request to the /revert-patch endpoint.
        """
        print(f"\n--- Attempting to revert patch in '{workdir}' ---")
        payload = {
            "workdir": workdir,
            "patch": patch_content
        }
        response = self._make_request("revert-patch", payload)
        if not response['revert_success']:
            print("warning, patch did not successfully apply.")
        return response['output']

    # --- NEW CLIENT METHOD ---
    def execute_as_script(self, workdir, script_content, entrypoint, command, timeout):
        """
        Sends a request to the /execute-script endpoint.

        Args:
            workdir (str): The working directory on the server.
            script_content (str): The content of the script to execute.
            entrypoint (str): The filename for the script on the server (e.g., "/eval.sh").
            command (str): The command to run the script (e.g., "/bin/bash /eval.sh").
            timeout (int): The timeout in seconds for the command execution.

        Returns:
            tuple: A tuple containing (test_output, timed_out, total_runtime),
                   or (None, False, 0.0) on communication error.
        """
        print(f"\n--- Executing script in '{workdir}' with timeout {timeout}s ---")
        payload = {
            "workdir": workdir,
            "script_content": script_content,
            "entrypoint": entrypoint,
            "command": command,
            "timeout": timeout,
        }

        response_data = self._make_request("execute-script", payload)

        if response_data:
            return (
                response_data.get("output"),
                response_data.get("timed_out", False),
                response_data.get("total_runtime", 0.0)
            )

        # Return default values on request failure
        return None, False, 0.0


def run_instance(test_spec: TestSpec,
                 pred: dict,
                 run_id: str,
                 timeout: int = None):
    # Set up logging directory
    instance_id = test_spec.instance_id
    model_name_or_path = pred.get(KEY_MODEL, "None").replace("/", "__")
    log_dir = RUN_EVALUATION_LOG_DIR / run_id / model_name_or_path / instance_id
    # Set up report file
    report_path = log_dir / LOG_REPORT

    client = SkillsExecutionClient()

    client.apply_patch(
        patch_content=pred[KEY_PREDICTION],
        workdir=DOCKER_WORKDIR,
    )

    git_diff_command = "git -c core.fileMode=false diff"
    git_diff_output_before = client.execute_command(
        command=git_diff_command,
        workdir=DOCKER_WORKDIR
    )
    print(f"Git diff before:\n{git_diff_output_before}")

    test_output, timed_out, total_runtime = client.execute_as_script(
        script_content=test_spec.eval_script,
        entrypoint="/eval.sh",
        command="/bin/bash /eval.sh",
        workdir="/",
        timeout=timeout,
    )
    test_output_path = log_dir / LOG_TEST_OUTPUT
    print(f"Test runtime: {total_runtime:_.2f} seconds")

    Path(test_output_path).parent.mkdir(parents=True, exist_ok=True)
    with open(test_output_path, "w") as f:
        f.write(test_output)
        print(f"Test output for {instance_id} written to {test_output_path}")
        if timed_out:
            f.write(f"\n\nTimeout error: {timeout} seconds exceeded.")
            print(
                instance_id,
                f"Test timed out after {timeout} seconds.",
            )
            return

    git_diff_output_after = client.execute_command(
        command=git_diff_command,
        workdir=DOCKER_WORKDIR
    )
    print(f"Git diff after:\n{git_diff_output_after}")
    if git_diff_output_after != git_diff_output_before:
        print("Git diff changed after running eval script")

    print(f"Grading answer for {instance_id}...")
    report = get_eval_report(
        test_spec=test_spec,
        prediction=pred,
        log_path=test_output_path,
        include_tests_status=True,
    )
    print(
        f"report: {report}\n"
        f"Result for {instance_id}: resolved: {report[instance_id]['resolved']}"
    )

    # Write report to report.json
    with open(report_path, "w") as f:
        f.write(json.dumps(report, indent=4))
    return instance_id, report
