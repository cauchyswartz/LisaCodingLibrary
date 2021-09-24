# optimizes artifacts per roll, not exact values
# e.g. a +20 artifact has 5 rolls total
# rolls are averaged, with data from 
# https://genshin-impact.fandom.com/wiki/Artifacts/Stats

# ===============================================
# how this works:
# ===============================================
# our damage equation will be a profit function
#   w(atk, er, cr, cd, em, incdmg, ...)
# specifically, it'll look something like
# w = f(atk, er, cr, incdmg...) +
# f(atk, er, cr, cd, incdmg, ...) + f(em, ...)


# in order to write this as a dynamic program,
# ie in order to make this problem decomposable,
# we'll split these into a three-level DP


# first level: will brute force search over # rolls
# into EM (Rolls_em) v. # rolls into everything else
# (Rolls_other)

# second level: DP will search over total number of rolls
# use (where the max #rolls is now Rolls_other) and 
# if we only measure dmg for stats up to
# 1:ATK%, 2:ER%, 3:CR+CD
# for a total of 3 stats

# third level: the calculation of rolls into CR
# and rolls into CD will be done with a 
# brute force search with function like
# (1 - CR) + CR(CD)


# Total runtime is o(max_rolls^2) cuz we do access in O(1)

# ===============================================


# ===============================================
# some extra things to be aware about
# ===============================================
# 1. substats cannot be rolled if its the same as main stat
# 2. This formulization only works for electro, anemo, and geo,
#    though you can reframe the em part to make it for others
# 3. also we only assume 5 star artifacts, for a total
#    of 5*5 = 25 rolls
# 4. this doesn't consider HP, DEF, or flat ATK because
#    we optimize for DPS
# ===============================================


# ===============================================
# Fact-checking:
# ===============================================
# This has been fact-checked by comparing results
# of

# ofc, any discovery of potential bugs is welcome
# plz dm me on LisaMains server at Patatartiner#5916
# ===============================================


# NOTICE: rolls_cap is not enabled. TODO

MAX_ROLLS=5
dp_stat_order = ["ATKb", "ERb", "CRCDb"]
max_num_stats = len(dp_stat_order)


# ------------------------------------------------
# create max_dmg/max_config arrays for fast access
# ------------------------------------------------
dp_statlv = [[(0,None) for i in range(max_num_stats+1)]
             for j in range(MAX_ROLLS+1)]

crcdlv = [(0, None) for j in range(MAX_ROLLS)]
# ------------------------------------------------


# ------------------------------------------------
# damage formulae
# ------------------------------------------------
def transformative_em_rolls_dmg(_rolls_em, _curr_stats):
  return _rolls_em*2-3

def atk_rolls_dmg(_rolls_atk, _curr_stats):
  return _rolls_atk*1.5

def er_rolls_dmg_multi(_rolls_er, _curr_stats):
  # returns damage for most optimal playstyle
  return _rolls_er+2

def crcd_rolls_dmg_calcd(_rolls, _curr_stats):
  return crcdlv[_rolls][0]

def crcd_rolls_dmg(_rolls_cr, _rolls_cd, _curr_stats):
  return (1-_rolls_cr)+(_rolls_cr)*(_rolls_cd)

stat_rolls_dmg = [atk_rolls_dmg, er_rolls_dmg_multi,
                  crcd_rolls_dmg_calcd]
# ------------------------------------------------

def artifact_optimizer_default(curr_stats,
                               roll_caps):
  return artifact_optimizerv0(MAX_ROLLS,
                              curr_stats,
                              roll_caps)


def artifact_optimizerv0(n_rolls_total,
                         curr_stats,
                         roll_caps):
  # fill out crcdlv
  for i in range(n_rolls_total):
    crcdlv[i] = third_level(i, curr_stats)

  # fill out dp_statlv
  second_level(n_rolls_total, curr_stats, 3)

  # compute first level
  best_dmg, best_dmg_config = first_level(n_rolls_total, curr_stats)
  
  return (best_dmg, best_dmg_config)


def first_level(max_rolls,
                curr_stats):
  curr_max_dmg = 1
  curr_max_config = None
  for i in range(max_rolls):
    other_dmg = dp_statlv[max_rolls-i][max_num_stats][0]
    transf_dmg = transformative_em_rolls_dmg(i, curr_stats)

    new_dmg = other_dmg + transf_dmg
    if (curr_max_dmg < new_dmg):
      curr_max_dmg = new_dmg
      curr_max_config = i
  return (curr_max_dmg, curr_max_config)

def print_dp_statlv():
  for i in dp_statlv:
    print(i)

def second_level(rolls_used, curr_stats,
                 num_calc_stats,
                 rolls_cap=None,
                 max_rolls=MAX_ROLLS):

  print_dp_statlv()

  ncs = num_calc_stats
  stat_i = num_calc_stats - 1 # sorry indexing is weird
  prev_calc = num_calc_stats - 1
  tmp_stat_i_config = 0


  print("rolls used ", rolls_used, " ncs ", ncs)
  if (dp_statlv[rolls_used][ncs][1] is not None):
    return dp_statlv[rolls_used][ncs]

  curr_max_dmg = 1
  curr_max_config = [0,0,0]

  # base cases (1,[0,0,0])
  if(num_calc_stats == 0): return (curr_max_dmg, curr_max_config)
  if(rolls_used == 0): return (curr_max_dmg, curr_max_config)

  for i in range(rolls_used):
    stat_dmg, stat_config = second_level(rolls_used-i,
                                         curr_stats,
                                         prev_calc,
                                         rolls_cap, max_rolls)

    new_dmg = stat_dmg
    new_dmg *= stat_rolls_dmg[stat_i](tmp_stat_i_config, curr_stats)
    if (new_dmg > curr_max_dmg):
      curr_max_dmg = new_dmg
      curr_max_config = stat_config
      curr_max_config[stat_i] = tmp_stat_i_config

    tmp_stat_i_config += 1

  dp_statlv[rolls_used][ncs] = (curr_max_dmg, curr_max_config)
  return dp_statlv[rolls_used][ncs]


def third_level(rolls_used, curr_stats,
                rolls_cap=None):
  curr_max_dmg = 1
  curr_max_config = None
  for i in range(rolls_used):
    new_dmg = crcd_rolls_dmg(i,rolls_used-i,curr_stats)
    if (curr_max_dmg < new_dmg):
      curr_max_dmg = new_dmg
      curr_max_config = i
  return (curr_max_dmg, curr_max_config)
