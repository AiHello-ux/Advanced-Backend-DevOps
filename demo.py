from pydantic import BaseModel, ValidationError

# 1. Describe what a valid User looks like
class User(BaseModel):
    name: str
    age: int

# 2. Good data works
user = User(name="Ana", age=30)
print(user)          # name='Ana' age=30

# 3. It auto-converts when it makes sense
user2 = User(name="Ben", age="25")   # age is text here
print(user2.age + 1)                 # 26 (it became a number!)

# 4. Bad data is rejected with a clear error
try:
    User(name="Cara", age="abc")
except ValidationError as e:
    print(e)