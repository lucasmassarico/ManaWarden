import os.path
from abc import ABC, abstractmethod
import time
from process_manager import ProcessManager, ScreenManager, MouseBlocker
from utils import ConfigManager
from process_manager.hex_codes import keys
from utils import LogManager
from datetime import datetime
import random
import cv2
import numpy as np
import os
from settings import BASE_DIR


class Action(ABC):
    def __init__(self, priority):
        self.priority = priority

        self.config_manager = ConfigManager()
        self.logger = LogManager()
        self.process_manager = ProcessManager()
        self.mouse_blocker = MouseBlocker()

    @abstractmethod
    def execute(self):
        pass


class ImageAction(Action):
    def __init__(self, priority):
        super().__init__(priority)

        self.screen_manager = ScreenManager()

    def validate_template(self, template_path, template_name="template"):
        """Validate if templates exists and log if not found."""
        if not os.path.exists(template_path):
            self.logger.log("error", f"{template_name} template not found: {template_path}")
            return False
        return True

    def capture_screen(self):
        screen = self.screen_manager.capture_screenshot()
        if screen is None:
            self.logger.log("error", "Failed to capture screenshot.")
        return screen

    @abstractmethod
    def execute(self):
        pass


class MoveItemAction(ImageAction):
    def __init__(self, priority=2, instance_n: int=1):
        """

        :type priority: Set priority of action
        """
        super().__init__(priority)

        self.instance_n = instance_n

        self.move_item_path = None
        self.move_item_threshold = None
        self.panels_region = None
        self.map_region = None
        self.destination_region = None
        self.delay = None
        self.steps = None
        self._initialize()

        self.config_manager.add_observer(f"move_item_path_{self.instance_n}", self)
        self.config_manager.add_observer(f"move_item_threshold_{self.instance_n}", self)
        self.config_manager.add_observer(f"panels_region", self)
        self.config_manager.add_observer(f"map_region", self)
        self.config_manager.add_observer(f"destination_region_m_{self.instance_n}", self)
        self.config_manager.add_observer(f"delay_m_{self.instance_n}", self)
        self.config_manager.add_observer(f"steps_m_{self.instance_n}", self)

        self.destination_coords = None

    def _initialize(self):
        """Initialize all configs need to execute action."""

        required_keys = [
            f"move_item_path_{self.instance_n}",
            f"move_item_threshold_{self.instance_n}",
            "panels_region",
            "map_region",
            f"destination_region_m_{self.instance_n}",
            f"delay_m_{self.instance_n}",
            f"steps_m_{self.instance_n}"
        ]

        try:
            self.config_manager.validate_config(required_keys=required_keys)
        except ValueError as e:
            self.logger.log("error", f"Configuration validation failed: {e}")
            raise

        self.move_item_path = self.config_manager.get(key=f"move_item_path_{self.instance_n}", default=None)
        self.move_item_threshold = self.config_manager.get(key=f"move_item_threshold_{self.instance_n}", default=0.8)
        self.panels_region = self.config_manager.get(key="panels_region", default=None)
        self.map_region = self.config_manager.get(key="map_region", default=None)
        self.destination_region = self.config_manager.get(key=f"destination_region_m_{self.instance_n}", default=None)
        self.delay = self.config_manager.get(key=f"delay_m_{self.instance_n}", default=0.08)
        self.steps = self.config_manager.get(key=f"steps_m_{self.instance_n}", default=30)

    def on_config_update(self, key, value):
        """React in config update"""
        if key == f"move_item_path_{self.instance_n}":
            self.move_item_path = value
            self.logger.log("info", f"Updated move_item_path_{self.instance_n} to value {value}")
        elif key == f"move_item_threshold_{self.instance_n}":
            self.move_item_threshold = value
            self.logger.log("info", f"Updated move_item_threshold_{self.instance_n} to value {value}")
        elif key == f"panels_region":
            self.panels_region = value
            self.logger.log("info", f"Updated panels_region to value {value}")
        elif key == f"map_region":
            self.map_region = value
            self.logger.log("info", f"Updated map_region to value {value}")
        elif key == f"destination_region_{self.instance_n}":
            self.destination_region = value
            self.logger.log("info", f"Updated destination_region_m_{self.instance_n} to value {value}")
        elif key == f"delay_m_{self.instance_n}":
            self.delay = value
            self.logger.log("info", f"Updated delay_m_{self.instance_n} to value {value}")
        elif key == f"steps_m_{self.instance_n}":
            self.steps = value
            self.logger.log("info", f"Updated steps_m_{self.instance_n} to value {value}")

    def validate_resources(self):
        if not self.validate_template(template_path=self.move_item_path, template_name=f"Move item path {self.instance_n}"):
            return False
        if not self.destination_region:
            return False
        return True

    def find_item(self, screen):
        self.logger.log("info", f"Searching for the move_item_{self.instance_n}")

        dest_x, dest_y, dest_width, dest_height = self.destination_region
        destination_rect = (dest_x, dest_y, dest_x + dest_width, dest_y + dest_height)

        for region in self.panels_region:
            x, y, width, height = region
            cropped_screen = screen[y:y+height, x:x+width]
            items_positions_in_region = self.screen_manager.find_image(
                main_image=cropped_screen,
                template=self.move_item_path,
                threshold=self.move_item_threshold,
                all_matches=True,
                variation=5
            )
            if items_positions_in_region:
                for item_position in items_positions_in_region:
                    item_x, item_y = item_position[0] + x, item_position[1] + y

                    if dest_x <= item_x <= dest_x + dest_width and dest_y <= item_y <= dest_y + dest_height:
                        continue

                    return item_x, item_y
        self.logger.log("error", f"move_item_{self.instance_n} not found")
        return None

    def perform_move(self, move_item_position):
        start_x, start_y = move_item_position
        dest_x, dest_y, dest_width, dest_height = self.destination_region

        self.logger.log("info", f"Clicking in item to move at position {move_item_position}")

        if self.process_manager.is_foreground() or self.process_manager.is_mouse_over_window():
            self.logger.log("info", f"Window in the foreground or mouse over window. Blocking user mouse input")
            self.mouse_blocker.start_blocking()

        if self.mouse_blocker.blocking:
            time.sleep(self.delay)
        self.logger.log("info", f"Moving item to {dest_x, dest_y}")
        self.process_manager.moveTo(start_x, start_y)
        if self.mouse_blocker.blocking:
            time.sleep(self.delay)
        self.process_manager.perform_drag_and_drop(start_x=start_x, start_y=start_y, dest_x=dest_x, dest_y=dest_y, steps=self.steps)

        if self.mouse_blocker.blocking:
            self.mouse_blocker.stop_blocking()
            self.logger.log("info", f"Ended action. Unblocking mouse input.")

        self.logger.log("info", f"Move_item_{self.instance_n} action completed.")

    def execute(self):
        if not self.validate_resources():
            return

        screen = self.capture_screen()
        if screen is None:
            return

        move_item_position = self.find_item(screen=screen)
        if not move_item_position:
            return

        self.perform_move(move_item_position)


