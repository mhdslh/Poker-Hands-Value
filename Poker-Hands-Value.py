
# -*- coding: utf-8 -*-
"""
Created on Thu Jan 30 17:18:14 2020

@author: Mohammad
"""
import numpy as np
import random
from collections import Counter
from multiprocessing import Process
import time

Cards = [0]*52
c = 0
for i in [2,3,4,5,6,7,8,9,10,"J","Q","K","A"]:
    Cards[c] = (i,"Hearts")
    Cards[c+1] = (i,"Diamonds")
    Cards[c+2] = (i,"Spades")
    Cards[c+3] = (i,"Clubs")
    c += 4

def shuffle(exclude,Cards): 
    Shuffled_Cards = Cards[:]
    for i in range(len(exclude)):
        Shuffled_Cards.remove( exclude[i] ) 
    random.shuffle(Shuffled_Cards)
    return Shuffled_Cards

def deal(n, exclude, Shuffled_Cards):
    Hands = {}
    Hands["Player" + str(1)] = exclude
    k = 0
    for i in range(2,n+1):
        Hands["Player" + str(i)] = [ Shuffled_Cards[k],  Shuffled_Cards[k+n-1] ]
        k += 1
    flop = [ Shuffled_Cards[2*n-1], Shuffled_Cards[2*n], Shuffled_Cards[2*n+1] ]
    turn = [ Shuffled_Cards[2*n+3] ] 
    river = [ Shuffled_Cards[2*n+5] ]
    return Hands, flop, turn, river

def Sort_Cards(List_of_numbers): 
    # From high to low
    number = List_of_numbers[:]
    s = [0] * len(number)
    ind = 0
    for n in ["A","K","Q","J",10,9,8,7,6,5,4,3,2]:
        while n in number:
            s[ind] = n
            number.remove(n)
            ind += 1
    return s
    
def Texas_Holdem_Hands(Hands, flop, turn, river):
    Flag = [1,0,0,0,0,0,0,0,0,0]
    H = ["High Cards","Pair","Two Pair","Three of a Kind", \
         "Straight","Flush","Full House","Four of a Kind", \
         "Straight Flush","Royal Flush"]
    W = {"High Cards":[], "Pair":[], "Two Pair":[], "Three of a Kind":[], \
         "Straight":[], "Flush":[], "Full House":[], "Four of a Kind":[], \
         "Straight Flush":[], "Royal Flush":[]}
    Cards = Hands + flop + turn + river
    n = [ i[0] for i in Cards ]
    s = [ i[1] for i in Cards ]
    c = Counter(n)
    k = list( c.keys() )
    v = list( c.values() ) 
    n_2 = 0
    n_3 = 0
    n_4 = 0
    for i in v:
        n_2 += int(i==2)
        n_3 += int(i==3)
        n_4 += int(i==4)
    n_Hearts = 0
    n_Diamonds = 0
    n_Spades = 0
    n_Clubs = 0
    for i in s:
        n_Hearts += int(i=="Hearts")
        n_Diamonds += int(i=="Diamonds")
        n_Spades += int(i=="Spades")
        n_Clubs += int(i=="Clubs")    
    W["High Cards"] = Sort_Cards(n)[0:5]
    if (n_2==1) and (n_3==0) and (n_4==0):
        Flag[1] = 1 # Pair
        B = [k[ind] for ind, i in enumerate(v) if i==2]
        W["Pair"] = [B[0], B[0]]
    if (n_2>1) and (n_3==0):
        Flag[2] = 1 # Two Pair
        B = [k[ind] for ind, i in enumerate(v) if i==2]
        B = Sort_Cards(B)
        W["Two Pair"] = [B[0], B[0], B[1], B[1]] 
    if (n_2==0) and (n_3==1) and (n_4==0):
        Flag[3] = 1 # Three of a kind
        B = [k[ind] for ind, i in enumerate(v) if i==3] 
        W["Three of a Kind"] = [B[0], B[0], B[0]]
    if (n_2>=1) and (n_3==1):
        Flag[6] = 1 # Full House
        B_2 = [k[ind] for ind, i in enumerate(v) if i==2]
        B_3 = [k[ind] for ind, i in enumerate(v) if i==3]
        B_2 = Sort_Cards(B_2)
        W["Full House"] = [B_3[0], B_3[0], B_3[0], B_2[0], B_2[0]]  
    if n_3==2 :
        Flag[6] = 1 # Full House
        B_3 = [k[ind] for ind, i in enumerate(v) if i==3]   
        B_3 = Sort_Cards(B_3)
        W["Full House"] = [B_3[0], B_3[0], B_3[0], B_3[1], B_3[1]]
    if (n_4==1):
        Flag[7] = 1 # Four of a Kind
        B = [k[ind] for ind, i in enumerate(v) if i==4]
        W["Four of a Kind"] = [B[0], B[0], B[0], B[0]]
        
    B = []
    if max(n_Hearts,n_Diamonds,n_Spades,n_Clubs)>=5:
        Flag[5] = 1 # Flush
        s_star = np.argmax([n_Hearts,n_Diamonds,n_Spades,n_Clubs])
        s_star = "Hearts"*(int(s_star==0)) + "Diamonds"*(int(s_star==1)) + "Spades"*(int(s_star==2)) + "Clubs"*(int(s_star==3))
        B.extend([ n[ind] for ind, i in enumerate(s) if i==s_star])
        W["Flush"] = Sort_Cards( B[0:5] )
        
    convert_n = n[:]
    for ind, i in enumerate(convert_n):
        if i in ["A","K","Q","J"]:
            convert_n[ind] = 14*(i=="A") + 13*(i=="K") + 12*(i=="Q") + 11*(i=="J")
            if i=="A":
                convert_n.extend([1])
    convert_n = list( dict.fromkeys(convert_n) )
    convert_n.sort()
    temp = list( np.diff(convert_n) )
    L = len(temp)
    if L>=4:
        for i in range(L-4+1):
            if temp[i:i+4]==[1,1,1,1]:
                Flag[4] = 1 # Straight
                b = convert_n[i+4]
    if Flag[4] == 1:
        B = [b,b-1,b-2,b-3,b-4]
        for ind, i in enumerate(B):
            if i in [14,13,12,11]:
                B[ind] = "A"*(i==14) + "K"*(i==13) + "Q"*(i==12) + "J"*(i==11)
        W["Straight"] = B
        n_H = 0
        n_D = 0
        n_S = 0
        n_C = 0
        for ind, i in enumerate(n):
            if i in B:
                n_H += int(s[ind]=="Hearts")
                n_D += int(s[ind]=="Diamonds")
                n_S += int(s[ind]=="Spades")
                n_C += int(s[ind]=="Clubs")
        if max(n_H,n_D,n_S,n_C)>=5:
            Flag[8] = 1 # Straight Flush
            W["Straight Flush"] = B
            if B[0]=="A":
                Flag[9] = 1 # Royal Flush
                W["Royal Flush"] = B
    
    F = [ind for ind, i in enumerate(Flag) if i==1]
    F_star = F[-1]
    H_star = H[F_star]
    W_star = W[H_star][:]
    
    temp1 = W["High Cards"][:]
    temp2 = W_star[:]
    for w in temp1:
        if w in temp2: 
            temp2.remove(w)
        else: 
            W_star.extend([w])            
    W_star = W_star[0:5]
    return F_star, H_star, W_star

