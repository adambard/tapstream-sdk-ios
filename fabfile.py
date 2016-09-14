import os.path
import plistlib
from fabric.api import lcd, local, task, execute


def sdk_version():
    with open('./tapstream-sdk-ios/Info.plist') as f:
        pl = plistlib.readPlist(f)
        return pl['CFBundleShortVersionString']


@task
def test():
    schemes = {
        'TapstreamIOS': [
            'iphonesimulator9.3'
        ],
        'TapstreamMac': [
            'macosx10.11'
        ]
    }

    local('pod update')
    local('pod install')
    for scheme, sdks in schemes.items():
        for sdk in sdks:
            local('xctool -scheme %s -workspace tapstream-sdk-ios.xcworkspace test -test-sdk %s' % (scheme, sdk))


@task
def package():
    execute(test)
    version = sdk_version()
    cmd = 'zip -D'
    ios_dest = os.path.abspath('./package/tapstream-sdk-ios-%s.zip' % version)
    mac_dest = os.path.abspath('./package/tapstream-sdk-mac-%s.zip' % version)

    if not os.path.exists('./package'):
        local('mkdir package')

    if os.path.exists(ios_dest):
        local('rm %s' % ios_dest)

    if os.path.exists(mac_dest):
        local('rm %s' % mac_dest)

    common_files = ['*.h',
                    '*.m']

    ios_only_files = ['**/*.h',
                      '**/*.m']

    with lcd('tapstream-sdk-ios'):
        for dir in common_files:
            local('%s %s %s' % (cmd, mac_dest, dir))
            local('%s %s %s' % (cmd, ios_dest, dir))

        for dir in ios_only_files:
            local('%s %s %s' % (cmd, ios_dest, dir))
