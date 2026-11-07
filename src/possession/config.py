"""Frozen production training parameters and local paths."""
from pathlib import Path
ROOT=Path('experiments/core-development')
DATA=Path('data/external')
CACHE=DATA/'prepared'
PARAMS=dict(iterations=300,depth=6,learning_rate=.05,l2_leaf_reg=3,random_seed=20261106,thread_count=1,loss_function='MultiClass',verbose=False,allow_writing_files=False)
