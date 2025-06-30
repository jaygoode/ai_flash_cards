import subprocess
import file_handler
from enum import Enum, auto


class TaskType(Enum):
    SETUP = auto()  # Creating folder structure, initializing dependencies, config files
    CODING = auto()  # Writing actual source code, modules, classes, functions
    DOCUMENTATION = auto()  # Writing docs, README, comments, docstrings
    TESTING = auto()  # Writing or configuring tests, test frameworks, CI tests
    INTEGRATION = auto()  # Setting up CI/CD pipelines, workflows, integrations
    DEPLOYMENT = auto()  # Docker containers, deployment scripts, hosting setup
    PLANNING = auto()  # Requirement analysis, design, task breakdown
    MAINTENANCE = auto()  # Bug fixes, refactoring, upgrades
    RESEARCH = auto()  # Prototyping, evaluating technologies/tools
    CONFIGURATION = auto()  # Setting up config files, environment variables
    BUILD = auto()  # Packaging, building releases or distributions
    MONITORING = auto()  # Setting up logging, alerts, performance tracking


config = file_handler.read_yaml_file("config.yaml")


def prompt_ai(system_prompt, model="llama2"):
    print(f"[*] Sending request to Ollama {model} model...")

    result = subprocess.run(
        ["ollama", "run", model, system_prompt],
        capture_output=True,
        text=True,
        encoding="utf-8",
    )

    if result.returncode != 0:
        raise RuntimeError(f"Ollama error:\n{result.stderr}")

    return result.stdout.strip()
