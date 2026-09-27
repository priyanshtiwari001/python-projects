### Lecture 2

Topics we covers:

Request parameter
jinja2 templats
template inheritance -> allows us to create a parent template with a common strcuture
how to mount static files
how to append in the html



### Lecture 3

path parameter and type hints
httpexception
exceptions
responses -> jsonresponse
starlettle -> httpexpection
validation error
internally if we hit an api where it doesn't exist it is starlettle which throw the error
fastapi is build on top of starlettle


have post.html
error.html
status code
message

pending erro:
http://localhost:8000/post/hello -> handle validationError -> RequestValidationError
http://localhost:8000/post/99 -> handle expection -> StarlettleExpection



# lecture 6

update- put,patch

model_dump()??

excule_unset -> it gave what client give 
if it is false and let say client give only title then it make other field as a None-default

setattr

delete,patch -  user
cancade-all,delete-orphan



# lecture 7


lazy loading dont work
what is lazy loading

lifespan is the modern way to in fastapi to handle startup and shutdown. it replace the older deprecarted onstartup and onshutdown decorators while used in previous version