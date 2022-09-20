ARG NODE_VERSION
FROM node:$NODE_VERSION
ADD ./build-rocketchat.sh /build/build-rocketchat.sh
ADD ./rocketchat.tar.gz /build
RUN /build/build-rocketchat.sh
RUN mv /build/bundle /rocketchat
RUN rm -rf /build
RUN rm -rf /var/lib/apt/lists/*
