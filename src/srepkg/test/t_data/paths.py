from pathlib import Path


base = Path(__file__).parent.absolute()
setup_cfg_test_cases = base / 'setup_cfg_test_cases'

repackaging_components_actual = Path(__file__).parent.parent.parent.\
                                    absolute() / 'repackaging_components'
