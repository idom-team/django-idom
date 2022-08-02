???+ tip "Looking for more hooks?"

    Check out the [IDOM Core docs](https://idom-docs.herokuapp.com/docs/reference/hooks-api.html?highlight=hooks) on hooks!

## Use Query

The `use_query` hook is used fetch Django ORM queries.

=== "components.py"

    ```python
    from example_project.my_app.models import TodoItem
    from idom import component, html
    from django_idom.hooks import use_query

    def get_items():
        return TodoItem.objects.all()

    @component
    def todo_list():
        item_query = use_query(get_items)

        if item_query.loading:
            rendered_items = html.h2("Loading...")
        elif item_query.error:
            rendered_items = html.h2("Error when loading!")
        else:
            rendered_items = html.ul(html.li(item, key=item) for item in item_query.data)

        return rendered_items
    ```

=== "models.py"

    ```python
    from django.db import models

    class TodoItem(models.Model):
        text = models.CharField(max_length=255)
    ```

??? question "Can I make ORM calls without hooks?"

    Due to Django's ORM design, database queries must be deferred using hooks. Otherwise, you will see a `SynchronousOnlyOperation` exception.

    This may be resolved in a future version of Django with a natively asynchronous ORM.

??? question "What is an "ORM"?"

    A Python **Object Relational Mapper** is an API for your code to access a database.

    See the [Django ORM documentation](https://docs.djangoproject.com/en/dev/topics/db/queries/) for more information.

## Use Mutation

The `use_mutation` hook is used to modify Django ORM objects.

=== "components.py"

    ```python
    from example_project.my_app.models import TodoItem
    from idom import component, html
    from django_idom.hooks import use_mutation

    def add_item(text: str):
        TodoItem(text=text).save()

    @component
    def todo_list():
        item_mutation = use_mutation(add_item)

        if item_mutation.loading:
            mutation_status = html.h2("Adding...")
        elif item_mutation.error:
            mutation_status = html.h2("Error when adding!")
        else:
            mutation_status = ""

        def submit_event(event):
            if event["key"] == "Enter":
                item_mutation.execute(text=event["target"]["value"])

        return html.div(
            html.label("Add an item:"),
            html.input({"type": "text", "onKeyDown": submit_event}),
            mutation_status,
        )
    ```

=== "models.py"

    ```python
    from django.db import models

    class TodoItem(models.Model):
        text = models.CharField(max_length=255)
    ```

??? question "Can `use_mutation` trigger a refetch of `use_query`?"

    Yes, `use_mutation` can queue a refetch of a `use_query` via the `refetch=...` argument.

    The example below is a merge of the `use_query` and `use_mutation` examples above with the addition of a `refetch` argument on `use_mutation`.
    
    Please note that any `use_query` hooks that use `get_items` will be refetched upon a successful mutation.

    ```python title="components.py"
    from example_project.my_app.models import TodoItem
    from idom import component, html
    from django_idom.hooks import use_mutation

    def get_items():
        return TodoItem.objects.all()

    def add_item(text: str):
        TodoItem(text=text).save()

    @component
    def todo_list():
        item_query = use_query(get_items)
        if item_query.loading:
            rendered_items = html.h2("Loading...")
        elif item_query.error:
            rendered_items = html.h2("Error when loading!")
        else:
            rendered_items = html.ul(html.li(item, key=item) for item in item_query.data)

        item_mutation = use_mutation(add_item, refetch=get_items)
        if item_mutation.loading:
            mutation_status = html.h2("Adding...")
        elif item_mutation.error:
            mutation_status = html.h2("Error when adding!")
        else:
            mutation_status = ""

        def submit_event(event):
            if event["key"] == "Enter":
                item_mutation.execute(text=event["target"]["value"])

        return html.div(
            html.label("Add an item:"),
            html.input({"type": "text", "onKeyDown": submit_event}),
            mutation_status,
            rendered_items,
        )
    ```

??? question "Can I make ORM calls without hooks?"

    Due to Django's ORM design, database queries must be deferred using hooks. Otherwise, you will see a `SynchronousOnlyOperation` exception.

    This may be resolved in a future version of Django with a natively asynchronous ORM.

    However, even when resolved it is best practice to perform ORM queries within the `use_query` in order to handle `loading` and `error` states.

??? question "What is an "ORM"?"

    A Python **Object Relational Mapper** is an API for your code to access a database.

    See the [Django ORM documentation](https://docs.djangoproject.com/en/dev/topics/db/queries/) for more information.

## Use Websocket

You can fetch the Django Channels websocket at any time by using `use_websocket`.

```python title="components.py"
from idom import component, html
from django_idom.hooks import use_websocket

@component
def my_component():
    my_websocket = use_websocket()
    return html.div(my_websocket)
```

## Use Scope

This is a shortcut that returns the Websocket's `scope`.

```python title="components.py"
from idom import component, html
from django_idom.hooks import use_scope

@component
def my_component():
    my_scope = use_scope()
    return html.div(my_scope)
```

## Use Location

??? info "This hook's behavior will be changed in a future update"

    This hook will be updated to return the browser's current URL. This change will come in alongside IDOM URL routing support.

    Check out [idom-team/idom#569](https://github.com/idom-team/idom/issues/569) for more information.

This is a shortcut that returns the Websocket's `path`.

```python title="components.py"
from idom import component, html
from django_idom.hooks import use_location

@component
def my_component():
    my_location = use_location()
    return html.div(my_location)
```
