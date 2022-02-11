ARG NODE_VERSION
FROM node:$NODE_VERSION
ARG ROCKETCHAT_VERSION
ADD ./build-rocketchat.sh /build/build-rocketchat.sh
ADD ./patches/app.patch /build/patches/app.patch
RUN /build/build-rocketchat.sh $ROCKETCHAT_VERSION
RUN mv /build/bundle /rocketchat
RUN rm -rf /build
RUN rm -rf /var/lib/apt/lists/*
