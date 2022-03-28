from typing import List, Dict
from mcdreforged.api.utils.serializer import Serializable


class Configure(Serializable):
    turn_off_auto_save: bool = True
    ignored_files: List[str] = [
        "session.lock"
    ]
    saved_world_keywords: List[str] = [
        "Saved the game",  # 1.13+
        "Saved the world",  # 1.12-
    ]
    mirror_path: str = "./mirror"
    server_path: str = "./server"
    overwrite_backup_folder: str = "overwrite"
    world_names: List[str] = [
        "world"
    ]

    # 0:guest 1:user 2:helper 3:admin 4:owner
    minimum_permission_level: Dict[str, int] = {
        "sync": 2,
        "confirm": 1,
        "abort": 1,
        "reload": 2,
        "status": 0,
    }

    def is_file_ignored(self, file_name: str) -> bool:
        for item in self.ignored_files:
            if len(item) > 0:
                if item[0] == "*" and file_name.endswith(item[1:]):
                    return True
                if item[-1] == "*" and file_name.startswith(item[:-1]):
                    return True
                if file_name == item:
                    return True
        return False
