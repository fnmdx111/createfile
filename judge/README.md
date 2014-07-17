
Rule Definition and Application for createfile
====

This module implements a DSL (domain specific language) for users to define
whatever rules they want.

Introduction
----
There's 2 fundamental elements of this module:
* the underscore object (`_`) which in the DSL represents for any random file
entries;
* the If (Rule) class which defines the rules.

Examples
----
See [this gist](https://gist.github.com/mad4alcohol/dbbe26984fe5536b5aaf ).

If we have the following rule:

    For any random file, if its creation time is greater than 10 or its
    modification time is less than 5 or its last cluster number is bigger
    than 100, then it's a xxx file.

We can write:
```python
rule = If(_.create_time > 10
        | _.modify_time < 5
        | _.cluster_list[-1][-1] > 100).then(conclusion='xxx')

print(rule.apply(entry))
```

