# Run vacuum robot
## Description
This configuration will determine the last time of the cleaning and ask if the cleaning should be started. On positive reaction (eg. ✅) a regular cleaning will be started.

![screenshot02](../images/screenshot03.png)

## Dependencies

* Matrix room (obviously)
* [home-assistant](https://www.home-assistant.io)
* Vacuum robot integration. In this example we will be using [homeassistant-roborock](https://github.com/humbertogontijo/homeassistant-roborock).

## home-assistant configuration

### sensor

This sensor will provide input for hasskbot. If the sensor turn to state `on` then hasskbot will prompt in a Matrix room to start a regular cleaning should be started.

If not using roborock integration then check if your robot integration provides the last cleaning timestamp. In this example it's `sensor.roborock_s7_maxv_last_clean_end`.

Mainly hasskbot just needs a sensor, which it will monitor, and the start, which will trigger the prompt.

`template.yaml`:
```YAML
- sensor:
  - name: "roborock_s7_maxv_next_clean_due"
    # clean every three days
    state: >
      {% set last_clean = as_timestamp(states('sensor.roborock_s7_maxv_last_clean_end')) %}
      {% set next_clean  = last_clean+(60*60*24*3) %}
      {% set now = as_timestamp(now()) %}
      {% if now > next_clean %}on
      {% else %}off
      {% endif %}
```

### start cleaning script

This script will be called by hasskbot to start the regular cleaning.

`scripts.yaml`:
```YAML
roborock_vacuum_clean_all:
  alias: 'Roborock: vacuum clean all'
  sequence:
  - service: notify.matrix_home_assistant
    data:
      message: "\U0001F9F9 Roborock: setting cleaning parameters"
  - service: roborock.vacuum_set_fan_speed
    data:
      fan_speed: balanced
    target:
      entity_id: vacuum.roborock_s7_maxv
  - wait_for_trigger:
    - platform: template
      value_template: '{{ state_attr(''vacuum.roborock_s7_maxv'', ''fan_speed'') ==
        "balanced" }}'
      for:
        hours: 0
        minutes: 0
        seconds: 30
    timeout:
      hours: 0
      minutes: 0
      seconds: 3
      milliseconds: 0
    continue_on_timeout: true
  - service: roborock.vacuum_set_mop_mode
    data:
      mop_mode: standard
    target:
      entity_id: vacuum.roborock_s7_maxv
  - wait_for_trigger:
    - platform: template
      value_template: '{{ state_attr(''vacuum.roborock_s7_maxv'', ''mop_mode'') ==
        "standard" }}'
      for:
        hours: 0
        minutes: 0
        seconds: 30
    timeout:
      hours: 0
      minutes: 0
      seconds: 3
      milliseconds: 0
    continue_on_timeout: true
  - service: roborock.vacuum_set_mop_intensity
    data:
      mop_intensity: 'off'
    target:
      entity_id: vacuum.roborock_s7_maxv
  - wait_for_trigger:
    - platform: template
      value_template: '{{ state_attr(''vacuum.roborock_s7_maxv'', ''mop_intensity'')
        == "off" }}'
      for:
        hours: 0
        minutes: 0
        seconds: 30
    timeout:
      hours: 0
      minutes: 0
      seconds: 3
      milliseconds: 0
  - service: notify.matrix_home_assistant
    data:
      message: "\U0001F9F9 Roborock: starting regular cleaning"
  - device_id: 84c2bb8c1091009d40a2c4332ac02687
    domain: vacuum
    entity_id: vacuum.roborock_s7_maxv
    type: clean
    enabled: true
  mode: single
  icon: mdi:vacuum
```

## hasskbot configuration

`secrets.env`:
```
HASS_SENSOR=sensor.roborock_s7_maxv_next_clean_due
HASS_STATE=on
```

`configuration.yaml`:
```YAML
connectors:
  matrix:
    # Required
    homeserver: "https://matrix.example.com"
    mxid: $MATRIX_MXID
    # use password or token
    #password: $MATRIX_PASSWORD
    access_token: $MATRIX_TOKEN
    # A dictionary of multiple rooms
    # One of these should be named 'main'
    rooms:
      main:
        alias: $MATRIX_ROOM_MAIN
        # Send messages as msgType: m.notice
        send_m_notice: False
    nick: "Roborock"  # The nick will be set on startup
    #room_specific_nicks: False  # Look up room specific nicknames of senders (expensive in large rooms)
  homeassistant:
    url: https://home-assistant.example.com
    # How to get the token: https://developers.home-assistant.io/docs/auth_api/#long-lived-access-token
    # Simple:
    # * Browse to https://my-home-assistant.example.com/profile
    # * Scroll to the bottom of the page (Long-Lived Access Tokens)
    # * Create a Long-Lived Access Token
    token: $HOME_ASSISTANT_TOKEN
skills:
  # Please leave the name unchanged
  hasskbot:
    # Can be path, repo or Python module
    # Details: https://docs.opsdroid.dev/en/stable/packaging.html#single-module-extensions
    path: /skills/hasskbot
    config:
      # Question to ask when the entity state is mached
      confirm_message: "\U0001f552 \U0001F9F9 Last cleaning was 3 days ago. Should I start regular cleaning \U0001F609"
      # Expire confirm event after X minutes
      expire_after: 120
      # Expire message
      expire_message: "\u23f0 Time for reaction is expired."
      # Allowed users
      # MXID is used
      # RegEx is possible
      allowed_users_re:
        - "^@oleg:fiksel.info$"
      # HASS data for triggering the automation/script
      hass_domain: 'script'
      hass_service: 'turn_on'
      hass_entity: 'script.roborock_vacuum_clean_all'
      # Message to send when the automation/script is triggered
      acknowledge_message: "\U0001F9F9 Starting regular cleaning"
```