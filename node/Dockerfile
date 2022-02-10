FROM node:12.18.4-slim
ADD ./download.sh /build/download.sh
ADD ./build-rocketchat.sh /build/build-rocketchat.sh
ADD ./patches/app.patch /build/patches/app.patch
RUN /build/download.sh
RUN /build/build-rocketchat.sh
RUN rm -rf /build
RUN rm -rf /var/lib/apt/lists/*
