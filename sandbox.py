import asyncio
import resource

ALLOWLIST = {
    "sandbox_test": [
        "python", "-c",
        "import time; print('TAES sandbox OK'); time.sleep(0.1)"
    ]
}

class Sandbox:
    def __init__(self):
        self.timeout = 5
        self.max_output = 4000

    def status(self):
        return {
            "mode": "allowlisted-process",
            "arbitrary_code": False,
            "timeout_seconds": self.timeout,
            "max_output": self.max_output
        }

    async def run(self, action, arguments=None):
        command = ALLOWLIST.get(action)
        if not command:
            return {
                "status": "blocked",
                "reason": "action_not_allowlisted"
            }

        def limits():
            resource.setrlimit(resource.RLIMIT_CPU, (1, 1))
            resource.setrlimit(
                resource.RLIMIT_FSIZE,
                (1024 * 1024, 1024 * 1024)
            )
            resource.setrlimit(resource.RLIMIT_NOFILE, (32, 32))

        try:
            process = await asyncio.create_subprocess_exec(
                *command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                preexec_fn=limits
            )

            stdout, stderr = await asyncio.wait_for(
                process.communicate(),
                timeout=self.timeout
            )

            return {
                "status": "completed"
                if process.returncode == 0 else "failed",
                "returncode": process.returncode,
                "stdout": stdout.decode(errors="replace")[:self.max_output],
                "stderr": stderr.decode(errors="replace")[:self.max_output]
            }

        except asyncio.TimeoutError:
            try:
                process.kill()
                await process.wait()
            except Exception:
                pass
            return {"status": "killed", "reason": "timeout"}
        except Exception as exc:
            return {"status": "error", "error": type(exc).__name__}
