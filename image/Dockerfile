FROM ubuntu:24.10

ARG username=anonymous
ARG path=/games

WORKDIR $path

SHELL ["/bin/bash", "-o", "pipefail", "-c"]
RUN echo steam steam/question select "I AGREE" | debconf-set-selections \
 && echo steam steam/license note '' | debconf-set-selections

# Update the repository and install SteamCMD
ARG DEBIAN_FRONTEND=noninteractive
RUN dpkg --add-architecture i386 \
 && apt-get update -y \
 && apt-get install -y --no-install-recommends ca-certificates locales steamcmd \
 && rm -rf /var/lib/apt/lists/*

# Create symlink for executable
RUN ln -s /usr/games/steamcmd /usr/bin/steamcmd

RUN steamcmd +force_install_dir $path  +login anonymous +app_update 2311970 +quit

RUN apt-get update
RUN apt-get install python3 -y

COPY ./script.py .
COPY ./commands.sh .
RUN ["chmod", "+x", "./commands.sh"]

RUN mkdir config
RUN touch config/game_settings.txt

ENTRYPOINT ["./commands.sh"]

# ENTRYPOINT ["ls"]