class CastSpellAction(Action):
    def __init__(self, priority=3, instance_n: int=1):
        """
        :param priority: Set priority of action
        """
        super().__init__(priority)

        self.instance_n = instance_n

        self.hotkey_to_cast = None
        self.scan_code = None
        self._initialize()

    def _initialize(self):
        """Initialize all configs need to execute action"""

        required_keys = [
            f"hotkey_to_cast_{self.instance_n}",
        ]

        try:
            self.config_manager.validate_config(required_keys=required_keys)
        except ValueError as e:
            self.logger.log("error", f"Configuration validation failed: {e}")
            raise

        self.hotkey_to_cast = self.config_manager.get(key=f"hotkey_to_cast_{self.instance_n}", default=None)
        self.get_scan_code(self.hotkey_to_cast)

    def get_scan_code(self, key: str):
        if key in keys:
            self.scan_code = keys[key]

    def on_config_update(self, key, value):
        """React in config update"""
        if key == f"hotkey_to_cast_{self.instance_n}":
            self.hotkey_to_cast = value
            self.get_scan_code(self.hotkey_to_cast)
            self.logger.log("info", f"updated hotkey_to_cast_{self.instance_n} to {value}")

    def execute(self):
        if not self.hotkey_to_cast:
            self.logger.log("error", "Need hotkey defined to cast spell.")
            return

        self.process_manager.send_key_to_window(scan_code=self.scan_code)
        self.logger.log("info", "Attempt to cast spell made.")


