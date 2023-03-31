FROM ghcr.io/opsdroid/opsdroid:v0.28.0
RUN pip install opsdroid-homeassistant==0.2.0
COPY __init__.py /skills/hasskbot/__init__.py
