#!/usr/bin/env python3

# Sample test generator

import sys,os,string
from random import seed, randint, sample

# first argument must be seed
seed(sys.argv[1])
MINN=int(sys.argv[2])
MAXN=int(sys.argv[3])
MINM=int(sys.argv[4])
MAXM=int(sys.argv[5])
MINS=int(sys.argv[6])
MAXS=int(sys.argv[7])

# safety
if MINM < 1:
    MINM = 1
if MAXM > 10000:
    MAXM = 10000

if MINS < 1:
    MINS = 1
if MAXS > 36:
    MAXN = 36

m = randint(MINM, MAXM)
if MAXN > m:
    MAXN = m
n = randint(MINN,MAXN)
s = randint(MINS,MAXS)

print(n)
print(m)
print(s)
