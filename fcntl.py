def fcntl(fd, op, arg=0):
    return 0
        
def ioctl(fd, op, arg=0, mutable_flag=True):
    if mutable_flag:
        return 0
    else:
        return ""
    
def flock(fd, op):
    return
        
def lockf(fd, operation, length=0, start=0, whence=0):
    return

def LOCK_SH(fd, operation, length=0, start=0, whence=0):
    return

def LOCK_UN(fd, operation, length=0, start=0, whence=0):
    return

def LOCK_EX(fd, operation, length=0, start=0, whence=0):
    return