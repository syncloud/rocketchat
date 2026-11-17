DAEMONS = ['mongodb', 'server']


def restarts(device, app):
    return {
        daemon: device.run_ssh('systemctl show -p NRestarts --value snap.{0}.{1}.service'.format(app, daemon)).strip()
        for daemon in DAEMONS
    }


def assert_no_restarts(device, app):
    counts = restarts(device, app)
    assert counts == {daemon: '0' for daemon in DAEMONS}, counts
