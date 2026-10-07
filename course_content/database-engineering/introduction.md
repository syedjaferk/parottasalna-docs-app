# Need of Database

Data comes in all shapes and sizes, and the ways that we deal with it will vary according to the nature of the data. In some cases, the data is simple—perhaps a single number such as the value of π that might be built into a program that draws circles.&#x20;

The application itself may have this as a hard-coded value for the ratio of the circumference of a circle to its diameter. We call this kind of data constant, as it will never need to change.

### Where can we store this details ?

As an initial step, we can go with flat files. A **flat file** is a simple text file that stores data in rows and columns, often separated by commas or tabs. It's like an Excel sheet or a CSV file where all information is laid out in a single table. There’s no inherent structure for relationships or links between data.

For example, consider Tamil movies.&#x20;

```
Karnan Dhanush MariSelvaraj 2021 Drama 70Crore 100Crore Tamil BestActor
SooraraiPottru Suriya SudhaKongara 2020 Biopic 50Crore 200Crore Tamil NationalAward
Vikram KamalHaasan LokeshKanagaraj 2022 Action 150Crore 400Crore Tamil BestFilm
```

The complexity of the above file will increase, if i am adding more actor details into the file, like this,&#x20;

```
Karnan Dhanush Natrajan Yogi babu MariSelvaraj 2021 Drama 70Crore 100Crore Tamil BestActor
SooraraiPottru Suriya SudhaKongara 2020 Biopic 50Crore 200Crore Tamil NationalAward
Vikram KamalHaasan Fahad  LokeshKanagaraj 2022 Action 150Crore 400Crore Tamil BestFilm
```

This problem is referred as **Repeating Group.**

### How to resolve Repeating Group ?

The repeating groups problem is very common and is the issue that really started the drive toward more sophisticated database management systems. We can attempt to resolve this problem by using ordinary text files with a little more structure. These are still often referred to as flat files, but they are probably better described as structured text files.

```
[Baasha]
year=1995
director=Suresh Krissna
genre=Action
starring=Rajinikanth
starring=Nagma
starring=Raghuvaran

[Sivaji]
year=2007
director=S. Shankar
genre=Drama, Action
starring=Rajinikanth
starring=Shriya Saran
starring=Vivek

[Nayakan]
year=1987
director=Mani Ratnam
genre=Crime, Drama
starring=Kamal Haasan
starring=Janagaraj
starring=Nassar

[Thalapathi]
year=1991
director=Mani Ratnam
genre=Drama
starring=Rajinikanth
starring=Mammootty
starring=Shobana

[Muthu]
year=1995
director=K. S. Ravikumar
genre=Comedy, Drama
starring=Rajinikanth
starring=Meena
starring=Sarath Babu

```

We have solved the repeating groups problem by introducing some tags to indicate the type of each element in the record.&#x20;

However, now our application must read and interpret a more complex file just to get its data. Updating a record and searching in this kind of structure can be quite difficult. How can we make sure that the descriptions for genre or classification are chosen from a specific subset? How can we easily produce a sorted list of K.S. Ravikumar  directed films?

What we need is a general purpose way of storing and retrieving data, not a solution invented many times to fit slightly different, but very similar, problems as in a generic data handling system. What we need is a database and a database management system.
