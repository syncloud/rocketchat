FROM node:12.18.4-slim
ADD ./build-rocketchat.sh /build/build-rocketchat.sh
ADD ./patches/app.patch /build/patches/app.patch
RUN /build/build-rocketchat.sh
RUN rm -rf /build
RUN rm -rf /var/lib/apt/lists/*
