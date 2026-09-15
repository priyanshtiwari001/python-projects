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