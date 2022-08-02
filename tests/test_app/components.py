import idom
from idom import html
from test_app.models import TodoItem

import django_idom
from django_idom.hooks import use_mutation, use_query


@idom.component
def hello_world():
    return html.h1({"id": "hello-world"}, "Hello World!")


@idom.component
def button():
    count, set_count = idom.hooks.use_state(0)
    return html.div(
        html.button(
            {"id": "counter-inc", "onClick": lambda event: set_count(count + 1)},
            "Click me!",
        ),
        html.p(
            {"id": "counter-num", "data-count": count},
            f"Current count is: {count}",
        ),
    )


@idom.component
def parameterized_component(x, y):
    total = x + y
    return html.h1({"id": "parametrized-component", "data-value": total}, total)


victory = idom.web.module_from_template("react", "victory-bar", fallback="...")
VictoryBar = idom.web.export(victory, "VictoryBar")


@idom.component
def simple_bar_chart():
    return VictoryBar()


@idom.component
def use_websocket():
    ws = django_idom.hooks.use_websocket()
    ws.scope = "..."
    success = bool(ws.scope and ws.close and ws.disconnect and ws.view_id)
    return html.div(
        {"id": "use-websocket", "data-success": success},
        html.hr(),
        f"use_websocket: {ws}",
        html.hr(),
    )


@idom.component
def use_scope():
    scope = django_idom.hooks.use_scope()
    success = len(scope) >= 10 and scope["type"] == "websocket"
    return html.div(
        {"id": "use-scope", "data-success": success},
        f"use_scope: {scope}",
        html.hr(),
    )


@idom.component
def use_location():
    location = django_idom.hooks.use_location()
    success = bool(location)
    return html.div(
        {"id": "use-location", "data-success": success},
        f"use_location: {location}",
        html.hr(),
    )


@idom.component
def django_css():
    return html.div(
        {"id": "django-css"},
        django_idom.components.django_css("django-css-test.css"),
        html.div({"style": {"display": "inline"}}, "django_css: "),
        html.button("This text should be blue."),
        html.hr(),
    )


@idom.component
def django_js():
    success = False
    return html._(
        html.div(
            {"id": "django-js", "data-success": success},
            f"django_js: {success}",
            django_idom.components.django_js("django-js-test.js"),
        ),
        html.hr(),
    )


@idom.component
@django_idom.decorators.auth_required(
    fallback=html.div(
        {"id": "unauthorized-user-fallback"},
        "unauthorized_user: Success",
        html.hr(),
    )
)
def unauthorized_user():
    return html.div(
        {"id": "unauthorized-user"},
        "unauthorized_user: Fail",
        html.hr(),
    )


@idom.component
@django_idom.decorators.auth_required(
    auth_attribute="is_anonymous",
    fallback=html.div(
        {"id": "authorized-user-fallback"},
        "authorized_user: Fail",
        html.hr(),
    ),
)
def authorized_user():
    return html.div(
        {"id": "authorized-user"},
        "authorized_user: Success",
        html.hr(),
    )


def get_items():
    return TodoItem.objects.all().order_by("done")


def add_item(text: str):
    existing = TodoItem.objects.filter(text=text).first()
    if existing:
        if existing.done:
            existing.done = False
            existing.save()
        else:
            return False
    else:
        TodoItem(text=text, done=False).save()


def toggle_item(item: TodoItem):
    item.done = not item.done
    item.save()


@idom.component
def todo_list():
    get_item_query = use_query(get_items)
    add_item_mutation = use_mutation(add_item, refetch=get_items)
    toggle_item_mutation = use_mutation(toggle_item, refetch=get_items)

    if get_item_query.data is None:
        rendered_items = html.h2("Loading...")
    elif get_item_query.error:
        rendered_items = html.h2(f"Error when loading - {get_item_query.error}")
    else:
        rendered_items = html.ul(
            [
                html.li(
                    {"id": f"todo-item-{item.text}"},
                    item.text,
                    html.input(
                        {
                            "id": f"todo-item-{item.text}-checkbox",
                            "type": "checkbox",
                            "defaultChecked": item.done,
                            "onChange": lambda event: toggle_item_mutation.execute(item),
                        }
                    ),
                    key=item.text,
                )
                for item in reversed(get_item_query.data)
            ]
        )

    if add_item_mutation.loading:
        mutation_status = html.h2("Adding...")
    elif add_item_mutation.error:
        mutation_status = html.h2(f"Error when adding - {add_item_mutation.error}")
    else:
        mutation_status = ""

    def submit_event(event):
        if event["key"] == "Enter":
            add_item_mutation.execute(text=event["target"]["value"])

    return html.div(
        html.label("Add an item:"),
        html.input({"type": "text", "id": "todo-input", "onKeyDown": submit_event}),
        mutation_status,
        rendered_items,
    )