class FishAction(ImageAction):
    def __init__(self, priority=5):
        """
        :param priority: The priority of action
        """
        super().__init__(priority)

        self.fishing_rod_path = None
        self.water_path = None
        self.panels_region = None
        self.map_region = None
        self.fishing_rod_threshold = None
        self.water_threshold = None
        self._initialize()

        self.config_manager.add_observer("fishing_rod_path", self)
        self.config_manager.add_observer("water_path", self)
        self.config_manager.add_observer("panels_region", self)
        self.config_manager.add_observer("map_region", self)
        self.config_manager.add_observer("fishing_rod_threshold", self)
        self.config_manager.add_observer("water_threshold", self)

    def _initialize(self):
        """Initialize all configs needs to execute action."""

        required_keys = [
            "fishing_rod_path",
            "water_path",
            "panels_region",
            "map_region",
            "fishing_rod_threshold",
            "water_threshold",
        ]

        try:
            self.config_manager.validate_config(required_keys=required_keys)
        except ValueError as e:
            self.logger.log("error", f"Configuration validation failed: {e}")
            raise

        self.fishing_rod_path = self.config_manager.get(key="fishing_rod_path", default=os.path.join(BASE_DIR, "assets", "templates", "fishing_rod.png"))
        self.water_path = self.config_manager.get(key="water_path", default=os.path.join(BASE_DIR, "assets", "templates", "water.png"))
        self.panels_region = self.config_manager.get(key="panels_region", default=None)
        self.map_region = self.config_manager.get(key="map_region", default=None)
        self.fishing_rod_threshold = self.config_manager.get(key="fishing_rod_threshold", default=0.5)
        self.water_threshold = self.config_manager.get(key="water_threshold", default=0.8)

    def on_config_update(self, key, value):
        """React in config update"""
        if key == "fishing_rod_threshold":
            self.fishing_rod_threshold = value
            self.logger.log("info", f"Updated fishing_rod_threshold to {value}")
        elif key == "water_threshold":
            self.water_threshold = value
            self.logger.log("info", f"Updated water_threshold to {value}")
        elif key == "panels_region":
            self.panels_region = value
            self.logger.log("info", f"Updated panels_region to {value}")
        elif key == "map_region":
            self.map_region = value
            self.logger.log("info", f"Updated map_region to {value}")
        elif key == "fishing_rod_path":
            self.fishing_rod_path = value
            self.logger.log("info", f"Updated fishing_rod_path to {value}")
        elif key == "water_path":
            self.water_path = value
            self.logger.log("info", f"Updated water_path to {value}")

    def validate_resources(self):
        if not self.validate_template(template_path=self.fishing_rod_path, template_name="Fishing rod"):
            return False
        if not self.validate_template(template_path=self.water_path, template_name="Water sprite"):
            return False
        return True

    def find_fishing_rod(self, screen):
        self.logger.log("info", "Searching for the fishing rod...")
        for region in self.panels_region:
            x, y, width, height = region
            cropped_screen = screen[y:y+height, x:x+width]
            rod_position_in_region = self.screen_manager.find_image(
                main_image=cropped_screen,
                template=self.fishing_rod_path,
                threshold=self.fishing_rod_threshold
            )
            if rod_position_in_region:
                return rod_position_in_region[0] + x, rod_position_in_region[1] + y
        self.logger.log("error", "Fishing rod not found.")
        return None

    def find_water_positions(self, screen):
        self.logger.log("info", "Searching for water regions...")
        water_positions = []
        for region in self.map_region:
            cropped_screen = self.screen_manager.capture_screenshot(region=region)
            matches = self.screen_manager.find_image(
                main_image=cropped_screen,
                template=self.water_path,
                threshold=self.water_threshold,
                all_matches=True
            )
            if matches:
                water_positions.extend(
                    (pos[0] + region[0], pos[1] + region[1]) for pos in matches
                )
        if not water_positions:
            self.logger.log("error", "No water regions found.")
        return water_positions

    def perform_fishing(self, rod_position, water_positions):
        self.logger.log("info", f"Right-clicking on fishing rod at {rod_position}")

        if self.process_manager.is_foreground() or self.process_manager.is_mouse_over_window():
            if not self.process_manager.medivia:
                self.logger.log("info", f"Window in the foreground or mouse over window. Blocking user mouse input.")
                self.mouse_blocker.start_blocking()
            else:
                try:
                    self.mouse_blocker.blocking_medivia()
                except Exception as e:
                    pass

        if self.mouse_blocker.blocking:
            time.sleep(0.05)
        self.process_manager.moveTo(*rod_position)
        if self.mouse_blocker.blocking:
            time.sleep(0.05)
        self.process_manager.click(*rod_position, button="right")

        selected_water = random.choice(water_positions)
        self.logger.log("info", f"Left-clicking on water region at {selected_water}.")
        if self.mouse_blocker.blocking:
            time.sleep(0.05)
        self.process_manager.moveTo(*selected_water)
        if self.mouse_blocker.blocking:
            time.sleep(0.05)
        self.process_manager.click(*selected_water, button="left")

        if self.mouse_blocker.blocking:
            if self.process_manager.medivia:
                self.mouse_blocker.unblocking_medivia()
            else:
                self.mouse_blocker.stop_blocking()
                self.logger.log("info", f"Ended action. Unblocking user mouse input.")

        self.logger.log("info", "Fishing action completed.")

    def execute(self):
        if not self.validate_resources():
            return

        screen = self.capture_screen()
        if screen is None:
            return

        fishing_rod_position = self.find_fishing_rod(screen)
        if not fishing_rod_position:
            return

        water_positions = self.find_water_positions(screen)
        if not water_positions:
            return

        self.perform_fishing(fishing_rod_position, water_positions)


