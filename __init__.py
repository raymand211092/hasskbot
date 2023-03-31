import logging

from opsdroid.events import Message, Reaction
from opsdroid.matchers import match_event, match_crontab
from opsdroid_homeassistant import HassSkill, match_hass_state_changed

import re
import os
import datetime

# import pprint
# pp = pprint.PrettyPrinter(indent=2)

_LOGGER = logging.getLogger(__name__)

version = "v1.0.2"

EMOJI_YES = '\u2705'
EMOJI_NO = '\u274c'
EMOJI_THUMBSUP = '\U0001f44d\ufe0f'


def _read_env_var(env_var_name):
    try:
        os.environ[env_var_name]
    except KeyError:
        _LOGGER.fatal("Environment variable {} is not defined.".format(env_var_name))
    return os.environ[env_var_name]


# Have to use environment variables because of using decorators (match_hass_state_changed)
hass_sensor = _read_env_var('HASS_SENSOR')
hass_state = _read_env_var('HASS_STATE')


class HASkill(HassSkill):
    def __init__(self, opsdroid, config):
        super(HASkill, self).__init__(opsdroid, config)
        # Load custom configuration part
        self.conf = self.opsdroid.config['skills']['hasskbot']['config']
        self.confirm_event = ""
        # Set default value if not specified in the config
        if 'expire_after' not in self.conf:
            self.conf['expire_after'] = 30

    async def _if_user_allowed(self, user):
        for allowed_user in self.conf['allowed_users_re']:
            if re.search(allowed_user, user, re.IGNORECASE):
                return True
        return False

    @match_crontab('* * * * *')
    async def cron(self, event):
        if self.confirm_event == "":
            return
        confirm_event_expire_time = self.confirm_event.created + datetime.timedelta(minutes=self.conf['expire_after'])
        present = datetime.datetime.now()
        if present > confirm_event_expire_time:
            _LOGGER.info("Expiring event {}".format(self.confirm_event.raw_event['event_id']))
            self.confirm_event = ""
            # TODO: delete message as soon it's possible using Matrix connector
            await self.opsdroid.get_connector("matrix").send(Message(self.conf['expire_message']))

    @match_event(Reaction)
    async def reaction(self, event):
        event_id = event.linked_event.raw_event['event_id']

        # Ignore reactions if the confirmation message have not been sent yet
        if self.confirm_event == "":
            return

        # Ignore other reactions
        confirm_event_id = self.confirm_event.raw_event['event_id']
        if event_id != confirm_event_id:
            return

        if not await self._if_user_allowed(event.user_id):
            _LOGGER.info("Access for user {} is denied".format(event.user_id))
            return

        _LOGGER.info("Access for user {} is granted".format(event.user_id))
        emoji = event.emoji
        _LOGGER.info("Got reaction: {}, with for event id: {}".format(emoji, event_id))

        if emoji == EMOJI_NO:
            # Make sure the answer can be provided only once
            _LOGGER.info("Not going to process reactions to event: {}".format(confirm_event_id))
            self.confirm_event = ""
            return
        if emoji == EMOJI_YES:
            _LOGGER.info("Calling home-assistant service")
            await self.opsdroid.get_connector("matrix").react(self.confirm_event, EMOJI_THUMBSUP)
            await self.opsdroid.get_connector("matrix").respond(self.conf['acknowledge_message'])
            await self.call_service(self.conf['hass_domain'],
                                    self.conf['hass_service'],
                                    entity_id=self.conf['hass_entity'])
            # Make sure the answer can be provided only once
            self.confirm_event = ""
            return

    @match_hass_state_changed(hass_sensor, state=hass_state)
    async def ask(self, event):
        matrix_connector = self.opsdroid.get_connector("matrix")
        resp = await matrix_connector.send(Message(self.conf['confirm_message']))
        self.confirm_event = await matrix_connector._event_creator.create_event_from_eventid(resp.event_id,
                                                                                             resp.room_id)
        _LOGGER.info("Creating message event for user input with id: {}".format(resp.event_id))
        await matrix_connector.react(self.confirm_event, EMOJI_YES)
        await matrix_connector.react(self.confirm_event, EMOJI_NO)
