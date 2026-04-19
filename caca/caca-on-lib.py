import libcaca

# load caca program
cf = open("this.cns")
caca = cf.read().splitlines()

line = 0 # set line number
stack = [0]
selnum = 0

ittcap = 0 # maximum itterations
itt = 0

while len(caca) > line:
     inst = caca[line]
     line, stack, selnum, out = libcaca.interp(inst, line, stack, selnum, caca)
     print(out, end='')
     line += 1
     itt += 1
     if ittcap:
         if itt > ittcap:
             print(f"\n itteration cap of {ittcap} exceeded!")
             break

print(f"\nFinal State: {stack}@#{selnum}")