class UseItemAction(ImageAction):
    def __init__(self, priority=5, instance_n: int = 1):
        super().__init__(priority)

        self.instance_n = instance_n

        self.use_item = None
        self.item_path = None
        self.item_threshold = None
        self.panels_region = None
        self.map_region = None
        self.destination_region = None
        self.delay = None
        self._initialize()

        self.config_manager.add_observer(f"use_item_{self.instance_n}", self)
        self.config_manager.add_observer(f"item_path_{self.instance_n}", self)
        self.config_manager.add_observer(f"item_threshold_{self.instance_n}", self)
        self.config_manager.add_observer("panels_region", self)
        self.config_manager.add_observer("map_region", self)
        self.config_manager.add_observer(f"destination_region_{self.instance_n}", self)
        self.config_manager.add_observer(f"delay_{self.instance_n}", self)

    def _initialize(self):
        """Initialize all configs need to execute action."""

        required_keys = [
            f"use_item_{self.instance_n}",
            f"item_path_{self.instance_n}",
            "panels_region",
            "map_region",
            f"destination_region_{self.instance_n}",
            f"delay_{self.instance_n}"
        ]

        try:
            self.config_manager.validate_config(required_keys=required_keys)
        except ValueError as e:
            self.logger.log("error", f"Configuration validation failed: {e}")
            raise

        self.use_item = self.config_manager.get(key=f"use_item_{self.instance_n}", default=0)
        self.item_path = self.config_manager.get(key=f"item_path_{self.instance_n}", default=None)
        self.item_threshold = self.config_manager.get(key=f"item_threshold_{self.instance_n}", default=0.8)
        self.panels_region = self.config_manager.get(key="panels_region", default=None)
        self.map_region = self.config_manager.get(key="map_region", default=None)
        self.destination_region = self.config_manager.get(key=f"destination_region_{self.instance_n}", default=None)
        self.delay = self.config_manager.get(key=f"delay_{self.instance_n}", default=0.08)

    def on_config_update(self, key, value):
        """React in config update"""
        if key == f"item_path_{self.instance_n}":
            self.item_path = value
            self.logger.log("info", f"Updated item_path_{self.instance_n} to {value}")
        elif key == f"item_threshold_{self.instance_n}":
            self.item_threshold = value
            self.logger.log("info", f"Updated item_threshold_{self.instance_n} to {value}")
        elif key == "panels_region":
            self.panels_region = value
            self.logger.log("info", f"Updated panels_region to {value}")
        elif key == "map_region":
            self.map_region = value
            self.logger.log("info", f"Updated map_region to {value}")
        elif key == f"destination_region_{self.instance_n}":
            self.destination_region = value
            self.logger.log("info", f"Updated destination_region_{self.instance_n} to {value}")
        elif key == f"use_item_{self.instance_n}":
            self.use_item = value
            self.logger.log("info", f"Updated use_item_{self.instance_n} to {value}")
        elif key == f"delay_{self.instance_n}":
            self.delay = value
            self.logger.log("info", f"Updated delay_{self.instance_n} to {value}")

    def validate_resources(self):
        if not self.validate_template(template_path=self.item_path, template_name=f"Item path {self.instance_n}"):
            return False
        return True

    def find_item(self, screen):
        self.logger.log("info", f"Searching for the item_{self.instance_n}")
        for region in self.panels_region:
            x, y, width, height = region
            cropped_screen = screen[y:y+height, x:x+width]
            item_position_in_region = self.screen_manager.find_image(
                main_image=cropped_screen,
                template=self.item_path,
                threshold=self.item_threshold
            )
            if item_position_in_region:
                return item_position_in_region[0] + x, item_position_in_region[1] + y
        self.logger.log("error", f"item_{self.instance_n} not found")
        return None

    def perform_movement(self, item_position):
        dest_x, dest_y = 0, 0
        if self.destination_region:
            dest_x, dest_y, dest_width, dest_height = self.destination_region

        self.logger.log("info", f"Clicking in item at position {item_position}")

        if self.process_manager.is_foreground() or self.process_manager.is_mouse_over_window():
            if not self.process_manager.medivia:
                self.logger.log("info", f"Window in the foreground or mouse over window. Blocking user mouse input.")
                self.mouse_blocker.start_blocking()
            else:
                try:
                    self.mouse_blocker.blocking_medivia()
                except Exception as e:
                    pass

        if self.mouse_blocker.blocking:
            time.sleep(self.delay)
        self.process_manager.moveTo(*item_position)
        if self.mouse_blocker.blocking:
            time.sleep(self.delay)
        self.process_manager.click(*item_position, button="right")

        if self.use_item == 1 and self.destination_region:
            if self.mouse_blocker.blocking:
                time.sleep(self.delay)
            self.logger.log("info", f"Using item at {dest_x, dest_y}")
            self.process_manager.moveTo(dest_x, dest_y)
            if self.mouse_blocker.blocking:
                time.sleep(self.delay)
            self.process_manager.click(dest_x, dest_y, button="left")

        if self.mouse_blocker.blocking:
            if self.process_manager.medivia:
                self.mouse_blocker.unblocking_medivia()
            else:
                self.mouse_blocker.stop_blocking()
                self.logger.log("info", f"Ended action. Unblocking user mouse input.")

        self.logger.log("info", f"Item action completed.")

    def execute(self):
        if not self.validate_resources():
            return

        screen = self.capture_screen()
        if screen is None:
            return

        item_position = self.find_item(screen)
        if not item_position:
            return

        self.perform_movement(item_position)


