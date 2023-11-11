import asyncio
import json

SOCKET_PATH = "/tmp/my_socket"


async def run_client():
    reader: asyncio.StreamReader
    writer: asyncio.StreamWriter
    reader, writer = await asyncio.open_unix_connection(SOCKET_PATH)
    writer.write(
        json.dumps(
            {
                "name": "import_folder",
                "music_path": "~/Downloads/torr/Metamorfosi - Inferno/",
            }
        ).encode("utf8")
    )
    resp = await reader.read(1024)
    print(resp)
    writer.write_eof()


asyncio.run(run_client())
