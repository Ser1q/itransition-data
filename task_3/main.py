from fastapi import FastAPI
from fastapi.responses import PlainTextResponse

app = FastAPI()

@app.get("/")
def root():
    return {"message": "Hello, World!"} 

def gcd(x: int, y: int):
    while y != 0:
        x, y = y, x % y
    
    return x

@app.get("/serik_nuradil_gmail_com")
def calculate_lcm(x:str = "", y:str = ""):
    
    try:
        xi = int(x)
        yi = int(y)
        
        if xi <= 0 or yi <= 0:
            return PlainTextResponse("NaN")
    except(ValueError, TypeError):
        return PlainTextResponse("NaN")
    
    
    # if x == 0 or y == 0:
    #     return f"{0}"
    
    if (yi % xi == 0) or (xi % yi == 0):
        return f"{xi}" if xi > yi else f"{y}"
    
    return PlainTextResponse(f"{(xi*yi)//gcd(xi,yi)}")
            
    
    
    