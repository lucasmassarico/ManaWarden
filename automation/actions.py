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


class Action(ABC):
    def __init__(self, priority):
        self.priority = priority

        self.config_manager = ConfigManager()
        self.logger = LogManager()
        self.process_manager = ProcessManager()
        self.mouse_blocker = MouseBlocker()

        self.hwnd = "Miracle 7.4 - Dropper"
        self.super_hwnd = self.process_manager.find_hWnd_by_name(self.hwnd)
        self.process_manager.set_hwnd(self.super_hwnd)

    @abstractmethod
    def execute(self):
        pass


class ImageAction(Action):
    def __init__(self, priority):
        super().__init__(priority)

        self.screen_manager = ScreenManager()
        self.screen_manager.set_window_handle(self.super_hwnd)

        pass

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


class MoveBlankRuneAction(ImageAction):
    def __init__(self, priority=2, config_path="../configs.mana"):
        """

        :type priority: Set priority of action
        """
        super().__init__(priority)
        self.blank_rune_path = "../assets/templates/blank_rune.png"
        self.destination_coords = None
        self.destination_region = None

        # example test
        self.hwnd = "Miracle 7.4 - Dropper"
        hwnd = self.process_manager.find_hWnd_by_name(self.hwnd)
        self.process_manager.set_hwnd(hwnd)
        self.screen_manager.set_window_handle(hwnd)

    def get_destination_region(self):
        return self.destination_region

    def set_destination_region(self, region):
        self.destination_region = region

    def get_destination_coords(self):
        return self.destination_coords

    def set_destination_coords(self, destination_x, destination_y):
        self.destination_coords = (destination_x, destination_y)

    def execute(self):
        if not self.destination_coords:
            print("Destination coord not defined.")
            return

        screen = self.screen_manager.capture_screenshot()
        position = self.screen_manager.find_image(main_image=screen, template=self.blank_rune_path)
        if position:
            print(position)
            start_x, start_y = position
            dest_x, dest_y = self.destination_coords
            self.process_manager.moveTo(start_x, start_y)
            time.sleep(0.2)
            self.process_manager.perform_drag_and_drop(start_x, start_y, dest_x, dest_y)
            print("Blank rune moved with success")
        else:
            print("Blank rune not found.")


# action = MoveBlankRuneAction(priority=2)
# action.set_destination_coords(destination_x=1832, destination_y=155)
#
# action.execute()


class CastSpellAction(Action):
    def __init__(self, priority=3):
        """

        :param priority: Set priority of action
        """
        super().__init__(priority)
        self.process_manager = ProcessManager()
        self.hotkey_scan_code = None

        # example_test
        self.hwnd = "Miracle 7.4 - Dropper"
        hwnd = self.process_manager.find_hWnd_by_name(self.hwnd)
        self.process_manager.set_hwnd(hwnd)

    def set_hotkey_to_cast(self, hotkey):
        self.hotkey_scan_code = hotkey

    def execute(self):
        if not self.hotkey_scan_code:
            print("Need hotkey defined to cast spell.")
            return

        self.process_manager.send_key_to_window(scan_code=self.hotkey_scan_code)
        print("Attempt to cast spell made.")


# action_spell = CastSpellAction(priority=3)
# action_spell.set_hotkey_to_cast(hotkey=keys.get("H"))
#
# action_spell.execute()


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

        self.fishing_rod_path = self.config_manager.get(key="fishing_rod_path", default="../assets/templates/fishing_rod.png")
        self.water_path = self.config_manager.get(key="water_path", default="../assets/templates/water.png")
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
            self.logger.log("info", f"Window in the foreground or mouse over window. Blocking user mouse input.")
            self.mouse_blocker.start_blocking()
        else:
            self.logger.log("info", f"Window not in the foreground.")

        if self.mouse_blocker.blocking:
            time.sleep(0.03)
        self.process_manager.moveTo(*rod_position)
        self.process_manager.click(*rod_position, button="right")

        selected_water = random.choice(water_positions)
        self.logger.log("info", f"Left-clicking on water region at {selected_water}.")
        if self.mouse_blocker.blocking:
            time.sleep(0.03)
        self.process_manager.moveTo(*selected_water)
        self.process_manager.click(*selected_water, button="left")

        if self.mouse_blocker.blocking:
            self.mouse_blocker.stop_blocking()

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


