"""
"""

import logging

from gi.repository import Gtk

from gaphor.core import inject, event_handler
from gaphor.event import ServiceInitializedEvent, ActionExecuted
from gaphor.abc import Service, ActionProvider

logger = logging.getLogger(__name__)


class ActionManager(Service):
    """
    This service is responsible for maintaining actions.
    """

    component_registry = inject("component_registry")
    event_manager = inject("event_manager")

    def __init__(self):
        self.ui_manager = Gtk.UIManager()

    def init(self, app):
        logger.info("Loading action provider services")

        for service, name in self.component_registry.all(ActionProvider):
            logger.debug("Service is %s" % service)
            self.register_action_provider(service)

        self.event_manager.subscribe(self._service_initialized_handler)

    def shutdown(self):

        logger.info("Shutting down")

        self.event_manager.unsubscribe(self._service_initialized_handler)

    def execute(self, action_id, active=None):

        logger.debug("Executing action, action_id is %s" % action_id)

        a = self.get_action(action_id)
        if a:
            a.activate()
            self.event_manager.handle(ActionExecuted(action_id, a))
        else:
            logger.warning("Unknown action %s" % action_id)

    def update_actions(self):

        self.ui_manager.ensure_update()

    def get_action(self, action_id):

        for g in self.ui_manager.get_action_groups():
            a = g.get_action(action_id)
            if a:
                return a

    def register_action_provider(self, action_provider):

        logger.debug("Registering action provider %s" % action_provider)

        try:
            # Check if the action provider is not already registered
            action_provider.__ui_merge_id
        except AttributeError:
            assert action_provider.action_group
            self.ui_manager.insert_action_group(action_provider.action_group, -1)

            try:
                menu_xml = action_provider.menu_xml
            except AttributeError:
                pass
            else:
                action_provider.__ui_merge_id = self.ui_manager.add_ui_from_string(
                    menu_xml
                )

    def unregister_action_provider(self, action_provider):
        try:
            # Check if the action provider is registered
            action_provider.__ui_merge_id
        except AttributeError:
            pass
        else:
            self.ui_manager.remove_ui(action_provider.__ui_merge_id)
            self.ui_manager.remove_action_group(action_provider.action_group)
            del action_provider.__ui_merge_id

    @event_handler(ServiceInitializedEvent)
    def _service_initialized_handler(self, event):

        logger.debug("Handling ServiceInitializedEvent")
        logger.debug("Service is %s" % event.service)

        if isinstance(event.service, ActionProvider):

            logger.debug("Loading registered service %s" % event.service)

            self.register_action_provider(event.service)

    # UIManager methods:

    def get_widget(self, path):
        return self.ui_manager.get_widget(path)

    def get_accel_group(self):
        return self.ui_manager.get_accel_group()
