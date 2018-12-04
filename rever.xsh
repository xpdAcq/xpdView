$PROJECT = 'xpdview'
$ACTIVITIES = ['version_bump',
               'changelog',
               'tag',
               'push_tag',
               'ghrelease',
               'conda_forge',
]

$VERSION_BUMP_PATTERNS = [
    ($PROJECT + '/__init__.py', '__version__\s*=.*', "__version__ = '$VERSION'"),
    ('setup.py', 'version\s*=.*,', "version='$VERSION',")
    ]
$CHANGELOG_FILENAME = 'CHANGELOG.rst'
$CHANGELOG_IGNORE = ['TEMPLATE']

$GITHUB_ORG = 'xpdAcq'
$GITHUB_REPO = $PROJECT
$TAG_REMOTE = 'git@github.com:xpdAcq/xpdView.git'

$LICENSE_URL = 'https://github.com/{}/{}/blob/master/LICENSE'.format($GITHUB_ORG, $GITHUB_REPO)

from urllib.request import urlopen
rns = urlopen('https://raw.githubusercontent.com/xpdAcq/mission-control/master/tools/release_not_stub.md').read().decode('utf-8')
$GHRELEASE_PREPEND = rns.format($LICENSE_URL, $PROJECT.lower())