class CastIciclesMedivia(ImageAction):
    def __init__(self, priority=5, instance_n: int = 1):
        super().__init__(priority)

        self.instance_n = instance_n

        self.use_item = None
        self.icicle_path = None
        self.icicle_threshold = None
        self.battle_region = None
        self.panels_region = None
        self.map_region = None
        self.destination_region = None
        self.delay = None
        self._initialize()

        self.config_manager.add_observer(f"use_item_{self.instance_n}", self)
        self.config_manager.add_observer(f"icicle_path_{self.instance_n}", self)
        self.config_manager.add_observer(f"icicle_threshold_{self.instance_n}", self)
        self.config_manager.add_observer("panels_region", self)
        self.config_manager.add_observer("battle_region", self)
        self.config_manager.add_observer("map_region", self)
        self.config_manager.add_observer(f"destination_region_{self.instance_n}", self)
        self.config_manager.add_observer(f"delay_{self.instance_n}", self)

    def _initialize(self):
        """Initialize all configs need to execute action."""

        required_keys = [
            f"use_item_{self.instance_n}",
            f"icicle_path_{self.instance_n}",
            "battle_region",
            "panels_region",
            "map_region",
            f"destination_region_{self.instance_n}",
            f"delay_{self.instance_n}"
        ]

        try:
            self.config_manager.validate_config(required_keys=required_keys)
        except ValueError as e:
            self.logger.log("error", f"Configuration validation failed: {e}")
            raise

        self.use_item = self.config_manager.get(key=f"use_item_{self.instance_n}", default=0)
        self.icicle_path = self.config_manager.get(key=f"icicle_path_{self.instance_n}", default=None)
        self.icicle_threshold = self.config_manager.get(key=f"icicle_threshold_{self.instance_n}", default=0.8)
        self.battle_region = self.config_manager.get(key="battle_region", default=None)
        self.panels_region = self.config_manager.get(key="panels_region", default=None)
        self.map_region = self.config_manager.get(key="map_region", default=None)
        self.destination_region = self.config_manager.get(key=f"destination_region_{self.instance_n}", default=None)
        self.delay = self.config_manager.get(key=f"delay_{self.instance_n}", default=0.08)

    def on_config_update(self, key, value):
        """React in config update"""
        if key == f"item_path_{self.instance_n}":
            self.icicle_path = value
            self.logger.log("info", f"Updated icicle_path_{self.instance_n} to {value}")
        elif key == f"item_threshold_{self.instance_n}":
            self.icicle_threshold = value
            self.logger.log("info", f"Updated icicle_threshold_{self.instance_n} to {value}")
        elif key == "battle_region":
            self.battle_region = value
            self.logger.log("info", f"Updated battle_region to {value}")
        elif key == "panels_region":
            self.panels_region = value
            self.logger.log("info", f"Updated panels_region to {value}")
        elif key == "map_region":
            self.map_region = value
            self.logger.log("info", f"Updated map_region to {value}")
        elif key == f"destination_region_{self.instance_n}":
            self.destination_region = value
            self.logger.log("info", f"Updated destination_region_{self.instance_n} to {value}")
        elif key == f"use_item_{self.instance_n}":
            self.use_item = value
            self.logger.log("info", f"Updated use_item_{self.instance_n} to {value}")
        elif key == f"delay_{self.instance_n}":
            self.delay = value
            self.logger.log("info", f"Updated delay_{self.instance_n} to {value}")

    def validate_resources(self):
        if not self.validate_template(template_path=self.icicle_path, template_name=f"Item path {self.instance_n}"):
            return False
        return True

    def find_item(self, screen):
        self.logger.log("info", f"Searching for the item_{self.instance_n}")
        for region in self.panels_region:
            x, y, width, height = region
            cropped_screen = screen[y:y+height, x:x+width]
            item_position_in_region = self.screen_manager.find_image(
                main_image=cropped_screen,
                template=self.icicle_path,
                threshold=self.icicle_threshold
            )
            if item_position_in_region:
                return item_position_in_region[0] + x, item_position_in_region[1] + y
        self.logger.log("error", f"item_{self.instance_n} not found")
        return None

    def find_red_pixel(self, screen):
        """Encontra um pixel vermelho puro (#ff0000) dentro da região de batalha e seleciona o ponto médio no eixo X."""
        for region in self.battle_region:
            x, y, width, height = region
            cropped_screen = screen[y:y + height, x:x + width]  # Recorta a região de batalha

            # Converte para formato RGB caso a imagem seja BGR
            cropped_screen = cv2.cvtColor(cropped_screen, cv2.COLOR_BGR2RGB)

            # Encontra todos os pixels que correspondem a #ff0000 (255, 0, 0)
            red_pixels = np.where(
                (cropped_screen[:, :, 0] == 255) &  # Canal R (Vermelho)
                (cropped_screen[:, :, 1] == 0) &  # Canal G (Verde)
                (cropped_screen[:, :, 2] == 0)  # Canal B (Azul)
            )

            if len(red_pixels[0]) > 0:  # Se encontrou pelo menos um pixel vermelho
                # Calcula a média dos valores no eixo X
                mean_x = int(np.mean(red_pixels[1]))

                # Encontra os índices onde X é aproximadamente igual à média
                closest_indices = np.where(red_pixels[1] == mean_x)[0]

                # Escolhe um Y correspondente a esse X médio
                if len(closest_indices) > 0:
                    index = random.choice(closest_indices)  # Escolhe um índice correspondente ao X médio
                    target_x = mean_x + x + random.randint(-10, 10)  # Ajusta para a posição original da tela
                    target_y = red_pixels[0][index] + y + 5
                    return target_x, target_y

        return None  # Nenhum pixel vermelho encontrado

    def perform_movement(self, item_position):
        """Realiza a movimentação para usar a magia."""
        # Buscar a posição do alvo dentro da battle_region
        target_position = self.find_red_pixel(self.capture_screen())

        if not target_position:
            self.logger.log("error", "Nenhum inimigo encontrado na região de batalha!")
            return

        target_x, target_y = target_position

        self.logger.log("info", f"Clicking in item at position {item_position}")

        if self.process_manager.is_foreground() or self.process_manager.is_mouse_over_window():
            if not self.process_manager.medivia:
                self.logger.log("info", "Window in the foreground or mouse over window. Blocking user mouse input.")
                self.mouse_blocker.start_blocking()
            else:
                try:
                    self.mouse_blocker.blocking_medivia()
                except Exception:
                    pass

        if self.mouse_blocker.blocking:
            time.sleep(self.delay)
        self.process_manager.moveTo(*item_position)
        if self.mouse_blocker.blocking:
            time.sleep(self.delay)
        self.process_manager.click(*item_position, button="right")

        if self.use_item == 1:
            if self.mouse_blocker.blocking:
                time.sleep(self.delay)
            self.logger.log("info", f"Using item at {target_x, target_y}")
            self.process_manager.moveTo(target_x, target_y)
            if self.mouse_blocker.blocking:
                time.sleep(self.delay)
            self.process_manager.click(target_x, target_y, button="left")

        if self.mouse_blocker.blocking:
            if self.process_manager.medivia:
                self.mouse_blocker.unblocking_medivia()
            else:
                self.mouse_blocker.stop_blocking()
                self.logger.log("info", "Ended action. Unblocking user mouse input.")

        self.logger.log("info", "Item action completed.")

    def execute(self):
        if not self.validate_resources():
            return

        screen = self.capture_screen()
        if screen is None:
            return

        item_position = self.find_item(screen)
        if not item_position:
            return

        self.perform_movement(item_position)
