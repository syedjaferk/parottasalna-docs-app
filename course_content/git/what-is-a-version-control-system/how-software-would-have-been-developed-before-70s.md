# How Software would have been developed before '70s?

#### Problem description

Consider we are in the time period before the 70s. Let's start with how people would have developed software before the 70s collaboration without any **version control system**.

Let's define some process flows,

#### &#x20;

#### Process Flow 1


```{figure} /_assets/image-1.png
:alt: Process 1 - Developer adding feature and sharing it with admin for merging

Process 1 - Developer adding feature and sharing it with admin for merging
```


Process 1 - Developer adding feature and sharing it with admin for merging

In this flow, there will be a master copy of the project with a dedicated person '**admin**', who takes care of the repository (master copy). So whenever there is a new request for a feature,

1. A developer will take a copy of the code from the **master copy** and then they will add some features.
2. The developer will create a **tarball** or a zip file with the **changelog** file, which contains the details of files that are been touched/changed while adding this new functionality.
3. Then the admin will verify the changes and merge the code to the master copy - this will be tiresome work. So the next time, when a feature request is coming, developers can take the code again from main -> add features -> tarball -> merge with master. This cycle will run.

The above process may feel simple, but what if many developers are working parallelly, whether they need to wait for the other developer to complete their work?

Let's see the other process flow,

#### &#x20;

#### Process Flow 2


![](/_assets/image-2.png)


Multiple developers locking file for adding features

In process 2, consider they have established some network kind of stuff so that each developer can log in to the host with their user ID and can access the files.

In the above situation, when developer 1 Is using a particular file, then the file will be locked and other developers won't be able to access the file.

So other developers have to wait till developer 1 finishes his work.

So far we have seen what could be the process . Now lets us investigate from the people of 70's

#### &#x20;

#### Let's hear from people in 70's

1. [https://qr.ae/prvymC](https://qr.ae/prvymC)


![](/_assets/image-3.png)


William says that it is difficult for **merging the files**, and files were shared in **tarballs or zip**

2\. [https://qr.ae/prvYFb](https://qr.ae/prvYFb)


![](/_assets/image-4.png)




Sam says, only a single person is been allocated to merge new changes and they usually take backups and file comparisons before merging files.

3\. [https://qr.ae/prvYO2](https://qr.ae/prvYO2)


![](/_assets/image-5.png)


Jeff says the loss of files is common/normal. They usually take a backup on a daily basis.

These are some of the reviews that I got from Quora. Now we have some expectations about the tool that we wanted. Let's pen it down.