def Convert(List_of_numbers): 
    convert_n = List_of_numbers[:]
    for ind, i in enumerate(convert_n):
        if i in ["A","K","Q","J"]:
            convert_n[ind] = 14*(i=="A") + 13*(i=="K") + 12*(i=="Q") + 11*(i=="J")
    return convert_n

def Winner(Set_F_star,Set_W_star):  
    n = len(Set_W_star)
    MAT_W = np.zeros((n,5))
    for i in range(n):
        MAT_W[i,:] = Convert( Set_W_star[i] )  
    
    F = np.max(Set_F_star)
    W = [ind for ind, i in enumerate(Set_F_star) if i==F]
    
    i = 0
    while (len(W)>1) and (i<5): 
        temp = np.zeros((n,5))
        temp[W,:] = MAT_W[W,:]
        W = [ind for ind, j in enumerate(temp[:,i]) if j==np.max(temp[:,i]) ]
        i += 1
    return list(np.array(W)+1)

def episode(n_players,exclude,cards):
    Shuffled = shuffle(exclude,cards)
    Hands, flop, turn, river = deal(n_players, exclude, Shuffled)
    Set_F_star = [0] * n_players
    Set_H_star = [0] * n_players
    Set_W_star = [0] * n_players
    for i in range(n_players):
        Set_F_star[i], Set_H_star[i], Set_W_star[i] = Texas_Holdem_Hands(Hands["Player" + str(i+1)], flop, turn, river)
    Set_Winners = Winner(Set_F_star,Set_W_star)
    # print("done") 
    return Set_Winners, Set_H_star, Set_W_star, Hands, flop, turn, river
    
# start = time.perf_counter() 
   
exclude = [("A","Clubs"),("A","Hearts")]
n_players = 5 
iteration = 100000
Pr_win = 0
processes = []
for ii in range(iteration):
    if (ii%1000 == 0) : print(ii)
    # process = Process(target=episode, args=(n_players,exclude,Cards) )
    # processes.append(process)
    # process.start()
    # process.join()
    Set_Winners, Set_H_star, Set_W_star, Hands, flop, turn, river = episode(n_players,exclude,Cards)
    Pr_win += int(1 in Set_Winners)/iteration
    # print(Hands, flop, turn, river, Set_H_star, Set_Winners)

    
finish = time.perf_counter()
    
print(Pr_win)
# print(f"{finish-start} sec" )
