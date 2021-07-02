# pyscript
An interpreted coding language in python. This is currently in development. 
PyScript is an untyped language like Python.

## Syntax <br />
#### Variables 
Variables are untyped, just like in Python. <br />
**Ex:** 
```
foo = 123
bar = 321
foo_bar = foo + bar
```
Referencing variables just involves writing the variable name. 
Of course, if the variable does not exist, there will be an error. 
<br /><br />
Variables can be "readonly", or cannot be changed once created. <br />
**Ex:**
```
readonly foo = 10
```

Assigning to a readonly variable should cause an `AssignmentError`.
```
readonly foo = 5
.
.
.
foo = 10
```
Should give:
```
AssignmentError: Editing readonly variable 'foo'
```

#### Types
1. Lists
1. Strings
1. Booleans
1. Integers and Floats<br />

**Strings** <br />
A *string* is anything that stores a text value. It can be defined using: <br/>
```
my_string = "Hello world!"
```
Note that (as of 27/6/2021) strings can only use double quotes.<br/><br/>

**Booleans** <br/>
A *boolean* is True or False. `True` and `False` (Capitalized) are the booleans:<br/>
```
a = True
b = False
```

The _boolean operators_ are `and`, `or`, `not`, and `xor`.<br/>
**AND**<br/>
| A     | B     | OUT   |
|-------|-------|-------|
| False | False | False |
| False | True  | False |
| True  | False | False |
| True  | True  | True  |
<br/>

**OR**<br/>
| A     | B     | OUT   |
|-------|-------|-------|
| False | False | False |
| False | True  | True  |
| True  | False | True  |
| True  | True  | True  |
<br/>

**XOR**<br/>
XOR stands for this or that, but not both.<br/>
| A     | B     | OUT   |
|-------|-------|-------|
| False | False | False |
| False | True  | True  |
| True  | False | True  |
| True  | True  | False |
<br/>

**NOT**<br/>
| A     | OUT   |
|-------|-------|
| False | True  |
| True  | False |
