from socket import *
import math
import time
import sys
import vector


#sys.tracebacklimit=0

from bitstring import BitArray

def render(t,w,h):

    #ok no 3d.

    #ok separator is 4 thick,
    #so. I have a virtual screen 
    #and that gets translated back to the 
    #one I have.
    #so, I am artificially increasing the rows and then I delete rows... 8 ok 4 delete, 8 ok 4 delete.i
    screen=[]
    y=0
    my=int(h*1.5)
    mx=w*8

    rows=20

    r_base=int(my/2)
    thick=5
    #rotang=sin(t)
    t=t%(math.pi*2)
    f=36
    ang=(math.pi*2)*(1/f)
    rm=vector.RotationMatrix(ang,vector.Vector(0,0,1))

    #needs a different drawing function
    base=vector.Vector(1,0,0)

    myvectors={
            1:vector.Vector(-1,-0.5,0),
            2:vector.Vector(-1,-2,0),
            }

    myvectors={}
    vc=0
    vm=f
    currentv=base
    while vc < vm:
        myvectors[vc]=currentv
        currentv=rm*currentv
        vc+=1

    #what is the value of y at x and should I draw this?

    #=(v.y/v.x)*x-y
    cc=25,25

    cr1=abs(math.sin(t))*r_base
    cr2=abs(math.sin(t))*(r_base+thick)
    offset=vector.Vector(-mx/2,-my/2,0)

    while y<my:
        if y%12>7:
            y+=1
            continue
        screenline=[]
        x=0
        drawnids=[]
        while x<mx:
            val=0

            v=vector.Vector(x,y,0)
            v=v+offset

            m=v.magnitude()
            if cr1 < m < cr2:
                val=1
            val=0
            for vid in myvectors:
                if vid not in drawnids:
                    myv=myvectors[vid]
                    if myv.x!=0:
                        if (myv.y/myv.x)*x-y> 0:
                            drawnids.append(vid)
                            val=1
            screenline.append(val)
            x+=1
        screen.append(screenline)
        y+=1

    
    if False:

        #print("render",my,mx,my*mx)
        c=0
        m=500


        while c <500:

            cri=cr*math.sin(t)*10
            ang=(c/m)*2*math.pi
            px = 10+math.cos(ang)*cri
            py = 10+math.sin(ang)*cri
            px=int(round(px,0))
            py=int(round(px,0))
            screen[py][px]=1
            c+=1

    return screen

def makepacket(ti):
    myscreen,w,h = make_screen(ti)
    header = make_header(w,h)
    final = header + myscreen

    #print(final)
    #print("final length",len(final))
    return final

def make_header(w,h):
    mode="big"
    mode="little"
    cmd_bitmaplinear =  18 # 0x0012
    subcmd_bitmap = 0 # 0x0
    command = htons(cmd_bitmaplinear).to_bytes(3,mode)
    offset = (0).to_bytes(1,mode)

    #print("length pre conversion",w*h)

    length = htons(int(w*h)).to_bytes(3,mode)
    subcommand = htons(subcmd_bitmap).to_bytes(1,mode)
    reserved = (0).to_bytes(1,mode)

    # https://github.com/arfst23/ServicePoint
    #print(command)
    #print(offset)
    #print(length)
    #print(subcommand)
    #print(reserved)

    header=b""
    header+=command
    header+=offset
    header+=length
    header+=subcommand
    header+=reserved

    return header

def make_screen(ti):
    #htons dreht byte order um weil cpu braucht eine
    #network braucht die andere
    #define SP_TILE_SIZE 8
    #define SP_TILES_HORIZ 56
    #define SP_TILES_VERT 20
    #define SP_SEPARATOR_WIDTH 4                               #define SP_WIDTH (SP_TILES_HORIZ * SP_TILE_SIZE) // 448
    #define SP_HEIGHT (SP_TILES_VERT * SP_TILE_SIZE) // 160
    #define SP_HEIGHT_VIRT (SP_HEIGHT + (SP_TILES_VERT - 1)
 #* SP_SEPARATOR_WIDTH) // 236
    tilesize=8
    tiles_h=56
    tiles_v=20
    sep=4

    w = tiles_h * tilesize
    h = tiles_v * tilesize
  
    w = tiles_h
    
    myscreen = render(ti,w,h)
    mystring = ""
    for line in myscreen:
        for bit in line:
            mystring+=str(bit)

    screen = BitArray(bin=mystring)
    screen = screen.tobytes()
    return screen, w, h

def main():
    t0=time.time()
    myport = 2342
    ip="172.23.42.29"
    
    my_socket=socket(AF_INET,SOCK_DGRAM)
    address=(ip,myport)
    my_socket.bind(("",0))
    my_socket.setblocking(False)
    nasa=10000
    c=0
    fps=30

    while True and c <nasa:
        t1=time.time()
        ti=t1-t0
        packet=makepacket(ti)
        r=my_socket.sendto(packet,address)
        #print("success!") 

        if c%100==0:
            print("nasa c",c)   
        time.sleep(1/fps)

        c+=1


if __name__=="__main__":
    makepacket(0)
    main()
