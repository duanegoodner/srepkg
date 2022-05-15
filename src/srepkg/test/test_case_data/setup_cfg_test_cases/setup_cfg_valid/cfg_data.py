import srepkg.shared_utils as su

pkg_name = 'goodpkg'
num_entry_pts = 2

entry_pts = [
    su.ep_console_script.parse_cs_line('goodpkg = goodpkg.goodpkg:main'),
    su.ep_console_script.parse_cs_line('goodtool = goodpkg.tool:atool')
]
