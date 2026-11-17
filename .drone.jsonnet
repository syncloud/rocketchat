local name = 'rocketchat';
local rocketchat = '9.0.0';
local mongo = '8.0.38';
local platform = '26.10.02';
local playwright = 'mcr.microsoft.com/playwright:v1.59.1-jammy';
local store_publisher = 'stable-346';
local python = '3.12-slim-bookworm';
local golang = '1.25';
local debian = 'bookworm-slim';
local distro_default = 'bookworm';
local distros = ['bookworm', 'buster'];

local platform_image(distro) =
  'syncloud/platform-' + distro + ':' + platform;

local snapd_hold = "mkdir -p /etc/systemd/system/snapd.service.d && printf '[Service]\\nExecStartPost=/bin/sh -c \"/usr/bin/snap set system refresh.hold=2099-01-01T00:00:00Z\"\\n' > /etc/systemd/system/snapd.service.d/disable-refresh.conf && exec /sbin/init";

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
      image: 'golang:' + golang,
      commands: [
        './cli/build.sh',
      ],
    },
    {
      name: 'rocketchat',
      image: 'rocketchat/rocket.chat:' + rocketchat,
      user: 'root',
      commands: [
        './rocketchat/build.sh ' + rocketchat,
      ],
    },
    {
      name: 'mongo',
      image: 'mongo:' + mongo,
      commands: [
        './mongo/build.sh',
      ],
    },
  ] + [
    {
      name: 'cli test ' + distro,
      image: platform_image(distro),
      commands: [
        './cli/test.sh',
      ],
    }
    for distro in distros
  ] + [
    {
      name: 'rocketchat test ' + distro,
      image: platform_image(distro),
      commands: [
        './rocketchat/test.sh',
      ],
    }
    for distro in distros
  ] + [
    {
      name: 'mongo test ' + distro,
      image: platform_image(distro),
      commands: [
        './mongo/test.sh',
      ],
    }
    for distro in distros
  ] + [
    {
      name: 'package',
      image: 'debian:' + debian,
      commands: [
        './package.sh ' + name + ' $DRONE_BUILD_NUMBER',
      ],
    },
  ] + [
    {
      name: 'test ' + distro,
      image: 'python:' + python,
      commands: [
        './ci/test.sh test.py ' + distro + ' ' + name + ' ' + arch,
      ],
    }
    for distro in distros
  ] + (if test_ui then [
         {
           name: 'e2e',
           image: playwright,
           volumes: [{ name: 'shm', path: '/dev/shm' }],
           commands: [
             './test/e2e/run.sh specs/01-smoke.spec.ts',
           ],
         },
         {
           name: 'test-upgrade-prev',
           image: 'python:' + python,
           commands: [
             './ci/test.sh upgrade_prev.py ' + distro_default + ' ' + name + ' ' + arch,
           ],
         },
         {
           name: 'e2e-before-upgrade',
           image: playwright,
           volumes: [{ name: 'shm', path: '/dev/shm' }],
           commands: [
             './test/e2e/run.sh specs/02-pre-upgrade.spec.ts',
           ],
         },
         {
           name: 'test-upgrade',
           image: 'python:' + python,
           commands: [
             './ci/test.sh upgrade.py ' + distro_default + ' ' + name + ' ' + arch,
           ],
         },
         {
           name: 'e2e-after-upgrade',
           image: playwright,
           volumes: [{ name: 'shm', path: '/dev/shm' }],
           commands: [
             './test/e2e/run.sh specs/03-post-upgrade.spec.ts',
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
        branch: ['stable'],
        event: ['push'],
      },
    },
    {
      name: 'artifact',
      image: 'appleboy/drone-scp:1.6.4',
      settings: {
        host: { from_secret: 'artifact_host' },
        username: 'artifact',
        key: { from_secret: 'artifact_key' },
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
    event: ['push'],
  },
  services: [
    {
      name: name + '.' + distro + '.com',
      image: platform_image(distro),
      privileged: true,
      entrypoint: ['/bin/sh', '-c', snapd_hold],
      volumes: [
        { name: 'dbus', path: '/var/run/dbus' },
        { name: 'dev', path: '/dev' },
      ],
    }
    for distro in distros
  ],
  volumes: [
    { name: 'dbus', host: { path: '/var/run/dbus' } },
    { name: 'dev', host: { path: '/dev' } },
    { name: 'shm', temp: { medium: 'memory', size_limit: '1GiB' } },
  ],
}];

build('amd64', true) +
build('arm64', false)
