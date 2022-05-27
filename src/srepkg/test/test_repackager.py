import srepkg.repackager as repackager


# TODO patch builder paths calculator to

def test_howdoi_pypi():
    my_repackager = repackager.Repackager('howdoi', 'howdoipypi')
    my_repackager.repackage()


def test_howdoi_local():
    my_repackager = repackager.Repackager('howdoi', 'howdoilocal')
    my_repackager.repackage()


def test_howdoi_github():
    my_repackager = repackager.Repackager(
        'git+https://github.com/gleitz/howdoi',
        'howdoigithub')
    my_repackager.repackage()




