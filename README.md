# Ne0giLang
Ne0giLang is a dynamically typed, interpreted programming language basically created for fun and understanding of how interpreters work in general. Several compiler design techniques and principles have been used in the process. The language is still in development so things can break unexpectedly.

## Table of Contents
- [Installation](#installation)
- [Execution](#execution)
- [Quick Example](#quick-example)
- [Comments](#comments)
- [Data Types](#data-types)
- [Operators](#operators)
  - [Arithmetic Operators](#arithmetic-operators)
  - [Logical Operators](#logical-operators)
  - [Bitwise Operators](#bitwise-operators)
  - [Conditional Operators](#conditional-operators)
- [Variables](#variables)
- [Assignment](#assignment)
- [Control Flow](#control-flow)
  - [If-Else](#if-else)
  - [While](#while)
  - [For](#for)
- [Functions](#functions)
- [Classes](#classes)
- [Built-in Functions](#built-in-functions)

## Installation
Python 3.10 or higher is required.
```bash
$ git clone https://github.com/J16N/ne0giLang.git   
$ cd ne0giLang
```

## Execution
For windows use `python` instead of `python3`. Ne0giLang supports python/node.js like REPL. So you can play and try out various commands right away. You can also provide a file with extension `.ne` or `.ne0gi` in the argument.
```
$ python3 main.py
```
OR
```
$ python3 main.py [your_file]
```

## Quick Example
```rs
/**
 * Title: Quick Example
 * Description: Calculate n-th Fibonacci number.
 */
 
fn fib(n) {
    if (n < 2) return n;
    let a = 0, b = 1;
    for (let i = 2; i <= n; ++i) {
        let c = a + b;
        a = b;
        b = c;
    }
    return b;
}

print(fib(4));
```

## Comments
Ne0giLang supports both single line and multi-line comments. Single line comments start with `//` and multi-line comments are enclosed between `/*` and `*/`.

```js
// This is a single line comment

/*
    This is a multi-line comment.
    It can span multiple lines.
*/
```

## Data Types
Ne0giLang supports the following primitive data types:

  + String
    ```js
    "Hello, World!"
    ```

  + Integer
    ```js
    10
    ```

  + Float
    ```js
    10.5
    ```

## Operators
Like most other languages, Ne0giLang supports:  

### Arithmetic Operators  

  + Plus (`a + b`)
    ```java
    > print(1 + 2)
    3
    ```
    The `plus` operator is overloaded, so it works both with strings and integers. The concatenation also closely follow what Java does. When any of the operand is string then the other operator is converted to string and concatenated.

  + Minus (`a - b`)
    ```java
    > print(1 - 2)
    -1
    ```

  + Multiplication (`a * b`)
    ```java
    > print(3 * 3)
    9
    ```

  + Exponentiation (`a ** b`)
    ```java
    > print(5 * 2)
    25
    ```

  + Division (`a / b`)
    ```java
    > print(7 / 2)
    3.5
    ```

  + Modulo (`a % b`)
    ```java
    > print(3 % 2)
    1
    ```

### Logical Operators  

  All values except `0`, `false`, `""` and `nil` are considered `true`. Short-circuit evaluation is always performed. The result of short-circuiting is always the last value evaluated.

  * And (`a && b`)
    ```java
    > print(true && false)
    false
    ```

  * Or (`a || b`)
    ```java
    > print(true || false)
    true
    ```

  * Not (`!a`)
    ```java
    > print(!true)
    false
    ```

### Bitwise Operators

  * Xor (`a ^ b`)
    ```java
    > print(1 ^ 2)
    3
    ```

  * Bitwise-and (`a & b`)
    ```java
    > print(1 & 2)
    0
    ```

  * Bitwise-or (`a | b`)
    ```java
    > print(5 | 9)
    13
    ```

  * Left Shift (`a << b`)
    ```java
    > print(1 << 2)
    4
    ```

  * Right Shift (`a >> b`)
    ```java
    > print(4 >> 2)
    1
    ```

### Conditional Operators

  * Greater than (`a > b`)
    ```java
    > print(1 > 2)
    false
    ```

  * Lesser than (`a < b`)
    ```java
    > print(1 < 2)
    true
    ```

  * Equality (`a == b`)
    ```java
    > print(1 == 2)
    false
    ```

  * Ternary Operator (`a ? b : c`)
    ```java
    > print(1 > 2 ? "Hello" : "World")
    World
    ```

## Variables
Variables in Ne0giLang are declared by the `let` keyword.
```js
let myString, myNumber;
myString = "Hello";
myNumber = 10;
```

The assignment and declaration can be done in a single statement as:
```js
let myString = "Hello", myNumber = 10;
```

## Assignment
Since Ne0giLang is dynamically typed, the type of the variable is inferred from the value assigned to it. The type of the variable can be changed later on.
```js
let a = 10;
a = "Hello";
```

The shorthand assignment operators for all the binary operators are also supported.
```js
let a = 2;

a +=  10;    // a = a + 10
a -=  10;    // a = a - 10
a *=  10;    // a = a * 10
a /=  10;    // a = a / 10
a %=  10;    // a = a % 10
a &=  10;    // a = a & 10
a |=  10;    // a = a | 10
a ^=  10;    // a = a ^ 10
a <<= 10;    // a = a << 10
a >>= 10;    // a = a >> 10
```

C like increment and decrement operators are also supported. The operators can be used both as prefix and postfix.
```js
let a = 10;
++a;    // a = 11
--a;    // a = 10

a++;    // a = 11
a--;    // a = 10
```

## Control Flow
Ne0giLang supports the following control flow statements:

### If-Else
```js
if (condition) {
    // do something
} else if (condition) {
    // do something
} else {
    // do something
}
```

### While Loop
```js
while (condition) {
    // do something
}
```

### For Loop
```js
for (let i = 0; i < 10; ++i) {
    // do something
}
```

In case of loops, the `break` and `continue` statements are also supported.
```js
for (let i = 0; i < 10; ++i) {
    if (i == 5) {
        break;
    }
    if (i == 3) {
        continue;
    }
    print(i);
}
```

## Functions
Functions in Ne0giLang are declared using the `fn` keyword. The return type of the function is inferred from the return value. If the `return` is not specified, then the function returns `nil`.
```js
fn sum(a, b) {
  return a + b;
}
```

Ne0giLang also supports anonymous functions.
```js
let sum = fn(a, b) {
  return a + b;
}
```

## Classes
In Ne0giLang, classes are declared using the `class` keyword. The class can have instance methods for now. The instance methods can access the instance variables using the `this` keyword. The constructor of the `class` must have the same name as the `class` itself.
```js
class Person {
  Person(name) {
    this.name = name;
  }

  getName() {
    return this.name;
  }
}

let person = Person("Bishakh Ne0gi");
print(person.getName());
```

Ne0giLang also supports single inheritance. The `<` keyword is used to inherit from a class. The `super` keyword is used to access the methods of the parent class. The `super()` method is used to call the parent constructor. The constructor of the child class must call the parent constructor using `super()` before doing anything else.
```js
class Person {
  Person(name) {
    this.name = name;
  }

  getName() {
    return this.name;
  }
}

class Student < Person {
  Student(name, roll) {
    super(name);
    this.roll = roll;
  }

  getRoll() {
    return this.roll;
  }
}

let student = Student("Bishakh Ne0gi", 1);
print(student.getName());
print(student.getRoll());
```

## Built-in Functions
Ne0giLang has the following built-in functions as of now:

### `print(args)`
The `print` function is used to print the value of the expression passed to it.
```py
print("Hello World");
```

### `clock()`
The `clock` function returns the number of seconds elapsed since the epoch.
```py
print(clock());
```