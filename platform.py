# Copyright 2014-present PlatformIO <contact@platformio.org>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
import sys
import subprocess

from platformio.managers.platform import PlatformBase


IS_WINDOWS = sys.platform.startswith("win")

class PyPlatform(PlatformBase):

    def configure_default_packages(self, variables, targets):
        board = variables.get("board")
        board_config = self.board_config(board)
        build_core = variables.get(
            "board_build.core", board_config.get("build.core", "arduino"))
        build_mcu = variables.get("board_build.mcu", board_config.get("build.mcu", ""))

        frameworks = variables.get("pioframework", [])
        if "arduino" in frameworks:
                self.packages["toolchain-gccarmnoneeabi"]["version"] = "~1.120301.0"
                if build_core == "py32":
                    self.packages["framework-arduinopy32"]["optional"] = False
                    self.packages["framework-cmsis"]["version"] = "~2.50900.0"
                    self.packages["framework-cmsis"]["optional"] = False

        # include or exclude other packages for different frameworks.. 

        default_protocol = board_config.get("upload.protocol") or ""



    def get_boards(self, id_=None):
        result = PlatformBase.get_boards(self, id_)
        if not result:
            return result
        if id_:
            return self._add_default_debug_tools(result)
        else:
            for key, value in result.items():
                result[key] = self._add_default_debug_tools(result[key])
        return result

    def _add_default_debug_tools(self, board):
        debug = board.manifest.get("debug", {})
        upload_protocols = board.manifest.get("upload", {}).get(
            "protocols", [])
        if "tools" not in debug:
            debug["tools"] = {}


        # BlackMagic, J-Link, ST-Link
        # for link in ("blackmagic", "jlink", "stlink", "cmsis-dap"):
        for link in ("blackmagic", "jlink", "stlink"):
            if link not in upload_protocols or link in debug["tools"]:
                continue
            if link == "cmsis-dap":
                server_args = ["-s", "$PACKAGE_DIR/openocd/scripts"]
                if debug.get("openocd_board"):
                    server_args.extend([
                        "-f", "board/%s.cfg" % debug.get("openocd_board")
                    ])
                else:
                    assert debug.get("openocd_target"), (
                        "Missed target configuration for %s" % board.id)
                    server_args.extend([
                        "-f", "interface/%s.cfg" % link,
                        "-c", "transport select %s" % (
                            "hla_swd" if link == "stlink" else "swd"),
                        "-f", "target/%s.cfg" % debug.get("openocd_target")
                    ])
                    server_args.extend(debug.get("openocd_extra_args", []))

                debug["tools"][link] = {
                    "server": {
                        "package": "tool-openocd",
                        "executable": "bin/openocd",
                        "arguments": server_args
                    }
                }
            debug["tools"][link]["onboard"] = link in debug.get("onboard_tools", [])
            debug["tools"][link]["default"] = link in debug.get("default_tools", [])

        board.manifest["debug"] = debug
        return board

    def configure_debug_session(self, debug_config):
        if debug_config.speed:
            server_executable = (debug_config.server or {}).get("executable", "").lower()
            if "openocd" in server_executable:
                debug_config.server["arguments"].extend(
                    ["-c", "adapter speed %s" % debug_config.speed]
                )
            elif "jlink" in server_executable:
                debug_config.server["arguments"].extend(
                    ["-speed", debug_config.speed]
                )
