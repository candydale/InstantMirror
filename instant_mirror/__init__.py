import os
import time
import shutil
from sys import prefix
from typing import Any
from distutils.command.config import config
from mcdreforged.api.all import *
from instant_mirror.config import Configure

config: Configure
server_inst: PluginServerInterface

PREFIX = "!!mirror"
CONFIG_FILE = os.path.join("config", "InstantMirror.json")


def text(text_key: str, *args) -> RTextMCDRTranslation:
    return ServerInterface.get_instance().rtr(f"instant_mirror.{text_key}", *args)


def print_message(source, msg, tell=True, prefix="§b[Mirror]§r "):
    msg = RTextList(prefix, msg)
    if source.is_player and not tell:
        source.get_server().say(msg)
    else:
        source.reply(msg)


@new_thread("InstantMirror - sync")
def mirror_sync(source):
    print_message(source, text("sync.start"), tell=False)
    time_start = time.time()
    try:
        if config.turn_off_auto_save:
            server_inst.execute("save-off")
            server_inst.execute("save-all flush")
        for world in config.world_names:
            mirror_world_path = os.path.join(config.mirror_path, world)
            server_world_path = os.path.join(config.server_path, world)
            if os.path.exists(mirror_world_path):
                shutil.rmtree(mirror_world_path)
            shutil.copytree(server_world_path, mirror_world_path, ignore=lambda path, files: set(
                filter(config.is_file_ignored, files)))
        time_finish = time.time()
        time_used = round(time_finish - time_start, 1)
        print_message(
            source,
            RTextList(
                f"{text('sync.finish')} {text('sync.time_used')} §e{time_used}§r {text('sync.seconds')} ",
                RText(f"[{text('switch_to_mirror')}]", RColor.green)
                .h(text("click_to_switch"))
                .c(RAction.run_command, f"/server {config.mirror_proxy_name}")),
            tell=False)
    except Exception as e:
        server_inst.logger.exception(
            f"[InstantMirror] Error while syncing to mirror: {e}")
        print_message(source, text("sync.fail", e), tell=False)
    finally:
        if config.turn_off_auto_save:
            server_inst.execute("save-on")


def show_help(source):
    print_message(source, text("show_help"))


def unknown_command(source):
    print_message(source, text("unknown_command"))


def register_command(server):
    def get_literal_node(literal):
        lvl = config.minimum_permission_level.get(literal)
        return Literal(literal).requires(lambda src: src.has_permission(lvl)).on_error(RequirementNotMet, lambda src: print_message(src, text("permission_denied")), handled=True)

    server.register_command(
        Literal("!!mirror")
        .runs(show_help)
        .on_error(UnknownArgument, unknown_command, handled=True)

        .then(get_literal_node("sync").runs(mirror_sync))
        .then(get_literal_node('reload').runs(
            lambda src: (
                src.get_server().reload_plugin("instant_mirror"),
                print_message(src, text("reloaded"))))
              ))


def on_load(server, prev):
    global server_inst, config
    server_inst = server
    config = server_inst.load_config_simple(
        CONFIG_FILE, target_class=Configure, in_data_folder=False, source_to_reply=server)
    server.register_help_message("!!mirror", text("show_help"))
    register_command(server)
