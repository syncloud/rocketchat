local name = 'rocketchat';
local rocketchat = '8.4.3';
// mongo 5+ needs ARMv8.2-A (rpi5 / Odroid C4/HC4); the install hook rejects older arm64 (rpi4)
local mongo = '8.0.23';
local platform = '26.06.01';
local playwright = 'v1.59.1-jammy';
local store_publisher = 'stable-291';
local python = '3.12-slim-bookworm';
local distro_default = 'buster';
local distros = ['bookworm', 'buster'];

local build(arch, test_ui) = [{
  kind: 'pipeline',
  type: 'docker',
  name: arch,
  platform: {
    os: 'linux',
    arch: arch,
  },
  steps: [
           {
             name: 'version',
             image: 'alpine:3.17.0',
             commands: [
               'echo $DRONE_BUILD_NUMBER > version',
             ],
           },
           {
             name: 'cli',
            image: 'golang:1.23',
            commands: [
              'cd cli',
              'CGO_ENABLED=0 go build -o ../build/snap/meta/hooks/install ./cmd/install',
              'CGO_ENABLED=0 go build -o ../build/snap/meta/hooks/configure ./cmd/configure',
              'CGO_ENABLED=0 go build -o ../build/snap/meta/hooks/pre-refresh ./cmd/pre-refresh',
              'CGO_ENABLED=0 go build -o ../build/snap/meta/hooks/post-refresh ./cmd/post-refresh',
              'CGO_ENABLED=0 go build -o ../build/snap/bin/cli ./cmd/cli',
            ],
           },
           {
             name: 'server build',
             image: 'rocketchat/rocket.chat:' + rocketchat,
             user: 'root',
             commands: [
               './node/build.sh ' + rocketchat,
             ],
           },
           {
             name: 'server test',
             image: 'debian:bookworm-slim',
             commands: [
               'build/snap/node/bin/node.sh --help',
             ],
           },
           {
             name: 'mongo build',
             image: 'mongo:' + mongo,
             commands: [
               './mongo/build.sh',
             ],
           },
           {
             name: 'mongo test',
             image: 'syncloud/platform-buster-' + arch + ':' + platform,
             commands: [
               './mongo/test.sh',
             ],
           },
           {
             name: 'package',
             image: 'debian:bookworm-slim',
             commands: [
               'VERSION=$(cat version)',
               './package.sh ' + name + ' $VERSION ',
             ],
           },
         ] + [
           {
             name: 'test ' + distro,
             image: 'python:' + python,
             commands: [
               'DOMAIN="' + distro + '.com"',
               'APP_DOMAIN="' + name + '.' + distro + '.com"',
               'getent hosts $APP_DOMAIN | sed "s/$APP_DOMAIN/auth.$DOMAIN/g" | tee -a /etc/hosts',
               'cat /etc/hosts',
               'APP_ARCHIVE_PATH=$(realpath $(cat package.name))',
               'cd test',
               './deps.sh',
               'py.test -x -s test.py --device-user=testuser --distro=' + distro + ' --app-archive-path=$APP_ARCHIVE_PATH --app=' + name + ' --arch=' + arch,
             ],
           }
           for distro in distros
         ] + (if test_ui then [
                {
                  name: 'test-ui',
                  image: 'mcr.microsoft.com/playwright:' + playwright,
                  commands: [
                    './test/e2e/run.sh ' + distro_default + ' ' + name,
                  ],
                },
              ]
              else []) +
         (if arch == 'amd64' then [
            {
              name: 'test-upgrade',
              image: 'python:' + python,
              commands: [
                'DOMAIN="' + distro_default + '.com"',
                'APP_DOMAIN="' + name + '.' + distro_default + '.com"',
                'getent hosts $APP_DOMAIN | sed "s/$APP_DOMAIN/auth.$DOMAIN/g" | tee -a /etc/hosts',
                'cat /etc/hosts',
                'APP_ARCHIVE_PATH=$(realpath $(cat package.name))',
                'cd test',
                './deps.sh',
                'py.test -x -s upgrade.py --device-user=testuser --distro=' + distro_default + ' --app-archive-path=$APP_ARCHIVE_PATH --app=' + name,
              ],
            },
            {
              name: 'test-ui-after-upgrade',
              image: 'mcr.microsoft.com/playwright:' + playwright,
              commands: [
                './test/e2e/run.sh ' + distro_default + ' ' + name + ' e2e-after-upgrade',
              ],
            },
          ] else []) + [
    {
      name: 'publish',
      image: 'syncloud/store-publisher:' + store_publisher,
      environment: {
        SYNCLOUD_TOKEN: { from_secret: 'SYNCLOUD_TOKEN' },
      },
      command: ['snap', '-c', '${DRONE_BRANCH}'],
      when: {
        branch: ['master', 'stable'],
        event: ['push'],
      },
    },
    {
      name: 'artifact',
      image: 'appleboy/drone-scp:1.6.4',
      settings: {
        host: {
          from_secret: 'artifact_host',
        },
        username: 'artifact',
        key: {
          from_secret: 'artifact_key',
        },
        timeout: '2m',
        command_timeout: '2m',
        target: '/home/artifact/repo/' + name + '/${DRONE_BUILD_NUMBER}-' + arch,
        source: 'artifact/*',
        strip_components: 1,
      },
      when: {
        status: ['failure', 'success'],
        event: ['push'],
      },
    },
  ],
  trigger: {
    event: [
      'push',
    ],
  },
  services: [
    {
      name: name + '.' + distro + '.com',
      image: 'syncloud/platform-' + distro + '-' + arch + ':' + platform,
      privileged: true,
      entrypoint: ['/bin/sh', '-c', "mkdir -p /etc/systemd/system/snapd.service.d && printf '[Service]\\nExecStartPost=/bin/sh -c \"/usr/bin/snap set system refresh.hold=2099-01-01T00:00:00Z\"\\n' > /etc/systemd/system/snapd.service.d/disable-refresh.conf && exec /sbin/init"],
      volumes: [
        {
          name: 'dbus',
          path: '/var/run/dbus',
        },
        {
          name: 'dev',
          path: '/dev',
        },
      ],
    } for distro in distros
  ],
  volumes: [
    {
      name: 'dbus',
      host: {
        path: '/var/run/dbus',
      },
    },
    {
      name: 'dev',
      host: {
        path: '/dev',
      },
    },
  ],
}];

build('amd64', true) +
build('arm64', false)
