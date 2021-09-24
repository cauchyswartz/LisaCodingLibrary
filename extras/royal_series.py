#!/bin/bash/python
import numpy as np
import numpy.linalg as la
import scipy.linalg as spla

# =====================================================
# params
# =====================================================

x = [0.08, 0.16, 0.24, 0.32, 0.4, 0.48]	# crit rate without royal stacks
b = [0.08]	# royal stack +critrate% (+2% per refinement)

# to limit the number of states, pretend that if
# the probability that we didn't get a crit after n
# is <= tol, it means we automatically get a crit
# (most game code is developed with this type of
# pseudorng anyways)

tol = 0.01

def get_n(tol, x, b):
    n = 0
    p_notcrit = 1
    while (p_notcrit > tol):
        n+=1
        if (n<=5): p_notcrit *= (1-n*b-x)
        else: p_notcrit *= (1-5*b-x)
    return n

# =====================================================
# building state machine
# =====================================================
# state machine has n states:
# state 0 represents crit rate of x
# state 1 represents crit rate of x+b
# etc until state 5, with rate of x*5+b
# then we have states 5..n-2 which are placeholder states
# until we reach state n-1 where we have a guaranteed crit
# if at a state s we crit w prob p then we return to state
# 0 with prob p and we move onto the next state s+1 with
# prob 1-p. The only state with one transition is state n-1,
# which goes to state 0 w prob 1
# =====================================================

def state_machine(x, b,n):
    A = np.zeros((n,n))
    
    for i in range(min(5,n-1)):
        A[i,0]=x+i*b # got crit transition
        A[i,i+1]=1-(x+i*b) # didnt get crit transition
    
    if (n-1>5):
        for i in range(5,n-1):
            A[i,0]=x+5*b
            A[i,i+1]=1-(x+5*b)
    
    A[n-1,0] = 1  # guaranteed crit transition
    return A

# =====================================================
# transition matrix w/o cr pity
# =====================================================
def state_machine_nopity(x, b):
    if (b != 0): n = min(6,1+int((1-x)/b))
    else: n = 6
    A = np.zeros((n,n))
    
    for i in range(n-1):
        A[i,0]=min(1,x+i*b) # got crit transition
        A[i,i+1]=max(0,1-(x+i*b)) # didnt get crit transition
    A[n-1,0]=min(1,x+5*b) # got crit transition
    A[n-1,n-1]=max(0,1-(x+5*b)) # didnt get crit transition
    return A


# =====================================================
# figuring out royal set in terms of one time +cr stat
# =====================================================
# find left eigenvector of the state machine of the
# max eigenvalue. This is the stationary distribution, e.g.
# the probability u are at the state if u were to use
# royal weapon infinite times and average them.
# then multiply eigenvector by crit rate at each state
# in order to find equivalence of royal set mechanic
# to a one time +cr stat

def find_cr(A, x, b, n=6, ifpity=True, calc_probs=False):
    eigval, eigvec = spla.eig(A, left=True, right=False)
    max_id = np.argmax(eigval)
    #print("\n\n")
    #print(eigval[max_id])
    #print(-eigvec[:, max_id] @ A)

    if (ifpity):
        cr_probs = np.array([min(x+5*b,x+i*b) for i in range(n)])
        cr_probs[-1] = 1

    else:
        if (b != 0): n = min(6,1+int((1-x)/b))
        else: n = 6
        cr_probs = np.array([min(1,x+i*b) for i in range(n)])


    e = eigvec[:,max_id]/np.sum(eigvec[:, max_id])
    #print(np.complex(e))

    # extra calculation for me
    if (calc_probs):
        _n = min(n,6)
        probs = np.zeros(_n)
        probs[:_n-1] = e[:_n-1]
        probs[_n-1] = np.sum(e[_n-1:])
        print("prob of having 0,1,2,3,4,etc stacks: ", np.abs(np.real(probs)))

    #print("\n\n")
    #print(cr_probs)

    # if the eigenvector is negative just make it positive
    # because the positive version is still an eigenvector

    cr = np.abs(np.dot(e, cr_probs))
    return cr

def main():
    print("\nignore complex warnings, only real numbers in solutions\n")
    for _x in x:
        for _b in b:
            _n = get_n(tol,_x,_b)
            _A = state_machine(_x,_b,_n)
            _B = state_machine(_x, 0,_n)
            cr = find_cr(_A, _x, _b, _n, calc_probs=True)
            base_cr = find_cr(_B, _x, 0, _n)

            print("for base crit: "+str(_x)+ " with stack bonus: "+str(_b),
                  " avg cr inc is "+str(cr-base_cr))
            print(" where base effective cr with cr pity is "+str(base_cr),
                  " and effective cr w royal and pity: "+str(cr)+"\n")

            _C = state_machine_nopity(_x, _b)
            cr_nopity = find_cr(_C, _x, _b, ifpity=False, calc_probs=True)

            # check math
            _D = state_machine_nopity(_x, 0)
            base_cr_nopity = find_cr(_D, _x, 0, ifpity=False)
            assert(np.abs(base_cr_nopity - _x) <= 1e-4)

            print("for base crit: "+str(_x)+ " with stack bonus: "+str(_b),
                  " no cr pity, avg cr inc is "+str(cr_nopity-_x))
            print(" where base effective cr w/o cr pity is "+str(_x),
                  " and effective cr w royal and no pity: "+str(cr_nopity))
            print("========================================")

if __name__ == "__main__":
    main()
