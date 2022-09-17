ARG NODE_VERSION
FROM node:$NODE_VERSION
ADD ./build-rocketchat.sh /build/build-rocketchat.sh
ADD ./vips-* /build
ADD ./rocketchat.tar.gz /build
ADD ./patches-4/app.patch /build/patches/app.patch
RUN /build/build-rocketchat.sh
RUN mv /build/bundle /rocketchat
RUN rm -rf /build
RUN rm -rf /var/lib/apt/lists/*
