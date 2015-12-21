import math

def nCr(n,r):
    f = math.factorial
    return f(n) / f(r) / f(n-r)

prob = 10.0/22.0
neg_prob = 1 - prob


for num_l in range(0, 1000):
    half = int(math.ceil(num_l/2.0))
    running_sum = 0.0
    for i in range(half, num_l + 1):
        running_sum += math.pow(prob,i) * math.pow(neg_prob,num_l-i) * nCr(num_l,i)
    print num_l
    print running_sum
