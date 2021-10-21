# dsdslsd\
# saasadsl
FROM ubuntu:20.04

ENV TZ="Europe/Berlin"

RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localetime && echo $TZ > /etc/timezone \
    && env

RUN apt-get update && \
    apt-get install --no-install-recommends -y \
    libglib2.0-0 curl python3.8 python3-pip && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

RUN pip3 install conan
RUN curl -sL https://aka.ms/InstallAzureCLIDeb | bash