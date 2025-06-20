import os
import subprocess
import tempfile
import time
import stat
from flask import Flask, jsonify, request

# Initialize Flask App
app = Flask(__name__)

# --- Configuration ---
# List of commands to attempt for applying a patch
GIT_APPLY_CMDS = [
    "git apply --verbose",
    "git apply --verbose --reject",
    "patch --batch --fuzz=5 -p1 -i",
]


# --- Helper Functions ---

def execute_command_logic(command, workdir):
    """
    Executes a shell command and captures its output.
    """
    try:
        process = subprocess.run(
            command,
            shell=True,
            cwd=workdir,
            capture_output=True,
            text=True,
            check=False
        )
        return process.returncode, process.stdout, process.stderr
    except Exception as e:
        return -1, "", str(e)


# --- Flask Routes ---

@app.route("/apply-patch", methods=["POST"])
def apply_patch():
    """
    Applies a git patch to a specified working directory.
    """
    data = request.get_json()
    if not data or "patch" not in data or "workdir" not in data:
        return jsonify({"error": "Missing 'patch' or 'workdir' in JSON payload"}), 400

    patch_content = data["patch"]
    workdir = data["workdir"]

    if not os.path.isdir(workdir):
        return jsonify({"error": f"Working directory not found: {workdir}"}), 400

    with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".patch", dir=workdir) as patch_file:
        patch_file.write(patch_content)
        patch_filename = patch_file.name

    applied_patch = False
    stdout, stderr = "", ""
    try:
        for cmd_template in GIT_APPLY_CMDS:
            full_cmd = f"{cmd_template} {os.path.basename(patch_filename)}"
            exit_code, out, err = execute_command_logic(full_cmd, workdir)
            stdout, stderr = out, err

            if exit_code == 0:
                applied_patch = True
                break

        if applied_patch:
            return jsonify({
                "patch_success": True,
                "message": "Patch applied successfully",
                "output": stdout
            })
        else:
            return jsonify({
                "patch_success": False,
                "message": "Failed to apply patch",
                "error": stderr
            }), 500
    finally:
        if os.path.exists(patch_filename):
            os.remove(patch_filename)


@app.route("/execute-command", methods=["POST"])
def execute_command_route():
    """
    Executes a shell command in a specified working directory.
    """
    data = request.get_json()
    if not data or "command" not in data or "workdir" not in data:
        return jsonify({"error": "Missing 'command' or 'workdir' in request"}), 400

    command = data["command"]
    workdir = data["workdir"]

    if not os.path.isdir(workdir):
        return jsonify({"error": f"Working directory not found: {workdir}"}), 400

    exit_code, stdout, stderr = execute_command_logic(command, workdir)

    return jsonify({
        "exit_code": exit_code,
        "output": stdout + stderr,
    })


@app.route("/revert-patch", methods=["POST"])
def revert_patch():
    """
    Reverts the last applied patch in a given directory.
    """
    data = request.get_json()
    if not data or "patch" not in data or "workdir" not in data:
        return jsonify({"error": "Missing 'patch' or 'workdir' in request"}), 400

    patch_content = data["patch"]
    workdir = data["workdir"]

    if not os.path.isdir(workdir):
        return jsonify({"error": f"Working directory not found: {workdir}"}), 400

    with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".patch", dir=workdir) as patch_file:
        patch_file.write(patch_content)
        patch_filename = patch_file.name

    try:
        git_revert_command = f"git apply --reverse {os.path.basename(patch_filename)}"
        patch_revert_command = f"patch --batch -p1 -R -i {os.path.basename(patch_filename)}"
        exit_code, stdout, stderr = execute_command_logic(git_revert_command, workdir)
        if exit_code != 0:
            exit_code, stdout, stderr = execute_command_logic(patch_revert_command, workdir)
        remove_agentless_intermediate_files = f"rm -f {workdir}/reproduce_bug.py {workdir}/this_is_invisible.py {workdir}/this_is_invisible_2.py"
        execute_command_logic(remove_agentless_intermediate_files, workdir)
        if exit_code == 0:
            return jsonify({"revert_success": True, "message": "Patch reverted successfully", "output": stdout})
        else:
            return jsonify({"revert_success": False, "message": "Failed to revert patch", "error": stderr}), 500
    finally:
        if os.path.exists(patch_filename):
            os.remove(patch_filename)


@app.route("/execute-script", methods=["POST"])
def execute_script():
    """
    Creates a script file, executes it with a timeout, and returns the result.
    """
    data = request.get_json()
    required_fields = ["workdir", "script_content", "entrypoint", "command", "timeout"]
    if not data or not all(field in data for field in required_fields):
        return jsonify({"error": f"Missing one or more required fields: {required_fields}"}), 400

    workdir = data["workdir"]
    script_content = data["script_content"]
    entrypoint = data["entrypoint"]  # e.g., "/eval.sh"
    command = data["command"]  # e.g., "/bin/bash /eval.sh"
    timeout = data["timeout"]

    if not os.path.isdir(workdir):
        return jsonify({"error": f"Working directory not found: {workdir}"}), 400

    # Securely join path and prevent directory traversal
    script_filename = os.path.basename(entrypoint.strip('/'))
    script_path = os.path.join(workdir, script_filename)

    try:
        # Write the script content to the file
        with open(script_path, "w") as f:
            f.write(script_content)

        # Make the script executable (e.g., chmod 755)
        st = os.stat(script_path)
        os.chmod(script_path, st.st_mode | stat.S_IEXEC)

        start_time = time.time()
        timed_out = False
        stdout, stderr = "", ""
        exit_code = -1

        try:
            process = subprocess.run(
                command,
                shell=True,
                cwd=workdir,
                capture_output=True,
                text=True,
                timeout=timeout
            )
            exit_code = process.returncode
            stdout = process.stdout
            stderr = process.stderr
        except subprocess.TimeoutExpired as e:
            timed_out = True
            stdout = e.stdout if e.stdout else ""
            stderr = e.stderr if e.stderr else "Command timed out."
        except Exception as e:
            stderr = f"An unexpected error occurred: {str(e)}"

        total_runtime = time.time() - start_time

        return jsonify({
            "exit_code": exit_code,
            "output": stdout + stderr,
            "timed_out": timed_out,
            "total_runtime": total_runtime
        })

    finally:
        # Ensure the script is removed after execution
        if os.path.exists(script_path):
            os.remove(script_path)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=6005, debug=True)