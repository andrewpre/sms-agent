import argparse
from agents.orchestrator import run_orchestrator
import asyncio

async def f():
    """
    Your agent logic goes here.
    """
    print(f"Starting agent")

    user_input = input("You: ")

    response = await run_orchestrator("13479252439", user_input, True)


async def main():

    await f()


if __name__ == "__main__":
    asyncio.run(main())