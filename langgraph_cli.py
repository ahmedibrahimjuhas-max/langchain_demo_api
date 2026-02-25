#!/usr/bin/env python3
import argparse
import os


def run_explicit(question: str) -> str:
    from langgraph_explicit_fastapi.core import graph

    result = graph.invoke(
        {
            "user_input": question,
            "intent": "joke",
            "city": None,
            "topic": None,
            "final_answer": None,
        }
    )
    return str(result.get("final_answer") or "No answer generated.")


def run_react(question: str) -> str:
    from langgraph_react_fastapi.core import graph

    result = graph.invoke({"messages": [{"role": "user", "content": question}]})

    for message in reversed(result["messages"]):
        if message.get("role") == "assistant" and message.get("content"):
            text = str(message["content"]).strip()
            if text:
                return text
    return "No answer generated."


def run_once(mode: str, question: str) -> None:
    if mode in {"explicit", "both"}:
        print("\n[Explicit]")
        print(run_explicit(question))
    if mode in {"react", "both"}:
        print("\n[ReAct]")
        print(run_react(question))


def interactive_loop(mode: str) -> None:
    print("LangGraph CLI ready. Type 'exit' to quit.")
    while True:
        question = input("You: ").strip()
        if question.lower() in {"exit", "quit"}:
            break
        if not question:
            continue
        run_once(mode, question)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run LangGraph explicit/react flows from terminal."
    )
    parser.add_argument(
        "--mode",
        choices=["explicit", "react", "both"],
        default="both",
        help="Which graph mode to run.",
    )
    parser.add_argument(
        "--question",
        type=str,
        default=None,
        help="Single question input. If omitted, starts interactive mode.",
    )
    parser.add_argument(
        "--env-file",
        type=str,
        default=None,
        help="Absolute path to .env file. Sets ENV_FILE before app import.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    if args.env_file:
        os.environ["ENV_FILE"] = args.env_file

    if args.question:
        run_once(args.mode, args.question.strip())
        return

    interactive_loop(args.mode)


if __name__ == "__main__":
    main()
