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
1. Integers and Floats<br />
