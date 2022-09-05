from pathlib import Path
import srepkg.utils.lehs_caller as lc
import srepkg.logging_initializer as li


li.LoggingInitializer(
    logfile_dir=Path("/Users/duane/dproj/srepkg/src/srepkg/utils")
).setup()

lc.run_git_lehs()




