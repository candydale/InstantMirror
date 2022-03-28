import os
import shutil
from sys import prefix
from typing import Any
from distutils.command.config import config
from mcdreforged.api.all import *
from instant_mirror.config import Configure

config: Configure
server_inst: PluginServerInterface
HelpMessage: RTextBase

PREFIX = "!!mirror"
CONFIG_FILE = os.path.join("config", "InstantMirror.json")


def text(text_key: str, *args) -> RTextMCDRTranslation:
    return ServerInterface.get_instance().rtr(f"instant_mirror.{text_key}", *args)


def print_message(source: CommandSource, msg, tell=True, prefix="§b[Mirror] "):
    msg = RTextList(prefix, msg)
    if source.is_player and not tell:
        source.get_server().say(msg)
    else:
        source.reply(msg)


def command_run(message: Any, text: Any, command: str) -> RTextBase:
    fancy_text = message.copy() if isinstance(
        message, RTextBase) else RText(message)
    return fancy_text.set_hover_text(text).set_click_event(RAction.run_command, command)


@new_thread("Mirror - sync")
def mirror_sync(source):
    for world in config.world_names:
        mirror_world_path = os.path.join(config.mirror_path, world)
        server_world_path = os.path.join(config.server_path, world)
        if os.path.exists(mirror_world_path):
            shutil.rmtree(mirror_world_path)
        shutil.copytree(server_world_path, mirror_world_path, ignore=lambda path, files: set(
            filter(config.is_file_ignored, files)))
    print_message(source, "§6同步完成", tell=False)


def show_help(source):
    print_message(source, text("show_help"))


def on_load(server, prev):
    global server_inst
    server_inst = server
    global config
    config = server_inst.load_config_simple(
        CONFIG_FILE, target_class=Configure, in_data_folder=False, source_to_reply=CommandSource)
    server.register_help_message("!!mirror", text("show_help"))
    server.register_command(Literal("!!mirror").runs(show_help)
                            .then(Literal("sync").runs(mirror_sync))
                            )