class MoveItemAction(ImageAction):
    def __init__(self, priority=5, instance_n: int=1):
        super().__init__(priority)

        self._instance_n = instance_n

        self.item_path = None
        self.item_threshold = None
        self.panels_region = None
        self.map_region = None
        self.destination_region = None
        self._initialize()

        self.config_manager.add_observer(f"item_path_{self._instance_n}", self)
        self.config_manager.add_observer(f"item_threshold_{self._instance_n}", self)
        self.config_manager.add_observer("panels_region", self)
        self.config_manager.add_observer("map_region", self)
        self.config_manager.add_observer(f"destination_region_{self._instance_n}", self)

    def _initialize(self):
        """Initialize all configs need to execute action."""

        required_keys = [
            f"item_path_{self._instance_n}",
            "panels_region",
            "map_region",
            f"destination_region_{self._instance_n}"
        ]

        try:
            self.config_manager.validate_config(required_keys=required_keys)
        except ValueError as e:
            self.logger.log("error", f"Configuration validation failed: {e}")
            raise

        self.item_path = self.config_manager.get(key=f"item_path_{self._instance_n}", default=None)
        self.item_threshold = self.config_manager.get(key=f"item_threshold_{self._instance_n}", default=0.8)
        self.panels_region = self.config_manager.get(key="panels_region", default=None)
        self.map_region = self.config_manager.get(key="map_region", default=None)
        self.destination_region = self.config_manager.get(key=f"destination_region_{self._instance_n}", default=None)

    def on_config_update(self, key, value):
        """React in config update"""
        if key == f"item_path_{self._instance_n}":
            self.item_path = value
            self.logger.log("info", f"Updated item_path_{self._instance_n} to {value}")
        elif key == f"item_threshold_{self._instance_n}":
            self.item_threshold = value
            self.logger.log("info", f"Updated item_threshold_{self._instance_n} to {value}")
        elif key == "panels_region":
            self.panels_region = value
            self.logger.log("info", f"Updated panels_region to {value}")
        elif key == "map_region":
            self.map_region = value
            self.logger.log("info", f"Updated map_region to {value}")
        elif key == f"destination_region_{self._instance_n}":
            self.destination_region = value
            self.logger.log("info", f"Updated destination_region_{self._instance_n} to {value}")

    def validate_resources(self):
        if not self.validate_template(template_path=self.item_path, template_name=f"Item path {self._instance_n}"):
            return False
        if not self.destination_region:
            return False
        return True

    def find_item(self, screen):
        self.logger.log("info", f"Searching for the item_{self._instance_n}")
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
        self.logger.log("error", f"item_{self._instance_n} not found")
        return None

    def perform_movement(self, item_position):
        dest_x, dest_y, dest_width, dest_height = self.destination_region

        self.logger.log("info", f"Clicking in item at position {item_position}")

        if self.process_manager.is_foreground() or self.process_manager.is_mouse_over_window():
            self.logger.log("info", f"Window in the foreground or mouse over window. Blocking user mouse input.")
            self.mouse_blocker.start_blocking()
        else:
            self.logger.log("info", f"Window not in the foreground.")

        if self.mouse_blocker.blocking:
            time.sleep(0.08)
        self.process_manager.moveTo(*item_position)
        self.process_manager.click(*item_position, button="right")

        if self.mouse_blocker.blocking:
            time.sleep(0.08)
        self.logger.log("info", f"Using item at {dest_x, dest_y}")
        self.process_manager.moveTo(dest_x, dest_y)
        if self.mouse_blocker.blocking:
            time.sleep(0.08)
        self.process_manager.click(dest_x, dest_y, button="left")

        if self.mouse_blocker.blocking:
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
