# rucksack: A place to store your useful one liners

## Overview

Rucksack is a 

It gives you a way to store your one-liners (along with their arguments)

It was inspired by that `useful_stuff.txt` file that every SysAdmin has on their desktop. You know the one: you come up with a clever one-liner, and you throw it in there so that you can reuse it someday.

What can 


A simple one-liner:

```
$ cat rucksack.yml
system:
  get-uptime:
    command: uptime
```

TODO: gif

```
system:
  get-uptime:
    command: uptime
  performance:
    get-basic-info:
      command: "uptime && echo && free -h && echo && df -h"
```

TODO: gif


A more advanced command with some options:

```
system:
...
  tail-log:
    command: "tail {{ log_file }}"
    args:
      - num_lines:
         arg_string: -n {{ num_lines }}
      - log_file:
          mandatory: True
          values:
            - /var/log/syslog
            - /var/log/kern.log
            - /var/log/auth.log
```

TODO: gif

More advanced, with the template variables embedded:

```
system:
  disk-usage:
    get-largest-files:
      command: du -h -d {{ depth }} {{ directory }} 2>/dev/null | sort -hr | head -n 10
      args:
        - depth:
            mandatory: True
        - directory:
            mandatory: True
            values:
              - /
              - /home
              - /var
```


A really advanced one-liner that dynamically provides argument options by executing another command:

```
nginx:
  get-top-5-ips:
    command: "sudo cat {{ log_file }} 2>/dev/null | cut -f 1 -d ' ' | sort | uniq -c | sort -hr | head -n 5"
    args:
      - log_file:
          mandatory: True
          from_command: "sudo find /var/log/nginx -name '*access.log*' | grep -v '.gz'"
```

TODO:

## Installing

## Configuring

Need to cover:

* Config file locations
* Syntax
* A tutorial to add some commands

## Logging

Log to a file whenever possible, especially for the completer (which will otherwise make the tool impossible to use).
