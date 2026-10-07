# Entity

A definable thing - such as a person, object, concept or event, that can have data stored about it. Think of entities as nouns. Examples: a customer, student, car or product.&#x20;

Organisation require information in order to carry out tasks and activities for which they are responsible. The information that these organisations need could be categorized in a number of ways, for example,&#x20;

An entity may represent a category of people, things, events, locations or concepts within the area under consideration. An entity instance is a specific example of an entity. For example, Syed Jafer is an entity instance of an student entity.

Denoted with Rectangle.&#x20;


![](/_assets/image-5.png)


### **Entity Type**

A group of definable things, such as **students**. Examples include:

* **Student**: A generic type representing all students.
* **Course**: Represents all courses offered by the university.
* **Department**: Represents academic departments.

**Specific Entities**

* A specific student, e.g., _John Doe, Student\_ID: 12345_.
* A specific course, e.g., _Calculus I, Course\_ID: MATH101_.
* A specific department, e.g., _Mathematics Department_.

### **Entity Set**

Represents an entity type at a specific point in time. Examples include:

* **Students enrolled in "Fall 2024" semester**: This subset might include _John Doe, Jane Smith, and Alice Brown_.
* **Courses offered in "Spring 2025"**: Includes _MATH101, ENG202, and CS301_.
* **Departments active as of "2024"**: Includes _Mathematics, Physics, and Computer Science_.

**Related Instances**

* Instance of **Student**: _John Doe, enrolled in Spring 2024_.
* Instance of **Course**: _MATH101, offered by the Mathematics Department_.

### **Entity Categories**

> 🥁 For now, dont think about primary key, foreign key or something.&#x20;

**Strong Entity**

* **Student**: A strong entity because it can be uniquely identified using its own attributes like _Student\_ID_.
* Example attributes:
  * Student\_ID (Primary Key)
  * Name
  * Date\_of\_Birth


![](/_assets/image-6.png)


**Weak Entity**

* **Dependent**: A weak entity related to a student, such as a family member. It depends on the Student entity for identification. Even though it has a unique ID, Conceptually its dependant on student.&#x20;
* Example: _Dependent\_ID_ is meaningful only when associated with a specific Student\_ID.


![](/_assets/image-7.png)


**Associative Entity**

* **Enrollment**: An entity that associates Students and Courses.
* Example attributes:
  * Enrollment\_ID (Primary Key)
  * Student\_ID (Foreign Key)
  * Course\_ID (Foreign Key)
  * Semester

**The Associative Entity is there to establish a Many to Many Relationship between Two or More Entities.**&#x20;

For Example, A Student can enroll in many courses. Also a course can be enrolled by many students. But we can't able to manage these details without an additional Entity (Table). This Entity is denoted as Associative Entity.&#x20;


![](/_assets/image-8.png)


Also, Associative Entity, can contain additional values like duration in above example.&#x20;

### What Should an Entity Type Be?

**SHOULD BE:**&#x20;

• An object that will have many instances in the database&#x20;

• An object that will be composed of multiple attributes&#x20;

• An object that we are trying to model&#x20;

**SHOULD NOT BE:**&#x20;

• A user of the database system&#x20;

• An output of the database system (e.g. a report)
