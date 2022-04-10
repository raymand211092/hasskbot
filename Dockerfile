FROM opsdroid/opsdroid:v0.25.0
RUN pip install opsdroid-homeassistant==0.2.0
COPY __init__.py /skills/hasskbot/__init__.py
