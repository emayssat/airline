# Airline coding challenge

## Getting started

For this small project, we used the 'make' utility as a meta command line.
To see the command that is going to be executed, simply run for the intended target

```
make -n [target]
```

For this program to properly work, you need install Python dependencies

```
make -n install_module
make install_module
```

## Running using the command line

You can also use more advanced commands
```
export AIRLINE_NAME='American Airline'

./cli.py LIST
./cli.py ADD AIRPLANE_001

export AIRPLANE_NAME=AIRPLANE_001
./cli.py BOOK D2 3
./cli.py CANCEL D2 3
```

A simpler alternative is the following

```
make run
```


## Testing

This project is using extensive doctest tests. To run them, do the following:
```
make -n test
make test
```

## Debugging and troubleshooting

To better understand the code, you may way to run the CLI in DEBUG mode

```
export DEBUG=True
./cli.py  ...
```

To get out of the debugging mode, simply uset the environment variable

```
unset DEBUG
```

## God mode

```
DEBUG=True make __DOCTEST_OPTS=-v
```

Enjoy!