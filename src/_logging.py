import logging
import datetime
import discord
from discord.ext import tasks
import asyncio
import aiohttp

formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')

ZWSP = "\N{ZERO WIDTH SPACE}"


class EmbedWebhookLogger:
    _to_log: list[discord.Embed]

    def __init__(self, webhook_url: str, *, loop: asyncio.BaseEventLoop = None) -> None:
        self.loop = loop or asyncio.get_event_loop()
        self.webhook_url = webhook_url
        self.to_log = []

        self.session = aiohttp.ClientSession()
        self.webhook = discord.Webhook.from_url(
            self.webhook_url, session=self.session)

        # setup loop
        self.loop.start()

    def log(self, embed: discord.Embed) -> None:
        self.to_log.append(embed)

    @tasks.loop(seconds=5)
    async def loop(self) -> None:
        while self.to_log:
            embeds = [self.to_log.pop(0)
                      for _ in range(min(10, len(self.to_log)))]
            await self.webhook.send(embeds=embeds)


def codeblock(text, *, language: str = "") -> str:
    return f"```{language}\n{text}\n```"


class WebhookHandler(logging.Handler):
    _colours = {
        logging.DEBUG: discord.Colour.light_grey(),
        logging.INFO: discord.Colour.gold(),
        logging.WARNING: discord.Colour.orange(),
        logging.ERROR: discord.Colour.red(),
        logging.CRITICAL: discord.Colour.dark_red(),
    }

    def __init__(self, webhook_url: str, level: int = logging.NOTSET) -> None:
        super().__init__(level)
        self.webhook_logger = EmbedWebhookLogger(webhook_url)

    def emit(self, record: logging.LogRecord) -> None:
        self.format(record)

        message = f'{record.message}\n{record.exc_text or ""}'
        message = message[:4000] + "..." if len(message) > 4000 else message

        self.webhook_logger.log(
            discord.Embed(
                colour=self.colours.get(record.levelno, discord.Embed.Empty),
                title=record.name,
                description=codeblock(message, language="py"),
                timestamp=datetime.datetime.fromtimestamp(record.created),
            ).add_field(name=ZWSP, value=f"{record.filename}:{record.lineno}")
        )


def setup_logger(name, log_file, webhook_url, level):
    """To setup as many loggers as you want"""

    stream_handler = logging.StreamHandler()  # this handler will log to stderr
    file_handler = logging.FileHandler(
        filename=log_file, encoding='utf-8', mode='w')
    if webhook_url is not None:
        webhook_handler = WebhookHandler(
            webhook_url=webhook_url, level=logging.WARNING)
        handlers = [stream_handler, file_handler, webhook_handler]
    else:
        handlers = [stream_handler, file_handler]

    logger = logging.getLogger(name)
    logger.setLevel(level)
    for handler in handlers:
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    return logger
