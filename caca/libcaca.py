def interp(inst: str, line: int, stack: list, selnum: int, caca: list, inp: int = None):
     out = ""
     if inst in ("icaca", "out"):
         cha = chr(stack[selnum])
         out = cha
     elif inst in ("icacac", "inc"):
         stack[selnum] += 1

     elif inst in ("icac", "dec"):
         stack[selnum] -= 1

     elif inst[:6] in ("cacaca", "repeat"):
         count = int(inst[6:])
         # print(f"DEBUG: REPEATING INSTRUCTION {caca[line+1]} {count} TIMES")
         for _ in range(0, count-1):
             interp(caca[line+1], line, stack, selnum, caca, inp)

     elif inst in ("icacan", "sq"):
         stack[selnum] = stack[selnum] ** 2

     elif inst in ("youcaca", "input"):
         if inp is None:
             y = True
             while y == True:
                 inp = input("?")
                 try:
                     inp = int(inp);
                     y = False
                 except:
                     print("Not a number, try again")
         stack[selnum] += inp

     elif inst.startswith("cacato") or inst.startswith("goto"):
         count = int(inst.replace("cacato", '').replace("goto", ''))
         line = count - 2 # minus 1 because internal indexing is at 0, and the linecount always increments after a interp()

     elif inst in ("nocaca", "prev"):
         selnum -= 1
         if selnum == -1:
             selnum = len(stack)-1

     elif inst in ("yescaca", "next"):
         selnum += 1
         if selnum == len(stack):
             selnum = 0

     elif inst in ("newcaca", "newcaca"):
         stack.append(0)

     elif inst in ("icaca?", "ifp"):
         if not stack[selnum] > 0:
             line += 1

     elif inst in ("nocaca?", "ifn"):
         if not stack[selnum] < 0:
             line += 1

     elif inst in ("zecaca?", "ifz"):
         if not stack[selnum] == 0:
             line += 1

     elif inst in ("cacacaca", "copy"):
         stack.append(stack[selnum])

     else:
         out+=("INVALID INSTRUCTION: "+inst)

     return line, stack, selnum, out
