# What is this?

This repository contains code to support analysing usage of static variables in CPython.

# Why is that needed?

Static variables are defined all over the place in CPython code in a somewhat _ad hoc_ fashion. They might logically be part of the thread state, the interpreter state or the runtime state, for which CPython contains defined structures; but these variables are often defined outside these structures.

CPython serialises access to its static variables using a single Global Interpreter Lock (GIL). In order to reduce dependency on a single GIL, for example to improve support for multiple subinterpreters working with the main Python interpreter, statics need to be tidied up so that concurrency management can be made easier. For example, if all interpreter-related statics were moved to an interpreter-state structure, there could be separate such structure instances per sub-interpreter, each protected by a separate lock, and this would help to improve Python's concurrency support in multi-core environments (which are pretty much the norm these days).

# Approach

The approach used in this repository is to use the ``clang`` compiler to parse CPython code into an AST, and to walk that AST to look for usage of static variables. By "static", we mean those either explicitly defined as ``static``, or those implicitly defined as ``static`` by having no explicit storage class and defined outside a function.

As a first step, analysis has been done on Linux (Ubuntu). The following steps would be needed to repeat this analysis:

1. Clone the CPython repository, if you haven't already.
2. Clone this repository.
3. Create a virtual environment using a Python3 interpreter and activate it.
4. Ensure that ``libclang`` is installed on your system. I did this by running ``sudo apt install libclang-6.0-dev``.
5. Ensure that you have SQLite 3 installed. I did this by running ``sudo apt install sqlite3``.
6. Run ``pip install clang`` to install the Python bindings for ``libclang`` into the virtual environment.
7. We now need to establish which CPython files to process with ``clang``, and which include directories and preprocessor definitions we need to apply for each such file. To do this, we run, in your clone of the Python repository, ``make 2>&1 > ~/tmp/make.txt``, where you can specify a different filename for the output of the make command. (You may need to run ``./configure`` first to create the Makefile, if it doesn't exist.)
8. In your clone of this repository, with the virtual environment active, run ``python clang_analysis.py -c ~/tmp/make.txt > args.json``, substituting whatever you might have used instead of ``~/tmp/make.txt`` to hold the output of the ``make`` command run earlier. This creates a JSON file ``args.json`` containing the list of CPython source files to process, along with the include directory and preprocessor definitions needed for each.
9. Run ``sqlite3 statics.template.sqlite < statics.template.sqlite.sql``. This creates a template database which we use to hold the statics information.
10. Then run ``python clang_analysis.py``. This will create a SQLite database called ``statics.sqlite`` from the template earlier created, and populate the database with the results of running ``clang`` over the files whose information is in ``args.json``.

You can run ``python clang_analysis.py -h`` to get help on other command-line options available.

# Viewing the results via the Web

You can view the results with any SQLite browser (I used ``sudo apt install sqlite-browser`` to install such a browser). Alternatively, you can use code in this repository to assist viewing the code in a Web browser, using the following steps:

1. With the virtual environment active, do ``pip install bottle``.
2. In your clone of this repository, run ``python webapp.py``.
3. Open a Web browser and point it to ``localhost:5001``. You should see the analysis results in your browser. My version is deployed at ``https://cpython.red-dove.com/``. It was deployed using ``gunicorn`` and ``supervisor``.

