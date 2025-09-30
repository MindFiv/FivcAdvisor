import asyncio
from typing import Any

import dotenv
from strands.hooks import HookProvider, HookRegistry, BeforeInvocationEvent, AfterInvocationEvent, MessageAddedEvent
from strands.handlers.callback_handler import PrintingCallbackHandler

from fivcadvisor import agents

dotenv.load_dotenv()


class LoggingHook(HookProvider):
    def register_hooks(self, registry: HookRegistry, **kwargs: Any) -> None:
        registry.add_callback(BeforeInvocationEvent, self.log_start)
        registry.add_callback(AfterInvocationEvent, self.log_end)
        registry.add_callback(MessageAddedEvent, self.log_stream)

    def log_start(self, event: BeforeInvocationEvent) -> None:
        print(f"Request started for agent: {event.agent}")

    def log_stream(self, event: MessageAddedEvent) -> None:
        print(f"Message added: {event.message}")

    def log_end(self, event: AfterInvocationEvent) -> None:
        print(f"Request completed for agent: {event.agent}")


def debugger_callback_handler(**kwargs):
    # Print the values in kwargs so that we can see everything
    if 'message' in kwargs:
        print(kwargs)


async def main():
    """
    Run agent example
    """

    print("FivcAdvisor - Generic Agent Example")
    print("\n" + "=" * 50)

    agent = agents.create_companion_agent(callback_handler=debugger_callback_handler)
    # agent.hooks.add_hook(LoggingHook())
    result = agent("What time is it now?")

    # print(f'Result: {str(result)}')


if __name__ == '__main__':
    asyncio.run(main())
