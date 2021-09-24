# calculates rankings for weapon
# to be used for weapons spreadsheet
# please import the csv output into the sheets file
# for pretty display


import "database/buff_dir.py"
import "database/lisa_stats.py"
import "database/team_data.py"
import "database/weap_dir.py"
import "active/artifact_optimizer.py"
import numpy as np
import sys

# the output file will look like:
# ===============================================
#
# ===============================================

playstyle_type = {
  "NAt" = 0,		# mv/s from NA
  "CAt" = 0,		# mv/s from CA	
  "Et" = 0,		# mv/s from E	
  "Qt" = 0,		# mv/s from Q
}

# ignore def and element shred because it benefits
# everything
stats = {
  "lv" = 0,		# Lisa lv
  "ATK" = 0,		# base attack
  "ATKb" = 0,		# attack bonus
  "EM" = 0,		# total EM
  "ER" = 0,		# total ER
  "particlet" = 0,	# particles per sec
  "incd" = 0,		# general increase dmg
  "incdNA" = 0,		# NA increase dmg
  "incdCA" = 0,		# CA increase dmg
  "incdE" = 0,		# E increase dmg
  "incdQ" = 0,		# Q increase dmg
  "tAA" = 0,		# talent AA
  "tE" = 0,		# talent E
  "tQ" = 0,		# talent Q
  "playstyle" = ""	# prefered playstyle, leave blank for optimal
}

# select lisa stats
# select weapon and refinement
# select playstyle or leave to be optimally chosen
# select buffs
# select artifact main stats and compute roll_caps

# run through optimizer

# dmg
