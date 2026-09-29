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

sync sqlalchemy vs async sqlchmey
 
 sync sqlalchemy  - lazy loadin is just works
    when we have post object and you access post.author so sqlalchmey automatically runs a query internally to load that author coz of the realtion and without any issue that called lazy loadin
 async sqlchmey -> dont support lazy loading. if we try to do the same without expicitly loaded then it will not work 
     -> sol -> eager loadin that -> selectandload


# lecture 8
create a routes folder
and move all the route based users,posts
  
 # lecture 9
 frontend

 # lecture 10
 authenication
 - packages
    pwdlib[argon2]/byscrypt -> hash
    pyjwt - creating and verifying jwt
    pydantic-settings /python.env 