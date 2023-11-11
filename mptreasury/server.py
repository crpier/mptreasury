import asyncio
import json
from pathlib import Path

from loguru import logger

import mptreasury.services.import_service
from mptreasury.core.bootstrap import bootstrap

SOCKET_PATH = "/tmp/my_socket"


def parse_request(request: str) -> dict | None:
    try:
        request_body = json.loads(request)
    except json.JSONDecodeError as e:
        logger.info("Failed to parse request '{}': {}", request, e)
        return None
    return request_body


async def handle_client(reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
    try:
        request: str | None = None
        while request != "quit":
            # TODO: handle messages larger than 255 bytes
            request = (await reader.read(255)).decode("utf8")
            if reader.at_eof():
                logger.info("bye client")
                break
            if not (request_body := parse_request(request)):
                continue
            match request_body["name"]:
                case "import_folder":
                    mptreasury.services.import_service.import_folder(
                        Path(request_body["music_path"])
                    )
            response = "some response"
            writer.write(response.encode("utf8"))
            await writer.drain()
    except Exception as e:
        logger.info("Something wonky happened: {}", e)
    finally:
        writer.close()


async def run_server():
    bootstrap()
    server = await asyncio.start_unix_server(handle_client, SOCKET_PATH)
    async with server:
        await server.serve_forever()


asyncio.run(run_server())
