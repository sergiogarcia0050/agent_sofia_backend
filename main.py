# main.py
from livekit.agents import WorkerOptions, cli
from agent.agent import entrypoint  # Cambiado aquí


if __name__ == "__main__":
    cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint))