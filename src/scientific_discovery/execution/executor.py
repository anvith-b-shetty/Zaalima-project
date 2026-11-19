
"""
Docker-based Code Execution Engine.

Executes validated Python code inside a restricted
Docker container and returns structured results.
"""

import subprocess
import threading
import time
import uuid

from .config import (
    DOCKER_IMAGE,
    DOCKER_NETWORK_MODE,
    DOCKER_MEMORY_LIMIT,
    DOCKER_CPU_LIMIT,
    DOCKER_PIDS_LIMIT,
    DOCKER_READ_ONLY,
    DOCKER_TMPFS_SIZE,
    MAX_OUTPUT_SIZE_BYTES,
)

from .model import ExecutionRequest, ExecutionResponse


class CodeExecutor:
    """Execute Python code inside an isolated Docker container."""

    def __init__(self, image: str = DOCKER_IMAGE):
        self.image = image

    def _stop_container(self, container_name: str) -> None:
        """Stop a running container."""
        try:
            subprocess.run(
                ["docker", "kill", container_name],
                capture_output=True,
                timeout=5,
                check=False,
            )
        except (subprocess.TimeoutExpired, OSError):
            pass

    def _remove_container(self, container_name: str) -> None:
        """Remove the container after execution."""
        try:
            subprocess.run(
                ["docker", "rm", "-f", container_name],
                capture_output=True,
                timeout=5,
                check=False,
            )
        except (subprocess.TimeoutExpired, OSError):
            pass

    def execute(
        self, request: ExecutionRequest
    ) -> ExecutionResponse:
        """Execute validated Python code and return its result."""

        container_name = f"scientific-exec-{uuid.uuid4().hex[:12]}"
        started_at = time.perf_counter()

        command = [
            "docker", "run",
            "--interactive",
            "--name", container_name,
            "--network", DOCKER_NETWORK_MODE,
            "--memory", DOCKER_MEMORY_LIMIT,
            "--memory-swap", DOCKER_MEMORY_LIMIT,
            "--cpus", DOCKER_CPU_LIMIT,
            "--pids-limit", str(DOCKER_PIDS_LIMIT),
            "--cap-drop", "ALL",
            "--security-opt", "no-new-privileges:true",
            "--user", "1000:1000",
            "--workdir", "/tmp",
            "--tmpfs",
            f"/tmp:rw,noexec,nosuid,nodev,size={DOCKER_TMPFS_SIZE},mode=1777",
            "--env", "PYTHONDONTWRITEBYTECODE=1",
        ]

        if DOCKER_READ_ONLY:
            command.append("--read-only")

        command.extend([
            self.image,
            "python", "-I", "-B", "-"
        ])

        try:
            process = subprocess.Popen(
                command,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                bufsize=0,
            )

        except FileNotFoundError:
            return ExecutionResponse(
                status="error",
                stderr="Docker CLI was not found on this system.",
            )

        except OSError as exc:
            return ExecutionResponse(
                status="error",
                stderr=f"Could not start Docker: {exc}",
            )

        buffers = {
            "stdout": bytearray(),
            "stderr": bytearray(),
        }

        total_output = 0
        output_lock = threading.Lock()
        output_limit_reached = threading.Event()
        kill_started = threading.Event()
        execution_timed_out = False

        def stop_once():
            """Stop the container only once."""
            if not kill_started.is_set():
                kill_started.set()
                self._stop_container(container_name)

        def read_stream(stream, key):
            """Read output without storing unlimited data."""
            nonlocal total_output

            while True:
                chunk = stream.read(4096)

                if not chunk:
                    break

                should_stop = False

                with output_lock:
                    remaining = MAX_OUTPUT_SIZE_BYTES - total_output
                    keep_size = min(len(chunk), max(remaining, 0))

                    if keep_size:
                        buffers[key].extend(chunk[:keep_size])
                        total_output += keep_size

                    if len(chunk) > keep_size:
                        output_limit_reached.set()
                        should_stop = True

                if should_stop:
                    stop_once()

        stdout_thread = threading.Thread(
            target=read_stream,
            args=(process.stdout, "stdout"),
            daemon=True,
        )

        stderr_thread = threading.Thread(
            target=read_stream,
            args=(process.stderr, "stderr"),
            daemon=True,
        )

        stdout_thread.start()
        stderr_thread.start()

        try:
            # Send code through standard input, not a shell command.
            process.stdin.write(request.code.encode("utf-8"))
            process.stdin.close()

        except (BrokenPipeError, OSError):
            pass

        try:
            process.wait(timeout=request.timeout_seconds)

        except subprocess.TimeoutExpired:
            execution_timed_out = True
            stop_once()

            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait()

        finally:
            if process.stdin and not process.stdin.closed:
                process.stdin.close()

            stdout_thread.join(timeout=5)
            stderr_thread.join(timeout=5)

            self._remove_container(container_name)

        execution_time_ms = int(
            (time.perf_counter() - started_at) * 1000
        )

        stdout = bytes(buffers["stdout"]).decode(
            "utf-8", errors="replace"
        )

        stderr = bytes(buffers["stderr"]).decode(
            "utf-8", errors="replace"
        )

        if execution_timed_out:
            status = "timeout"
            stderr += "\nExecution time limit exceeded."

        elif output_limit_reached.is_set():
            status = "error"
            stderr += "\nMaximum output size exceeded."

        elif process.returncode == 0:
            status = "success"

        else:
            status = "error"

        return ExecutionResponse(
            status=status,
            stdout=stdout,
            stderr=stderr,
            exit_code=process.returncode,
            execution_time_ms=execution_time_ms,
            truncated_output=output_limit_reached.is_set(),
        )
