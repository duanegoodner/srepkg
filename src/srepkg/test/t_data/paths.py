from pathlib import Path


base = Path(__file__).parent.absolute()

repackaging_components_actual = Path(__file__).parent.parent.parent.\
                                    absolute() / 'repackaging_components'
