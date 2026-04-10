from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def root():
    return {"message": "Hello, World!"} 

def gcd(x: int, y: int):
    while y != 0:
        x, y = y, x % y
    
    return x

@app.get("/serik_nuradil_gmail_com")
def calculate_lcm(x:int | None = None, y:int | None = None):
    if x is None or y is None or x < 0 or y < 0:
        return "NaN"
    
    if x == 0 or y == 0:
        return f"{0}"
    
    if (y % x == 0) or (x % y == 0):
        return f"{x}" if x > y else f"{y}"
    
    return f"{(x*y)/gcd(x,y)}"
            
    
    
    