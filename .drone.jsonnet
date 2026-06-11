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
             name: 'cli',
             image: 'golang:1.23',
             commands: [
               './cli/build.sh',
             ],
           },
           {
             name: 'rocketchat build',
             image: 'rocketchat/rocket.chat:' + rocketchat,
             user: 'root',
             commands: [
               './rocketchat/build.sh ' + rocketchat,
             ],
           },
           {
             name: 'mongo build',
             image: 'mongo:' + mongo,
             commands: [
               './mongo/build.sh',
             ],
           },
         ] + [
           {
             name: 'rocketchat test ' + distro,
             image: 'syncloud/platform-' + distro + '-' + arch + ':' + platform,
             commands: [
               './rocketchat/test.sh',
             ],
           }
           for distro in distros
         ] + [
           {
             name: 'mongo test ' + distro,
             image: 'syncloud/platform-' + distro + '-' + arch + ':' + platform,
             commands: [
               './mongo/test.sh',
             ],
           }
           for distro in distros
         ] + [
           {
             name: 'package',
             image: 'debian:bookworm-slim',
             commands: [
               './package.sh ' + name + ' $DRONE_BUILD_NUMBER',
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
                  volumes: [{
                    name: 'shm',
                    path: '/dev/shm',
                  }],
                  commands: [
                    './test/e2e/run.sh ' + distro_default + ' ' + name + ' e2e ./specs',
                  ],
                },
              ]
              else []) +
         (if arch == 'amd64' then [
            {
              name: 'test-upgrade',
              image: 'mcr.microsoft.com/playwright:' + playwright,
              volumes: [{
                name: 'shm',
                path: '/dev/shm',
              }],
              commands: [
                './test/e2e/run.sh ' + distro_default + ' ' + name + ' e2e-upgrade ./specs-upgrade',
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
    {
      name: 'shm',
      temp: {},
    },
  ],
}];

build('amd64', true) +
build('arm64', false)
