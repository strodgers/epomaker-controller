FROM python:3.13-slim

RUN apt-get update && apt-get install -y \
    python3-tk \
    udev \
    && rm -rf /var/lib/apt/lists/*

COPY .. /src
WORKDIR /src

RUN pip install .

RUN useradd -ms /bin/bash nonrootuser && chown -R nonrootuser:nonrootuser /src

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]
