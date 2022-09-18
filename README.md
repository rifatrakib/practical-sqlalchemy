# Practical SQLAlchemy

The repository will present the concepts of the `SQLAlchemy Core API` and the `SQLAlchemy ORM API` in the natural order that they should be learned, first with a mostly-Core-centric approach and then spanning out into more ORM-centric concepts. One can browse through the commit history to check how to go about this step-by-step. The major sections of this tutorial are as follows:

* __Establishing Connectivity - the Engine__ - all SQLAlchemy applications start with an `Engine` object.

* __Working with Transactions and the DBAPI__ - the usage API of the `Engine` and its related objects `Connection` and `Result`. This content is Core-centric however ORM users will want to be familiar with at least the `Result` object.

* __Working with Database Metadata__ - SQLAlchemy's SQL abstractions as well as the ORM rely upon a system of defining database schema constructs as Python objects. This section introduces how to do that from both a Core and an ORM perspective.

* __Working with Data__ - here we learn how to create, select, update and delete data in the database. The so-called `CRUD operations` here are given in terms of SQLAlchemy Core with links out towards their ORM counterparts. The SELECT operation that is introduced in detail at `Selecting Rows with Core or ORM` applies equally well to Core and ORM.

* __Data Manipulation with the ORM__ - covers the persistence framework of the ORM; basically the ORM-centric ways to insert, update and delete, as well as how to handle transactions.

* __Working with Related Objects__ - introduces the concept of the `relationship` construct and provides a brief overview of how it’s used, with links to deeper documentation.

* __Further Reading__ - lists a series of major top-level documentation sections which fully document the concepts introduced in this tutorial.
